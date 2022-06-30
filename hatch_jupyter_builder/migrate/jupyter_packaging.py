import os
import sys
from pathlib import Path

import tomli
import tomli_w

__this_shim = sys.modules.pop("jupyter_packaging")
__current_directory = sys.path.pop(0)

import jupyter_packaging as __real_jupyter_packaging

sys.path.insert(0, __current_directory)
sys.modules["jupyter_packaging"] = __this_shim


def _write_config(path, data):
    pyproject = Path("pyproject.toml")
    top = tomli.loads(pyproject.read_text(encoding="utf-8"))
    current = top
    parts = path.split(".")
    for part in parts[:-1]:
        if part in current:
            current = current[part]
        else:
            current[part] = current = {}
    if parts[-1] in current:
        existing = current[parts[-1]]
    else:
        existing = current[parts[-1]] = {}
    existing.update(data)
    pyproject.write_text(tomli_w.dumps(top), encoding="utf-8")


_npm_kwargs = ["path", "build_dir", "source_dir", "build_cmd", "npm"]


def _normalize_path(path):
    path = str(path)
    cwd = os.getcwd()
    if path.startswith(cwd):
        return os.path.relpath(path, cwd)
    return path


def _get_build_kwargs(**kwargs):
    build_kwargs = {}
    for name in _npm_kwargs:
        value = kwargs[name]
        if value is not None:
            if name in ["path", "build_dir", "source_dir"]:
                value = _normalize_path(value)
            build_kwargs[name] = value
    if kwargs.get("force"):
        build_kwargs["force"] = True
    return build_kwargs


def skip_if_exists(paths, *args):
    if paths:
        data = {"skip-if-exists": [_normalize_path(p) for p in paths]}
        _write_config("tool.hatch.build.hooks.jupyter-builder", data)
    return __real_jupyter_packaging.skip_if_exists(paths, *args)


def ensure_targets(targets):
    if targets:
        data = {"ensured-targets": [_normalize_path(t) for t in targets]}
        _write_config("tool.hatch.build.hooks.jupyter-builder", data)
    return __real_jupyter_packaging.ensure_targets(targets)


def wrap_installers(
    pre_develop=None,
    pre_dist=None,
    post_develop=None,
    post_dist=None,
    ensured_targets=None,
    skip_if_exists=None,
):
    if pre_develop or post_develop:
        func = pre_develop or post_develop
        build_kwargs = _get_build_kwargs(**func.__kwargs)
        _write_config("tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs", build_kwargs)

    if pre_dist or post_dist:
        func = pre_dist or post_dist
        build_kwargs = _get_build_kwargs(**func.__kwargs)
        _write_config("tool.hatch.build.hooks.jupyter-builder.build-kwargs", build_kwargs)

    if skip_if_exists:
        data = {"skip-if-exists": [_normalize_path(p) for p in skip_if_exists]}
        _write_config("tool.hatch.build.hooks.jupyter-builder", data)

    return __real_jupyter_packaging.wrap_installers(
        pre_develop=pre_develop,
        pre_dist=pre_dist,
        post_develop=post_develop,
        post_dist=post_dist,
        ensured_targets=ensured_targets,
        skip_if_exists=skip_if_exists,
    )


def create_cmdclass(
    prerelease_cmd=None, package_data_spec=None, data_files_spec=None, exclude=None
):
    shared_data = {}
    if data_files_spec is not None:
        for (path, dname, pattern) in data_files_spec:
            if pattern == "**":
                shared_data[dname] = path
            else:
                shared_data[f"{dname}/{pattern}"] = f"{path}/{pattern}"

    print(shared_data)

    _write_config("tool.hatch.build.targets.wheel.shared-data", shared_data)

    return __real_jupyter_packaging.create_cmdclass(
        prerelease_cmd=prerelease_cmd,
        package_data_spec=package_data_spec,
        data_files_spec=data_files_spec,
        exclude=exclude,
    )


def install_npm(
    path=None, build_dir=None, source_dir=None, build_cmd="build", force=False, npm=None
):
    build_kwargs = _get_build_kwargs(**locals())
    if build_kwargs:
        _write_config("tool.hatch.build.hooks.jupyter-builder.build-kwargs", build_kwargs)

    return __real_jupyter_packaging.install_npm(
        path=path,
        build_dir=build_dir,
        source_dir=source_dir,
        build_cmd=build_cmd,
        force=force,
        npm=npm,
    )


def npm_builder(
    path=None, build_dir=None, source_dir=None, build_cmd="build", force=False, npm=None
):
    func = __real_jupyter_packaging.npm_builder(
        path=path,
        build_dir=build_dir,
        source_dir=source_dir,
        build_cmd=build_cmd,
        force=force,
        npm=npm,
    )
    func.__kwargs = {}
    for name in _npm_kwargs + ["force"]:
        func.__kwargs[name] = locals()[name]
    return func


def __getattr__(name):
    return getattr(__real_jupyter_packaging, name)


del __this_shim
del __current_directory
