"""Compare the dist file created by a migrated package to one created by the original."""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument(dest="source_dir", help="Source Directory")
parser.add_argument(dest="target_dir", help="Target Directory")
parser.add_argument(dest="dist_name", help="Dist name")


def build_file(dirname, dist_name):
    orig_dir = os.getcwd()
    os.chdir(dirname)
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    subprocess.check_call([sys.executable, "-m", "build", f"--{dist_name}"])
    os.chdir(orig_dir)


def get_tar_names(dirname):
    dist_file = glob.glob(f"{dirname}/dist/*.tar.gz")[0]
    tarf = tarfile.open(dist_file, "r:gz")
    return set(tarf.getnames())


def get_zip_names(dirname):
    wheel_file = glob.glob(f"{dirname}/dist/*.whl")[0]
    with zipfile.ZipFile(wheel_file, "r") as f:
        return set(f.namelist())


def filter_file(path):
    if "egg-info" in path:
        return True
    _, ext = os.path.splitext(path)
    if not ext:
        return True
    if os.path.basename(path) in [path, "setup.py", "setup.cfg", "MANIFEST.in"]:
        return True
    return False


def main(source_dir, target_dir, dist_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "build"])

    build_file(source_dir, dist_name)
    build_file(target_dir, dist_name)

    if dist_name == "sdist":
        source_names = get_tar_names(source_dir)
        target_names = get_tar_names(target_dir)
    else:
        source_names = get_zip_names(source_dir)
        target_names = get_zip_names(target_dir)

    removed = source_names - target_names
    removed = [r for r in removed if not filter_file(r)]
    if removed:
        print("\nRemoved_files:")
        [print(f) for f in removed]

    added = target_names - source_names
    added = [a for a in added if not filter_file(a)]
    if added:
        print("\nAdded files:")
        [print(f) for f in added]

    print()

    return dict(added=added, removed=removed)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.source_dir, args.target_dir, args.dist_name)
