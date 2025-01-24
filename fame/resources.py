import os
import shutil
from glob import glob

from platformdirs import user_data_dir

__all__ = ["get_fame3_executable"]

here = os.path.dirname(__file__)


def merge_file(filename, output):
    parts = sorted(glob(f"{filename}.part*"))

    with open(output, "wb") as f:
        for part in parts:
            with open(part, "rb") as p:
                f.write(p.read())


def setup_file(filename, sub_dir=None):
    # install fame3 in the user data directory if necessary
    fame3_dir = user_data_dir("fame3")
    if sub_dir:
        fame3_dir = os.path.join(fame3_dir, sub_dir)
    os.makedirs(fame3_dir, exist_ok=True)
    target_filename = os.path.join(fame3_dir, os.path.basename(filename))

    if os.path.exists(filename):
        if not os.path.exists(target_filename):
            shutil.copy(filename, fame3_dir)
    elif os.path.exists(f"{filename}.part000"):
        if not os.path.exists(target_filename):
            merge_file(filename, target_filename)

    return target_filename


def get_fame3_executable():
    # copy the fame3 executable to the user data directory
    fame3_jar_name = os.path.join(here, "fame3-server-0.0.0.dev7_server9.jar")

    lib_files = glob(os.path.join(here, "libs", "*"))
    for lib_file in lib_files:
        setup_file(lib_file, "libs")

    return setup_file(fame3_jar_name)
