import os
from glob import glob
from tempfile import TemporaryDirectory
from typing import List

import pandas as pd
from nerdd_module import AbstractModel
from nerdd_module.problem import Problem
from rdkit.Chem import AddHs, Mol, MolToSmiles, SanitizeMol
from sh import Command

from .resources import get_fame3_executable

__all__ = ["Fame3Model"]

# Predicts the site of metabolism for a given molecule or a set of molecules.
# mode: one of ['P1', 'P1+P2', 'P2']

# wrap FAME3 binary as a Python function
# r=4: number of processes
# c=True: output csv
fame3 = Command(get_fame3_executable()).bake(r=1, c=True)


default_columns = [
    "mol_id",
    "atom_id",
    "atom",
    "is_som",
    "probability_0",
    "probability_1",
    "ad_score",
]


def predict_mols(mols: List[Mol], mode="P1+P2"):
    with TemporaryDirectory() as tmp_dir:
        output_dir = os.path.join(tmp_dir, "output")

        # We use the smiles format as input for Fame3.
        # In order to be consistent with the original implementation, SMILES have to be 
        # kekulized and all hydrogens have to be explicit.
        input_smiles = [MolToSmiles(m, canonical=False, allHsExplicit=True, kekuleSmiles=True) for m in mols]

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
            df = pd.DataFrame(columns=default_columns)

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

            # fame uses new mol ids, but we want to use the original mol ids
            original_mol_ids = [int(m.GetProp("_Name")) for m in mols]
            mapping = dict(zip(range(len(original_mol_ids)), original_mol_ids))
            df["mol_id"] = df["mol_id"].map(mapping)

            # round all numbers to 3 decimal places
            for col in ["probability_0", "probability_1", "ad_score"]:
                df[col] = df[col].round(3)

            # filter and reorder columns
            df = df[default_columns]
        else:
            df = pd.DataFrame(columns=default_columns)

        # fix types
        df.mol_id = df.mol_id.astype(int)
        df.ad_score = df.ad_score.astype(float)
        df.probability_0 = df.probability_0.astype(float)
        df.probability_1 = df.probability_1.astype(float)

        return df


class Fame3Model(AbstractModel):
    def __init__(self):
        super().__init__(preprocessing_pipeline="custom")

    def _preprocess_single_mol(self, mol: Mol):
        SanitizeMol(mol)
        mol = AddHs(mol, explicitOnly=True)
        return mol, []

    def _predict_mols(
        self, mols: List[Mol], metabolism_phase="phase_1_and_2"
    ) -> pd.DataFrame:
        assert metabolism_phase in ["phase_1_and_2", "phase_1", "phase_2"]
        if metabolism_phase == "phase_1_and_2":
            metabolism_phase = "P1+P2"
        elif metabolism_phase == "phase_1":
            metabolism_phase = "P1"
        elif metabolism_phase == "phase_2":
            metabolism_phase = "P2"

        # predict the SOMs
        return predict_mols(mols, mode=metabolism_phase)
