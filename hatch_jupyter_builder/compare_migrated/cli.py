"""Compare the dist file created by a migrated package to one created by the original."""
from __future__ import annotations

import argparse
import glob
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


def build_file(dirname: str, dist_name: str) -> None:
    """Build a dist file in a directory."""
    orig_dir = Path.cwd()
    os.chdir(dirname)
    if Path("dist").exists():
        shutil.rmtree("dist")
    subprocess.check_call([sys.executable, "-m", "build", f"--{dist_name}"])
    os.chdir(orig_dir)


def get_tar_names(dirname: str) -> set[str]:
    """Get the tarball names in a directory."""
    dist_file = glob.glob(f"{dirname}/dist/*.tar.gz")[0]  # noqa: PTH207
    tarf = tarfile.open(dist_file, "r:gz")
    return set(tarf.getnames())


def get_zip_names(dirname: str) -> set[str]:
    """Get the zip (wheel) file names in a directory."""
    wheel_file = glob.glob(f"{dirname}/dist/*.whl")[0]  # noqa: PTH207
    with zipfile.ZipFile(wheel_file, "r") as f:
        return set(f.namelist())


def filter_file(path: str) -> bool:
    """Filter a file path for interesting files."""
    if "egg-info" in path:
        return True
    path_obj = Path(path)
    ext = path_obj.suffix
    if not ext:
        return True
    if path_obj.name in [path, "setup.py", "setup.cfg", "MANIFEST.in"]:
        return True
    return False


def main(source_dir: str, target_dir: str, dist_name: str) -> dict[str, list[str]]:
    """The main script."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "build"])

    logger = logging.getLogger(__name__)
    logging.basicConfig()

    build_file(source_dir, dist_name)
    build_file(target_dir, dist_name)

    if dist_name == "sdist":
        source_names = get_tar_names(source_dir)
        target_names = get_tar_names(target_dir)
    else:
        source_names = get_zip_names(source_dir)
        target_names = get_zip_names(target_dir)

    removed = list(source_names - target_names)
    removed = [r for r in removed if not filter_file(r)]
    if removed:
        logger.info("\nRemoved_files:")
        [logger.info(f) for f in removed]  # type:ignore[func-returns-value]

    added = list(target_names - source_names)
    added = [a for a in added if not filter_file(a)]
    if added:
        logger.info("\nAdded files:")
        [logger.info(f) for f in added]  # type:ignore[func-returns-value]

    logger.info("")

    return {"added": added, "removed": removed}


def make_parser(
    parser: argparse.ArgumentParser | None = None, prog: str | None = None
) -> argparse.ArgumentParser:
    """Make an arg parser."""
    if parser is None:
        parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument(dest="source_dir", help="Source Directory")
    parser.add_argument(dest="target_dir", help="Target Directory")
    parser.add_argument(dest="dist_name", help="Dist name")
    return parser


def run(args: argparse.Namespace | None = None) -> None:
    """Run the cli."""
    if args is None:
        parser = make_parser(prog=f"{sys.executable} -m hatch_jupyter_builder.compare_migrated")
        args = parser.parse_args()
    main(args.source_dir, args.target_dir, args.dist_name)
