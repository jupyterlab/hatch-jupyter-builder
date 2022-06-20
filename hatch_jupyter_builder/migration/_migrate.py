import json
import os
import re
import subprocess
import sys
from pathlib import Path

import tomli
import tomli_w

print("Starting pyproject.toml migration")

warnings = []

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
    current_version = "!!UNKONWN!!"


# Automatic migration from hatch.
subprocess.run([sys.executable, "-m", "hatch", "new", "--init"])

# Handle setup.cfg
# Move flake8 config to separate file, preserving comments.
# Add .flake8 file to git.
# Remove file when done.
setup_cfg = Path("setup.cfg")
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

        if matches and line.startswith("["):
            break

        flake8.append(line)

    Path(".flake8").write_text("\n".join(flake8) + "\n", "utf-8")

    subprocess.run(["git", "add", ".flake"])

# Handle pyproject.toml config.
# Migrate and remove unused config.
pyproject = Path("pyproject.toml")
text = pyproject.read_text("utf-8")
data = tomli.loads(text)

tool_table = data.setdefault("tool", {})

# Remove old check-manifest config.
if "check-manifest" in tool_table:
    del tool_table["check-manifest"]

# Build up the hatch config.
hatch_table = tool_table.setdefault("hatch", {})
build_table = hatch_table.setdefault("build", {})
targets_table = build_table.setdefault("targets", {})

# Remove the dynamic version.
if current_version:
    del hatch_table["version"]

# Remove any auto-generated sdist config.
if "sdist" in targets_table:
    del targets_table["sdist"]

# Exclude the .github folder by default.
targets_table["sdist"] = dict(exclude=[".github"])

hooks_table = build_table.setdefault("hooks", {})
hooks_table["jupyter-builder"] = {}
builder_table: dict = hooks_table["jupyter-builder"]
builder_table["dependencies"] = ["hatch-jupyter-builder>=0.3.3"]

# Migrate the jupyter-packaging static data.
if "jupyter-packaging" in tool_table:
    packaging_table = tool_table.get("jupyter-packaging", {})
    del tool_table["jupyter-packaging"]

    options_table = packaging_table.setdefault("options", {})
    build_args_table = packaging_table.setdefault("build-args", {})
    builder_table["build-function"] = "hatch_jupyter_builder.npm_builder"

    for option in ["ensured-targets", "skip-if-exists"]:
        if option in options_table:
            builder_table[option] = options_table[option]

    if build_args_table:
        builder_table["build-kwargs"] = build_args_table.copy()

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


# Handle setup.py - jupyter_packaging and pre-commit config.
# Remove the file when finished.
if setup_py.exists():
    text = setup_py.read_text("utf-8")
    if "pre-commit" in text:
        builder_table["install-pre-commit"] = True

    build_kwargs = builder_table.setdefault("build-kwargs", {})
    editable_build_command = None
    if "build_cmd" in text:
        match = re.search('build_cmd="(.*?)"', text, re.MULTILINE)
        assert match is not None
        editable_build_command = match.groups()[0]

    if "source_dir" in text or "build_dir" in text:
        builder_table["editable-build-kwargs"] = {}
        editable_build_kwargs: dict = builder_table["editable-build-kwargs"]
        editable_build_kwargs["build_cmd"] = editable_build_command

        for name in ["source_dir", "build_dir"]:
            if name not in text:
                continue
            match = re.search(f'{name}="(.*?)"', text, re.MULTILINE)
            if match is not None:
                editable_build_kwargs[name] = match.groups()[0]
            else:
                warnings.append(
                    f"Fill in '[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs][{name}]' in 'pyproject.toml', which was the '{name}' argument to 'npm_builder' in 'setup.py'"
                )
                editable_build_kwargs[name] = "!!! needs manual input !!!"

    elif editable_build_command:
        build_kwargs["editable_build_cmd"] = editable_build_command

    # Handle versioning with tbump - allows for static versioning and makes
    # it easier to use jupyter_releaser.
    data["project"]["version"] = current_version
    data["project"].pop("dynamic", None)

    tbump_table = tool_table.setdefault("tbump", {})
    tbump_table["version"] = dict(
        current=current_version,
        regex=r"""
          (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)((?P<channel>a|b|rc|.dev)(?P<release>\d+))?
        """.strip(),
    )
    tbump_table["git"] = dict(
        message_template=r"Bump to {new_version}", tag_template=r"v{new_version}"
    )
    tbump_table["field"] = [dict(name="channel", default=""), dict(name="release", default="")]
    tbump_table["file"] = [dict(src="pyproject.toml")]

    # Add entry for _version.py if it exists.
    version_py = Path(project_name) / "_version.py"
    if version_py.exists():
        tbump_table["file"].append(dict(src=str(version_py)))
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
            tbump_table["file"].append(dict(src="package.json"))

# Add a setup.py shim.
shim_text = """# setup.py shim for use with applications that require it.
__import__("setuptools").setup()
"""
setup_py.write_text(shim_text, encoding="utf-8")

# Remove old files
for fname in ["MANIFEST.in", "setup.cfg"]:
    if os.path.exists(fname):
        os.remove(fname)

# Write out the new config.
print("Writing pyproject.toml")
pyproject.write_text(tomli_w.dumps(data), "utf-8")

if warnings:
    print("Please address the following concerns:")
    for warning in warnings:
        print(f"  - {warning}")
