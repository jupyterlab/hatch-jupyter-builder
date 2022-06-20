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

args = parser.parse_args()

subprocess.run([sys.executable, "-m", "pip", "install", "build"])


def build_file(dirname):
    orig_dir = os.getcwd()
    os.chdir(dirname)
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    subprocess.run([sys.executable, "-m", "build", f"--{args.dist_name}"])
    os.chdir(orig_dir)


def get_tar_names(dirname):
    dist_file = glob.glob(f"{dirname}/dist/*.tar.gz")[0]
    tarf = tarfile.open(dist_file, "r:gz")
    return set(tarf.getnames())


def get_zip_names(dirname):
    wheel_file = glob.glob(f"{dirname}/dist/*.whl")[0]
    with zipfile.ZipFile(wheel_file, "r") as f:
        return set(f.namelist())


def filter_file(path, root):
    if "egg-info" in path:
        return True
    full_path = os.path.join(path, root)
    if os.path.isdir(full_path):
        return True
    if os.path.basename(path) in [path, "setup.py", "setup.cfg", "MANIFEST.in"]:
        return True
    return False


build_file(args.source_dir)
build_file(args.target_dir)

if args.dist_name == "sdist":
    source_names = get_tar_names(args.source_dir)
    target_names = get_tar_names(args.target_dir)
else:
    source_names = get_zip_names(args.source_dir)
    target_names = get_zip_names(args.target_dir)

removed = source_names - target_names
removed = [r for r in removed if not filter_file(r, args.source_dir)]
if removed:
    print("\nRemoved_files:")
    [print(f) for f in removed]

added = target_names - source_names
added = [a for a in added if not filter_file(a, args.target_dir)]
if added:
    print("\nAdded files:")
    [print(f) for f in added]

print()

if added or removed:
    sys.exit(1)
