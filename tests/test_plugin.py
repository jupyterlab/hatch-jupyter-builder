import os
import platform
import subprocess
import venv
import warnings
from pathlib import Path

import pytest

from hatch_jupyter_builder.plugin import JupyterBuildHook


def test_build_hook(tmp_path):
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

    hook = JupyterBuildHook(tmp_path, config, {}, {}, tmp_path, "wheel")
    assert hook.initialize("standard", {})
    assert hook.initialize("editable", {})

    hook = JupyterBuildHook(tmp_path, config, {}, {}, tmp_path, "sdist")
    assert hook.initialize("standard", {})

    hook = JupyterBuildHook(tmp_path, {}, {}, {}, tmp_path, "wheel")
    assert hook.initialize("standard", {})
    assert hook.initialize("editable", {})

    config["skip-if-exists"] = ["foo", "bar"]
    assert hook.initialize("standard", {})
    del config["skip-if-exists"]

    config["editable-build-kwargs"] = {"foo-bar": "2", "fizz_buzz": "3"}
    assert hook.initialize("editable", {})

    hook = JupyterBuildHook(tmp_path, config, {}, {}, tmp_path, "foo")
    assert not hook.initialize("standard", {})

    config["build-function"] = "test2.foo"
    text = """
def foo(target_name, version, foo_bar=None, fizz_buzz=None):
    raise RuntimeError('trigger error')
"""
    test2 = Path("test2.py")
    test2.write_text(text, encoding="utf-8")

    hook = JupyterBuildHook(tmp_path, config, {}, {}, tmp_path, "wheel")
    with pytest.raises(RuntimeError):
        hook.initialize("editable", {})

    os.environ["SKIP_JUPYTER_BUILDER"] = "1"
    assert not hook.initialize("standard", {})
    del os.environ["SKIP_JUPYTER_BUILDER"]

    config["optional-editable-build"] = "true"
    hook = JupyterBuildHook(tmp_path, config, {}, {}, tmp_path, "wheel")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert hook.initialize("editable", {})


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
    subprocess.check_call([python, "-m", "pip", "install", "build"], cwd=tmp_path)
    subprocess.check_call([python, "-m", "build", "--sdist", "."], cwd=tmp_path)
