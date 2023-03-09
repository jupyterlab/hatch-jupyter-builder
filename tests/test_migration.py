import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from hatch_jupyter_builder.compare_migrated.cli import main

HERE = Path(__file__).parent.absolute()
REPO_ROOT = str(HERE.parent).replace(os.sep, "/")


@pytest.mark.migration_test()
def test_npm_builder_migration():
    python = sys.executable
    os.environ["BUILDER_VERSION_SPEC"] = f"@file://{REPO_ROOT}"
    # Copy the source cookiecutter extension into two temporary directories.
    with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
        source = HERE / "data" / "npm_builder"
        shutil.copytree(source / "myextension", Path(td1) / "myextension")
        shutil.copytree(source / "myextension", Path(td2) / "myextension")
        target1 = Path(td1) / "myextension"
        target2 = Path(td2) / "myextension"

        # Migrate the first extension and compare its migrated pyproject.toml
        # to the expected one.
        subprocess.check_call([python, "-m", "hatch_jupyter_builder.migrate", target1])
        source_toml = source.joinpath("pyproject.toml").read_text(encoding="utf-8")
        target_toml = target1.joinpath("pyproject.toml").read_text(encoding="utf-8")
        source_data = tomllib.loads(source_toml)
        target_data = tomllib.loads(target_toml)

        # The hatchling and hatch_jupyter_builder versions might differ.
        source_data["build-system"]["requires"] = target_data["build-system"]["requires"]
        source_hooks = source_data["tool"]["hatch"]["build"]["hooks"]
        target_hooks = target_data["tool"]["hatch"]["build"]["hooks"]
        source_hooks["jupyter-builder"] = target_hooks["jupyter-builder"]
        # Hatchling might add some classifiers
        del source_data["project"]["classifiers"]
        del target_data["project"]["classifiers"]
        assert source_data == target_data

        # Compare the produced wheel and sdist for the migrated and unmigrated
        # extensions.
        for asset in ["sdist", "wheel"]:
            results = main(target2, target1, asset)

            if asset == "sdist":
                for item in results["removed"]:
                    assert "static/remoteEntry." in item

                for item in results["added"]:
                    assert ".eslintrc.js" in item or "static/remoteEntry." in item

            else:
                for item in results["removed"]:
                    assert "static/remoteEntry." in item or "top_level.txt" in item

                for item in results["added"]:
                    assert "static/remoteEntry." in item

            # Check the produced dist file in strict mode.
            dist_files = glob.glob(str(target1 / "dist/*.*"))
            assert len(dist_files) == 1
            subprocess.check_call([python, "-m", "twine", "check", "--strict", dist_files[0]])


@pytest.mark.migration_test()
def test_create_cmdclass_migration():
    python = sys.executable
    os.environ["BUILDER_VERSION_SPEC"] = f"@file://{REPO_ROOT}"
    # Copy the source cookiecutter extension into two temporary directories.
    with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
        source = HERE / "data" / "create_cmdclass"
        shutil.copytree(source / "myproject", Path(td1) / "myproject")
        shutil.copytree(source / "myproject", Path(td2) / "myproject")
        target1 = Path(td1) / "myproject"
        target2 = Path(td2) / "myproject"

        # Migrate the first extension and compare its migrated pyproject.toml
        # to the expected one.
        subprocess.check_call([python, "-m", "hatch_jupyter_builder.migrate", target1])
        source_toml = source.joinpath("pyproject.toml").read_text(encoding="utf-8")
        target_toml = target1.joinpath("pyproject.toml").read_text(encoding="utf-8")
        source_data = tomllib.loads(source_toml)
        target_data = tomllib.loads(target_toml)

        # The hatchling and hatch_jupyter_builder versions might differ.
        source_data["build-system"]["requires"] = target_data["build-system"]["requires"]
        source_hooks = source_data["tool"]["hatch"]["build"]["hooks"]
        target_hooks = target_data["tool"]["hatch"]["build"]["hooks"]
        source_hooks["jupyter-builder"] = target_hooks["jupyter-builder"]
        # Hatchling might add some classifiers
        del source_data["project"]["classifiers"]
        del target_data["project"]["classifiers"]
        assert source_data == target_data

        # Compare the produced wheel and sdist for the migrated and unmigrated
        # extensions.
        for asset in ["sdist", "wheel"]:
            results = main(target2, target1, asset)

            for item in results["removed"]:
                assert (
                    "remoteEntry." in item
                    or "embed-bundle.js" in item
                    or "dist-info/LICENSE.txt" in item
                    or "dist-info/top_level.txt" in item
                )

            if asset == "sdist":
                assert len(results["added"]) == 8
            else:
                for item in results["added"]:
                    assert (
                        "remoteEntry." in item
                        or "licenses/LICENSE.txt" in item
                        or "dist-info/entry_points.txt" in item
                    )

            # Check the produced dist file in strict mode.
            dist_files = glob.glob(str(target1 / "dist/*.*"))
            assert len(dist_files) == 1
            subprocess.check_call([python, "-m", "twine", "check", "--strict", dist_files[0]])
