"""Handle migration."""
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import tomli_w  # type:ignore[import-not-found]
from packaging import version

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

logger = logging.getLogger(__name__)
logging.basicConfig()

# Handle the version.
# If it is a dev version, use the previous minor version.
builder_version = version.parse(sys.argv[1])
if builder_version.is_devrelease:
    assert isinstance(builder_version, version.Version)
    builder_version_str = f">={builder_version.major}.{builder_version.minor - 1}.0"
else:
    builder_version_str = f">={builder_version}"
if "BUILDER_VERSION_SPEC" in os.environ:
    builder_version_str = os.environ["BUILDER_VERSION_SPEC"]

logger.info("\n\nStarting pyproject.toml migration")

warnings = []

# Read pyproject before migration to get old build requirements.
pyproject = Path("pyproject.toml")
if pyproject.exists():
    data = tomllib.loads(pyproject.read_text("utf-8"))
    requires = data["build-system"]["requires"]
    # Install the old build reqs into this venv.
    subprocess.run([sys.executable, "-m", "pip", "install", *requires], check=False)
    requires = [
        r
        for r in requires
        if not r.startswith("jupyter-packaging")
        and not r.startswith("setuptools")
        and not r.startswith("jupyter_packaging")
        and not r.startswith("wheel")
    ]
else:
    requires = []


# Extract the current version before beginning any migration.
setup_py = Path("setup.py")
if setup_py.exists():
    current_version = (
        subprocess.check_output([sys.executable, str(setup_py), "--version"])
        .decode("utf-8")
        .strip()
    )
else:
    warnings.append("Fill in '[project][version]' in 'pyproject.toml'")
    current_version = "!!UNKNOWN!!"

# Run the hatch migration script.
logger.info("Running hatch migration")
subprocess.run([sys.executable, "-m", "hatch", "new", "--init"], check=False)

# Run the jupyter-packaging migration script - must be done after
# hatch migration to avoid conflicts.
logger.info("Running jupyter-packaging migration")
here = Path(__file__).parent.resolve()
prev_pythonpath = os.environ.get("PYTHONPATH", "")
if prev_pythonpath:
    os.environ["PYTHONPATH"] = f"{here}{os.pathsep}{prev_pythonpath}"
else:
    os.environ["PYTHONPATH"] = str(here)
subprocess.run([sys.executable, "setup.py", "--version"], capture_output=True, check=False)
os.environ["PYTHONPATH"] = prev_pythonpath

# Handle setup.cfg
# Move flake8 config to separate file, preserving comments.
# Add .flake8 file to git.
setup_cfg = Path("setup.cfg")
flake8_path = Path(".flake8")
flake8 = ["[flake8]"]
if setup_cfg.exists():
    lines = setup_cfg.read_text("utf-8").splitlines()
    matches = False
    for line in lines:
        if line.strip() == "[flake8]":
            matches = True
            continue

        if not matches:
            continue

        if line.startswith("["):
            break

        flake8.append(line)

    if matches:
        flake8_path.write_text("\n".join(flake8) + "\n", "utf-8")
        subprocess.run(["git", "add", str(flake8_path)], check=False)


# Migrate and remove unused config.
# Read in the project.toml after auto migration.
logger.info("Migrating static data")
data = tomllib.loads(pyproject.read_text("utf-8"))
tool_table = data.setdefault("tool", {})

# Handle license file.
for lic_name in ["LICENSE", "COPYING.md", "LICENSE.txt"]:
    for fname in os.listdir("."):
        if fname.lower() == lic_name.lower():
            data["project"]["license"] = {"file": fname}

# Add the other build requirements.
data["build-system"]["requires"].extend(requires)

# Remove old check-manifest config.
if "check-manifest" in tool_table:
    del tool_table["check-manifest"]

# Build up the hatch config.
hatch_table = tool_table.setdefault("hatch", {})
build_table = hatch_table.setdefault("build", {})
targets_table = build_table.setdefault("targets", {})

# Remove the dynamic version.
if current_version and "version" in hatch_table:
    del hatch_table["version"]

# Remove any auto-generated sdist config.
if "sdist" in targets_table:
    del targets_table["sdist"]

# Exclude the .github folder by default.
targets_table["sdist"] = {"exclude": [".github"]}

hooks_table = build_table.setdefault("hooks", {})
builder_table = hooks_table.setdefault("jupyter-builder", {})
builder_table["dependencies"] = [f"hatch-jupyter-builder{builder_version_str}"]
builder_table["build-function"] = "hatch_jupyter_builder.npm_builder"

# Migrate the jupyter-packaging static data.
if "jupyter-packaging" in tool_table:
    packaging_table = tool_table.get("jupyter-packaging", {})
    del tool_table["jupyter-packaging"]

    options_table = packaging_table.setdefault("options", {})
    build_args_table = packaging_table.setdefault("build-args", {})

    for option in ["ensured-targets", "skip-if-exists"]:
        if option in options_table:
            builder_table[option] = options_table[option]

    if build_args_table:
        builder_table["build-kwargs"] = build_args_table.copy()

    if build_args_table.get("npm") and "editable-build-kwargs" in builder_table:
        builder_table["editable-build-kwargs"]["npm"] = build_args_table["npm"]

# Add artifacts config for package data that would be ignored.
project_name = data.get("project", {}).get("name", "")
gitignore = Path(".gitignore")
artifacts = []
if gitignore.exists() and project_name and Path(project_name).exists():
    text = gitignore.read_text("utf-8")
    for line in text.splitlines():
        if line.startswith(project_name):
            artifacts.append(f"{line}")
if artifacts:
    build_table["artifacts"] = artifacts


# Handle setup.py - pre-commit config.
if setup_py.exists():
    text = setup_py.read_text("utf-8")
    if "pre-commit" in text:
        builder_table["install-pre-commit"] = True

# Handle versioning with tbump - allows for static versioning and makes
# it easier to use jupyter_releaser.
data["project"]["version"] = current_version
data["project"].pop("dynamic", None)

tbump_table = tool_table.setdefault("tbump", {})
tbump_table["version"] = {
    "current": current_version,
    "regex": r"""
      (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)((?P<channel>a|b|rc|.dev)(?P<release>\d+))?
    """.strip(),
}
tbump_table["git"] = {
    "message_template": r"Bump to {new_version}",
    "tag_template": r"v{new_version}",
}
tbump_table["field"] = [{"name": "channel", "default": ""}, {"name": "release", "default": ""}]
tbump_table["file"] = [
    {
        "src": "pyproject.toml",
        "version_template": 'version = "{major}.{minor}.{patch}{channel}{release}"',
    }
]

# Add entry for _version.py if it exists.
version_py = Path(project_name) / "_version.py"
if version_py.exists():
    tbump_table["file"].append({"src": str(version_py)})
    text = version_py.read_text(encoding="utf-8")
    if current_version not in text:
        warnings.append(
            f'Add the static version string "{current_version}" to "{version_py}" instead of dynamic version handling'
        )

# Add entry for package.json if it exists and has the same version.
package_json = Path("package.json")
if package_json.exists():
    text = package_json.read_text(encoding="utf-8")
    npm_version = json.loads(text)["version"]
    if npm_version == current_version:
        tbump_table["file"].append(
            {
                "src": "package.json",
                "version_template": '"version": "{major}.{minor}.{patch}{channel}{release}"',
            }
        )

# Add a setup.py shim.
shim_text = """# setup.py shim for use with applications that require it.
__import__("setuptools").setup()
"""
setup_py.write_text(shim_text, encoding="utf-8")

# Remove old files
for fname in ["MANIFEST.in", "setup.cfg"]:
    fpath = Path(fname)
    if fpath.exists():
        fpath.unlink()

# Write out the new config.
logger.info("\n\nWriting pyproject.toml")
pyproject.write_text(tomli_w.dumps(data), "utf-8")

if warnings:
    logger.info("\n\nWarning!! Not everything could be migrated automatically.")
    logger.info("Please address the following concerns:")
    for warning in warnings:
        logger.info("  - %s", warning)

logger.info("\n\nMigration complete!")
