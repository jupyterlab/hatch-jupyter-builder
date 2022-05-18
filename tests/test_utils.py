import os
import shlex
import sys
from pathlib import Path

import pytest

from hatch_jupyter_builder import utils


def test_ensure_targets(tmp_path):
    os.chdir(tmp_path)
    Path("foo.txt").touch()
    os.mkdir("bar")
    Path("bar/fizz.md").touch()
    utils.ensure_targets(["foo.txt", "bar/fizz.md"])

    with pytest.raises(ValueError):
        utils.ensure_targets(["bar.txt"])


def test_run():
    cmd = f"{sys.executable} --version"
    utils.run(cmd)
    utils.run(shlex.split(cmd))


def test_normalize_kwargs():
    kwargs = {"foo-bar": "2", "fizz_buzz": "1"}
    result = utils.normalize_kwargs(kwargs)
    assert result == {"foo_bar": "2", "fizz_buzz": "1"}


def test_normalize_cmd():
    cmd = f"{sys.executable} --version"
    assert utils.normalize_cmd(cmd) == shlex.split(cmd)
    assert utils.normalize_cmd(shlex.split(cmd)) == shlex.split(cmd)
    with pytest.raises(ValueError):
        utils.normalize_cmd("does_not_exist")


def test_get_build_func(tmp_path):
    os.chdir(tmp_path)
    test = Path("test.py")
    text = "def foo(target_name, version):\n    return(target_name)\n"
    test.write_text(text, encoding="utf-8")
    callback = utils.get_build_func("test.foo")
    assert callback("fizz", "buzz") == "fizz"

    with pytest.raises(ImportError):
        utils.get_build_func("does_not_exist.bar")

    with pytest.raises(AttributeError):
        utils.get_build_func("test.bar")


def test_install_pre_commit_hook(tmp_path):
    os.chdir(tmp_path)
    os.makedirs(".git/hooks")
    utils.install_pre_commit_hook()
