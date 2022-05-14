from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from .utils import ensure_targets, get_build_func, normalize_kwargs


class JupyterBuildHook(BuildHookInterface):
    PLUGIN_NAME = "jupyter-builder"

    def initialize(self, version, build_data):
        # Get the configuration options.
        build_function = self.config.get("build-function")
        build_kwargs = self.config.get("build-kwargs", {})
        ensured_targets = self.config.get("ensured-targets", [])

        if not build_function:
            return

        # Get build function and call it with normalized parameter names.
        build_func = get_build_func(build_function)
        build_kwargs = normalize_kwargs(build_kwargs)
        build_func(self.target_name, version, **build_kwargs)

        # Ensure targets in distributable dists.
        if version == "standard":
            ensure_targets(ensured_targets)
