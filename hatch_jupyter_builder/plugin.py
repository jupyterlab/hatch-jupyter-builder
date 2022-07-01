from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from .utils import (
    _get_log,
    ensure_targets,
    get_build_func,
    install_pre_commit_hook,
    normalize_kwargs,
    should_skip,
)


class JupyterBuildHook(BuildHookInterface):
    PLUGIN_NAME = "jupyter-builder"

    def initialize(self, version, build_data):
        log = _get_log()
        log.info("Running jupyter-builder")
        if self.target_name not in ["wheel", "sdist"]:
            log.info(f"ignoring target name {self.target_name}")
            return

        should_install_hook = self.config.get("install-pre-commit-hook")

        if version == "editable" and should_install_hook:
            install_pre_commit_hook()

        # Get the configuration options.
        build_function = self.config.get("build-function")
        build_kwargs = self.config.get("build-kwargs", {})
        editable_build_kwargs = self.config.get("editable-build-kwargs")
        ensured_targets = self.config.get("ensured-targets", [])
        skip_if_exists = self.config.get("skip-if-exists", [])

        if version == "editable":
            build_kwargs = editable_build_kwargs or build_kwargs

        should_skip_build = False
        if not build_function:
            log.warning("No build function found")
            should_skip_build = True

        elif skip_if_exists and version == "standard":
            should_skip_build = should_skip(skip_if_exists)
            if should_skip_build:
                log.info("Skip-if-exists file(s) found")

        # Get build function and call it with normalized parameter names.
        if not should_skip_build:
            build_func = get_build_func(build_function)
            build_kwargs = normalize_kwargs(build_kwargs)
            log.info(f"Building with {build_function}")
            log.info(f"With kwargs: {build_kwargs}")
            build_func(self.target_name, version, **build_kwargs)
        else:
            log.info("Skipping build")

        # Ensure targets in distributable dists.
        if version == "standard":
            ensure_targets(ensured_targets)

        log.info("Finished running jupyter-builder")
