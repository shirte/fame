import logging
import os
from glob import glob
from tempfile import TemporaryDirectory
from typing import List, Tuple

import pandas as pd
from nerdd_module import Problem, SimpleModel
from rdkit.Chem import KekulizeException, Mol, SanitizeMol, SDWriter
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


def predict_mols(mols: List[Mol], mode="P1+P2") -> List[dict]:
    with TemporaryDirectory() as tmp_dir:
        output_dir = os.path.join(tmp_dir, "output")

        # For simplicity, we always provide the input for Fame3 in SDF format (even if the input
        # was given as SMILES).
        input_sdf = os.path.join(tmp_dir, "input.sdf")
        writer = SDWriter(input_sdf)
        try:
            for i, mol in enumerate(mols):
                # We need to assign proper names to the molecules, otherwise Fame3 will fail.
                # Also, we can later use the names to map the results back to the input molecules.
                copy = Mol(mol)
                copy.SetProp("_Name", f"mol_{i}")

                writer.write(copy)
        finally:
            writer.close()

        # execute Fame3 on the list of smiles
        fame3(input_sdf, o=output_dir, m=mode)

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
