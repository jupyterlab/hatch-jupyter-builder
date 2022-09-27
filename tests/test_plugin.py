import os
import subprocess
import venv
from pathlib import Path

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

    config["editable-build-kwargs"] = {"foo-bar": "2", "fizz_buzz": "3"}
    assert hook.initialize("editable", {})

    hook = JupyterBuildHook(tmp_path, config, {}, {}, tmp_path, "foo")
    assert not hook.initialize("standard", {})

    os.environ["SKIP_JUPYTER_BUILD"] = "1"
    assert not hook.initialize("standard", {})
    del os.environ["SKIP_JUPYTER_BUILD"]


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
