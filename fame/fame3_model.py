import logging
import os
from glob import glob
from tempfile import TemporaryDirectory
from typing import List, Tuple

import pandas as pd
from nerdd_module import Problem, SimpleModel
from rdkit.Chem import (
    KekulizeException,
    Mol,
    MolFromSmiles,
    MolToSmiles,
    SanitizeMol,
    SmilesParserParams,
)
from sh import Command

from .resources import get_fame3_executable

__all__ = ["Fame3Model"]

logger = logging.getLogger(__name__)

# Predicts the site of metabolism for a given molecule or a set of molecules.
# mode: one of ['P1', 'P1+P2', 'P2']

# wrap FAME3 binary as a Python function
# r=4: number of processes (note: I suspect that Fame ignores this parameter)
# c=True: output csv
fame3 = Command(get_fame3_executable()).bake(r=4, c=True)


default_columns = [
    "mol_id",
    "atom",
    "atom_id",
    "is_som",
    "ad_score",
    "probability_0",
    "probability_1",
]


def predict_mols(mols: List[Mol], mode="P1+P2"):
    with TemporaryDirectory() as tmp_dir:
        output_dir = os.path.join(tmp_dir, "output")

        # Note 1: For simplicity, we always provide the input for Fame3 in SMILES format (even if
        #         the input was given as a mol block / sdf).
        # Note 2: In order to be consistent with the original implementation, SMILES have to be
        #         kekulized and all hydrogens have to be explicit. This changes the atom indices
        #         and we have to map the results back to the original atom indices (see below).
        input_smiles = [
            MolToSmiles(m, canonical=False, allHsExplicit=True, kekuleSmiles=True)
            for m in mols
        ]

        # execute Fame3 on the list of smiles
        fame3("-s", *input_smiles, o=output_dir, m=mode)

        # Fame3 creates the following result file structure:
        #
        # output_dir
        # ├── individual_results
        # │   ├── mol_1
        # │   │   ├── mol_1_basic.csv
        # │   │   ├── mol_1_circ_level5.csv
        # │   │   ├── mol_1_fing_level10.csv
        # │   │   └── mol_1_soms.html
        # │   ├── mol_2
        # │   │   ├── ...
        # ├── results.html
        # └── results.zip
        #
        # We are only interested in the contents of the _basic.csv files:
        result_files = glob(os.path.join(output_dir, "**/*_basic.csv"), recursive=True)

        if len(result_files) > 0:
            df = pd.concat(
                [
                    pd.read_csv(result_file, index_col=False)
                    for result_file in result_files
                ]
            )
        else:
            return []

        # cleaning the results
        if len(df) > 0:
            df.columns = [c.lower() for c in df.columns]
            df.rename(
                columns={
                    "issom": "is_som",
                    "AD_score": "ad_score",
                    "probability(0)": "probability_0",
                    "probability(1)": "probability_1",
                },
                inplace=True,
            )

            df["atom_id"] = df.atom.map(lambda x: x.split(".")[1]).map(int) - 1
            df["mol_id"] = df["molecule"].map(lambda s: s[len("mol_") :]).map(int) - 1

            # round all numbers to 3 decimal places
            for col in ["probability_0", "probability_1", "ad_score"]:
                df[col] = df[col].round(3)

            # Create the mapping that maps atom indices in the manipulated molecules (given as
            # "input_smiles" to Fame; has hydrogens; is kekulized) to the atom indices in the
            # original molecules (given as "mols" to this method).
            mapping = {}
            for i, mol, input_smi in zip(range(len(mols)), mols, input_smiles):
                # If finding an alignment fails, we keep the original atom indices.
                try:
                    # Copy the molecule to avoid changes in the original molecule (GetSubstructMatch
                    # changes marked atoms inplace).
                    preprocessed_mol = Mol(mol)

                    # Get the manipulated molecule and keep the hydrogens (removeHs=False).
                    params = SmilesParserParams()
                    params.removeHs = False
                    params.sanitize = True
                    fame_mol = MolFromSmiles(input_smi, params)

                    # Use the graph matching algorithm to find the atom mapping. The mapping is a tuple
                    # of atom indices. When index j maps to number k, then atom j in fame_mol is atom k
                    # in the original mol.
                    match = preprocessed_mol.GetSubstructMatch(fame_mol)

                    # Make sure that all heavy atoms are matched.
                    assert len(match) == preprocessed_mol.GetNumAtoms()

                    # The expression mapping[m][i] maps atom i in fame_mol m to the corresponding atom
                    # in the original mol.
                    mapping[i] = match
                except Exception as e:
                    logger.error(e)
                    mapping[i] = list(range(mol.GetNumAtoms()))

            # apply the mapping
            df["atom_id"] = df.apply(
                lambda row: mapping[row["mol_id"]][row["atom_id"]], axis=1
            )
            df["atom"] = df.apply(
                lambda row: f"{row['atom'].split('.')[0]}.{row['atom_id']}", axis=1
            )

            # filter and reorder columns
            df = df[default_columns]
        else:
            df = pd.DataFrame(columns=default_columns)

        # fix types
        df.mol_id = df.mol_id.astype(int)
        df.ad_score = df.ad_score.astype(float)
        df.probability_0 = df.probability_0.astype(float)
        df.probability_1 = df.probability_1.astype(float)

        return df.to_dict(orient="records")


class Fame3Model(SimpleModel):
    def __init__(self):
        super().__init__(preprocessing_steps=[])

    def _preprocess(self, mol: Mol) -> Tuple[Mol, List[Problem]]:
        try:
            SanitizeMol(mol)
            return mol, []
        except KekulizeException:
            return None, [
                Problem("kekulization_error", "Failed kekulizing the molecule.")
            ]

    def _predict_mols(
        self, mols: List[Mol], metabolism_phase: str = "phase_1_and_2"
    ) -> List[dict]:
        assert metabolism_phase in ["phase_1_and_2", "phase_1", "phase_2"]
        if metabolism_phase == "phase_1_and_2":
            metabolism_phase = "P1+P2"
        elif metabolism_phase == "phase_1":
            metabolism_phase = "P1"
        elif metabolism_phase == "phase_2":
            metabolism_phase = "P2"

        # predict the SOMs
        return predict_mols(mols, mode=metabolism_phase)
