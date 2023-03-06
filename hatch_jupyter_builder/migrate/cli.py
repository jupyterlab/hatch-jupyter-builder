"""Migrate a Jupyter project from setuptools/jupyter-packaging to hatch and
hatch_jupyter_builder."""
import argparse
import logging
import os
import subprocess
import sys
import venv
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

from hatch_jupyter_builder import __version__ as builder_version


def main(td: str, target_dir: str) -> None:
    """Main script."""
    logger = logging.getLogger(__name__)
    logging.basicConfig()
    venv.create(td, with_pip=True)
    python = Path(td) / "Scripts/python.exe" if os.name == "nt" else Path(td) / "bin/python"

    logger.info("Installing in temporary virtual environment...")

    # Create a virtual environment and use it to run the migration.
    runner = subprocess.check_call
    runner([python, "-m", "pip", "install", "build"])
    runner([python, "-m", "pip", "install", "packaging"])
    runner([python, "-m", "pip", "install", "tomli_w"])
    runner([python, "-m", "pip", "install", "tomli;python_version<'3.11'"])
    runner([python, "-m", "pip", "install", "hatch"])
    runner([python, "-m", "build", target_dir, "--sdist"])

    migrator = Path(__file__).parent / "_migrate.py"
    runner([python, migrator, builder_version], cwd=target_dir)


def make_parser(
    parser: Optional[argparse.ArgumentParser] = None, prog: Optional[str] = None
) -> argparse.ArgumentParser:
    """Make a parser object."""
    if parser is None:
        parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument(dest="target_dir", help="Target Directory")
    return parser


def run(args: Optional[argparse.Namespace] = None) -> None:
    """Run the migration."""
    if args is None:
        parser = make_parser(prog=f"{sys.executable} -m hatch_jupyter_builder.migrate")
        args = parser.parse_args()
    with TemporaryDirectory() as td:
        main(td, args.target_dir)
