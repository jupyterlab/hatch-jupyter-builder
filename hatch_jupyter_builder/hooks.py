"""Register hooks for the plugin."""
from typing import Type

from hatchling.plugin import hookimpl

from .plugin import JupyterBuildHook


@hookimpl
def hatch_register_build_hook() -> Type[JupyterBuildHook]:
    """Get the hook implementation."""
    return JupyterBuildHook
