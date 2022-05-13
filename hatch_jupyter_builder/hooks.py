from hatchling.plugin import hookimpl

from .plugin import JupyterBuildHook


@hookimpl
def hatch_register_build_hook():
    return JupyterBuildHook
