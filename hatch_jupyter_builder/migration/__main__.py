"""Migrate a Jupyter project from setuptools/jupyter-packaging to hatch and
hatch_jupyter_builder."""
import argparse
import os
import subprocess
import venv
from pathlib import Path
from tempfile import TemporaryDirectory

parser = argparse.ArgumentParser()
parser.add_argument(dest="target_dir", help="Target Directory")

# Parse and print the results
args = parser.parse_args()

with TemporaryDirectory() as td:
    venv.create(td, with_pip=True)
    if os.name == "nt":
        python = Path(td) / "Scripts/python.exe"
    else:
        python = Path(td) / "bin/python"

    print("Installing in temporary virtual environment...")

    # Create a virtual environment and use it to run the migration.
    subprocess.run([python, "-m", "pip", "install", "-v", "-e", args.target_dir])
    subprocess.run([python, "-m", "pip", "install", "jupyter_packaging"])
    subprocess.run([python, "-m", "pip", "install", "tomli_w"])
    subprocess.run([python, "-m", "pip", "install", "tomli"])
    subprocess.run([python, "-m", "pip", "install", "hatch"])

    migrator = Path(__file__).parent / "migrate_core.py"
    subprocess.run([python, migrator], cwd=args.target_dir)
