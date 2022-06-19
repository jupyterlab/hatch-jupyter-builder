import glob
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import tomli

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
        subprocess.run([python, "-m", "hatch_jupyter_builder.migration", target1])
        source_toml = source.joinpath("pyproject.toml").read_text(encoding="utf-8")
        target_toml = target1.joinpath("pyproject.toml").read_text(encoding="utf-8")
        source_data = tomli.loads(source_toml)
        target_data = tomli.loads(target_toml)
        assert source_data == target_data

        # Compare the produced wheel and sdist for the migrated and unmigrated
        # extensions.
        for asset in ["sdist", "wheel"]:
            subprocess.check_call(
                [
                    python,
                    "-m",
                    "hatch_jupyter_builder.migration.compare",
                    str(target1),
                    str(target2),
                    asset,
                ]
            )

            # Check the produced dist file in strict mode.
            dist_files = glob.glob(str(target1 / "dist/*.*"))
            assert len(dist_files) == 1
            subprocess.check_call([python, "-m", "twine", "check", "--strict", dist_files[0]])
