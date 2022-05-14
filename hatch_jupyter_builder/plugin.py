from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from .utils import ensure_targets, get_build_func


class JupyterBuildHook(BuildHookInterface):
    PLUGIN_NAME = "jupyter_builder"

    def initialize(self, version, build_data):
        # Get the configuration options.
        build_function = self.config.get("build_function")
        build_kwargs = self.config.get("build_kwargs", {})
        ensured_targets = self.config.get("ensured_targets", [])
        if not build_function:
            return

        # Get build function, call it, and then ensure targets.
        build_func = get_build_func(build_function)
        build_func(self.target_name, version, **build_kwargs)
        ensure_targets(ensured_targets)
