import glob
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import tomli

from hatch_jupyter_builder.compare_migration.__main__ import main

HERE = Path(__file__).parent.absolute()


@pytest.mark.migration_test
def test_migration():
    python = sys.executable
    # Copy the source cookiecutter extension into two temporary directories.
    with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
        source = HERE / "data"
        shutil.copytree(source / "myextension", Path(td1) / "myextension")
        shutil.copytree(source / "myextension", Path(td2) / "myextension")
        target1 = Path(td1) / "myextension"
        target2 = Path(td2) / "myextension"

        # Migrate the first extension and compare its migrated pyproject.toml
        # to the expected one.
        subprocess.check_call([python, "-m", "hatch_jupyter_builder.migrate", target1])
        source_toml = source.joinpath("pyproject.toml").read_text(encoding="utf-8")
        target_toml = target1.joinpath("pyproject.toml").read_text(encoding="utf-8")
        source_data = tomli.loads(source_toml)
        target_data = tomli.loads(target_toml)

        # The hatchling and hatch_jupyter_builder versions might differ.
        source_data["build-system"]["requires"] = target_data["build-system"]["requires"]
        source_hooks = source_data["tool"]["hatch"]["build"]["hooks"]
        target_hooks = target_data["tool"]["hatch"]["build"]["hooks"]
        source_hooks["jupyter-builder"] = target_hooks["jupyter-builder"]
        assert source_data == target_data

        # Compare the produced wheel and sdist for the migrated and unmigrated
        # extensions.
        for asset in ["sdist", "wheel"]:
            results = main(target1, target2, asset)

            if asset == "sdist":
                assert len(results["added"]) == 1
                assert "static/remoteEntry." in results["added"][0]

                assert len(results["removed"]) == 2
                for item in results["removed"]:
                    assert ".eslintrc.js" in item or "static/remoteEntry." in item

            else:
                assert len(results["added"]) == 3
                for item in results["added"]:
                    assert "static/remoteEntry." in item or "top_level.txt" in item

                assert len(results["removed"]) == 3
                for item in results["removed"]:
                    assert "entry_points.txt" in item or "static/remoteEntry." in item

            # Check the produced dist file in strict mode.
            dist_files = glob.glob(str(target1 / "dist/*.*"))
            assert len(dist_files) == 1
            subprocess.check_call([python, "-m", "twine", "check", "--strict", dist_files[0]])
