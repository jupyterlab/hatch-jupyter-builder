import os
import platform
import subprocess
import sys
import venv
import warnings
from pathlib import Path

import pytest
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManager

from hatch_jupyter_builder.plugin import JupyterBuildHook


def test_build_hook(tmp_path):
    manager = PluginManager()
    meta = ProjectMetadata(".", manager, {})

    if "SKIP_JUPYTER_BUILD" in os.environ:
        del os.environ["SKIP_JUPYTER_BUILD"]

    config = {
        "build-function": "test.foo",
        "ensured-targets": ["test.py"],
        "build-kwargs": {"foo-bar": "1", "fizz_buzz": "2"},
        "install-pre-commit-hook": True,
    }
    os.chdir(tmp_path)
    test = Path("test.py")
    text = """
def foo(target_name, version, foo_bar=None, fizz_buzz=None):
    return(target_name)
"""
    test.write_text(text, encoding="utf-8")
    os.makedirs(".git/hooks")

    hook = JupyterBuildHook(tmp_path, config, {}, meta, tmp_path, "wheel")
    hook.initialize("standard", {})
    assert not hook._skipped
    hook.initialize("editable", {})
    assert not hook._skipped

    hook = JupyterBuildHook(tmp_path, config, {}, meta, tmp_path, "sdist")
    hook.initialize("standard", {})
    assert not hook._skipped

    hook = JupyterBuildHook(tmp_path, {}, {}, meta, tmp_path, "wheel")
    hook.initialize("standard", {})
    assert not hook._skipped
    hook.initialize("editable", {})
    assert not hook._skipped

    config["skip-if-exists"] = ["foo", "bar"]
    hook.initialize("standard", {})
    assert not hook._skipped
    del config["skip-if-exists"]

    config["editable-build-kwargs"] = {"foo-bar": "2", "fizz_buzz": "3"}
    hook.initialize("editable", {})
    assert not hook._skipped

    hook = JupyterBuildHook(tmp_path, config, {}, meta, tmp_path, "foo")
    hook.initialize("standard", {})
    assert hook._skipped

    text = """
def foo(target_name, version, foo_bar=None, fizz_buzz=None):
    raise RuntimeError('trigger error')
"""
    test.write_text(text, encoding="utf-8")
    # Force a re-import
    del sys.modules["test"]

    hook = JupyterBuildHook(tmp_path, config, {}, meta, tmp_path, "wheel")
    with pytest.raises(RuntimeError):
        hook.initialize("editable", {})

    os.environ["SKIP_JUPYTER_BUILDER"] = "1"
    hook.initialize("standard", {})
    assert hook._skipped
    del os.environ["SKIP_JUPYTER_BUILDER"]

    config["optional-editable-build"] = "true"
    hook = JupyterBuildHook(tmp_path, config, {}, meta, tmp_path, "wheel")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hook.initialize("editable", {})
        assert not hook._skipped

    config["optional-editable-build"] = True
    hook = JupyterBuildHook(tmp_path, config, {}, meta, tmp_path, "wheel")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hook.initialize("editable", {})
        assert not hook._skipped

    del sys.modules["test"]


HERE = Path(__file__).parent
REPO_ROOT = str(HERE.parent).replace(os.sep, "/")
TOML_CONTENT = f"""
[build-system]
requires = ["hatchling>=1.0"]
build-backend = "hatchling.build"

[project]
name = "test"
version = "0.6.0"

[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder@file://{REPO_ROOT}"]
"""


@pytest.mark.skipif(platform.python_implementation() == "PyPy", reason="Does not work on PyPy")
def test_hatch_build(tmp_path):
    venv.create(tmp_path, with_pip=True)
    if os.name == "nt":
        python = Path(tmp_path) / "Scripts/python.exe"
    else:
        python = Path(tmp_path) / "bin/python"
    pyproject = Path(tmp_path) / "pyproject.toml"
    pyproject.write_text(TOML_CONTENT, "utf-8")
    test = Path(tmp_path) / "test.py"
    test.write_text("print('hello')", "utf-8")
    env = os.environ.copy()
    # Handle running min version test.
    if "PIP_CONSTRAINT" in env:
        del env["PIP_CONSTRAINT"]
    subprocess.check_call([python, "-m", "pip", "install", "build"], cwd=tmp_path, env=env)

    subprocess.check_call([python, "-m", "build", "--sdist", "."], cwd=tmp_path, env=env)
