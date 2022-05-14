import os
from pathlib import Path

from hatch_jupyter_builder.plugin import JupyterBuildHook


def test_build_hook(tmp_path):
    config = {
        "build-function": "test.foo",
        "ensured-targets": ["test.py"],
        "build-kwargs": {"foo-bar": "1", "fizz_buzz": "2"},
    }
    os.chdir(tmp_path)
    test = Path("test.py")
    text = """
def foo(target_name, version, foo_bar=None, fizz_buzz=None):
    return(target_name)
"""
    test.write_text(text, encoding="utf-8")

    hook = JupyterBuildHook(tmp_path, config, {}, {}, tmp_path, "wheel")
    hook.initialize("standard", {})
    hook.initialize("editable", {})

    hook = JupyterBuildHook(tmp_path, config, {}, {}, tmp_path, "sdist")
    hook.initialize("standard", {})

    hook = JupyterBuildHook(tmp_path, {}, {}, {}, tmp_path, "wheel")
    hook.initialize("standard", {})
