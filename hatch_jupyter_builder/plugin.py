from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from .utils import (
    ensure_targets,
    get_build_func,
    install_pre_commit_hook,
    normalize_kwargs,
)


class JupyterBuildHook(BuildHookInterface):
    PLUGIN_NAME = "jupyter-builder"

    def initialize(self, version, build_data):
        if self.target_name not in ["wheel", "sdist"]:
            return

        should_install_hook = self.config.get("install-pre-commit-hook")

        if version == "editable" and should_install_hook:
            install_pre_commit_hook()

        # Get the configuration options.
        build_function = self.config.get("build-function")
        build_kwargs = self.config.get("build-kwargs", {})
        editable_build_kwargs = self.config.get("editable-build-kwargs")
        ensured_targets = self.config.get("ensured-targets", [])

        if not build_function:
            return

        # Get build function and call it with normalized parameter names.
        build_func = get_build_func(build_function)

        if version == "editable":
            build_kwargs = editable_build_kwargs or build_kwargs

        build_kwargs = normalize_kwargs(build_kwargs)
        build_func(self.target_name, version, **build_kwargs)

        # Ensure targets in distributable dists.
        if version == "standard":
            ensure_targets(ensured_targets)
