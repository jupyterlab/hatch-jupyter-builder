import os
from pathlib import Path
from unittest.mock import call

import pytest

from hatch_jupyter_builder import npm_builder


def test_npm_builder(mocker):
    which = mocker.patch("hatch_jupyter_builder.utils.which")
    run = mocker.patch("hatch_jupyter_builder.utils.run")
    which.return_value = "foo"
    npm_builder("wheel", "standard", force=True)
    cwd = str(Path.cwd())
    run.assert_has_calls(
        [call(["foo", "install"], cwd=cwd), call(["foo", "run", "build"], cwd=cwd)]
    )


def test_npm_build_skip(mocker):
    which = mocker.patch("hatch_jupyter_builder.utils.which")
    run = mocker.patch("hatch_jupyter_builder.utils.run")
    os.environ["HATCH_JUPYTER_BUILDER_SKIP_NPM"] = "1"
    which.return_value = "foo"
    npm_builder("wheel", "standard", force=True)
    run.assert_not_called()
    del os.environ["HATCH_JUPYTER_BUILDER_SKIP_NPM"]


def test_npm_builder_yarn(tmp_path, mocker):
    which = mocker.patch("hatch_jupyter_builder.utils.which")
    run = mocker.patch("hatch_jupyter_builder.utils.run")
    tmp_path.joinpath("yarn.lock").write_text("hello")
    which.return_value = "foo"
    npm_builder("wheel", "standard", path=tmp_path, force=True)
    run.assert_has_calls(
        [
            call(["foo", "install"], cwd=str(tmp_path)),
            call(["foo", "run", "build"], cwd=str(tmp_path)),
        ]
    )


def test_npm_builder_missing_yarn(tmp_path, mocker):
    which = mocker.patch("hatch_jupyter_builder.utils.which")
    run = mocker.patch("hatch_jupyter_builder.utils.run")
    tmp_path.joinpath("yarn.lock").write_text("hello")
    which.side_effect = ["", "foo"]
    npm_builder("wheel", "standard", path=tmp_path, force=True)
    run.assert_has_calls(
        [
            call(["foo", "install"], cwd=str(tmp_path)),
            call(["foo", "run", "build"], cwd=str(tmp_path)),
        ]
    )


def test_npm_builder_not_stale(tmp_path, mocker):
    which = mocker.patch("hatch_jupyter_builder.utils.which")
    run = mocker.patch("hatch_jupyter_builder.utils.run")
    is_stale = mocker.patch("hatch_jupyter_builder.utils.is_stale")
    is_stale.return_value = False
    which.return_value = "foo"
    npm_builder("wheel", "standard", build_dir=tmp_path, source_dir=tmp_path, force=True)
    run.assert_not_called()


def test_npm_builder_no_npm(mocker):
    which = mocker.patch("hatch_jupyter_builder.utils.which")
    run = mocker.patch("hatch_jupyter_builder.utils.run")
    is_stale = mocker.patch("hatch_jupyter_builder.utils.is_stale")
    is_stale.return_value = False
    which.return_value = ""
    with pytest.raises(ValueError):
        npm_builder("wheel", "standard", force=True)
    run.assert_not_called()
