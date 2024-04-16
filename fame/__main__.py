from nerdd_module import auto_cli

from .fame3_model import Fame3Model


@auto_cli
def main():
    return Fame3Model()
