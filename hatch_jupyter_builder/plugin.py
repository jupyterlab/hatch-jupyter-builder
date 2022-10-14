import os
import typing as t
import warnings
from dataclasses import dataclass, field, fields

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from .utils import (
    _get_log,
    ensure_targets,
    get_build_func,
    install_pre_commit_hook,
    normalize_kwargs,
    should_skip,
)


@dataclass
class JupyterBuildConfig:
    """Build config values for Hatch Jupyter Builder."""

    install_pre_commit_hook: str = ""
    build_function: t.Optional[str] = None
    build_kwargs: t.Mapping[str, str] = field(default_factory=dict)
    editable_build_kwargs: t.Mapping[str, str] = field(default_factory=dict)
    ensured_targets: t.List[str] = field(default_factory=list)
    skip_if_exists: t.List[str] = field(default_factory=list)
    optional_editable_build: str = ""


class JupyterBuildHook(BuildHookInterface):
    PLUGIN_NAME = "jupyter-builder"

    def initialize(self, version, build_data):
        log = _get_log()
        log.info("Running jupyter-builder")
        if self.target_name not in ["wheel", "sdist"]:
            log.info(f"ignoring target name {self.target_name}")
            return False

        if os.getenv("SKIP_JUPYTER_BUILDER"):
            log.info("Skipping the build hook since SKIP_JUPYTER_BUILDER was set")
            return False

        kwargs = normalize_kwargs(self.config)
        available_fields = [f.name for f in fields(JupyterBuildConfig)]
        for key in list(kwargs):
            if key not in available_fields:
                del kwargs[key]
        config = JupyterBuildConfig(**kwargs)

        should_install_hook = config.install_pre_commit_hook.lower() == "true"

        if version == "editable" and should_install_hook:
            install_pre_commit_hook()

        build_kwargs = config.build_kwargs
        if version == "editable":
            build_kwargs = config.editable_build_kwargs or build_kwargs

        should_skip_build = False
        if not config.build_function:
            log.warning("No build function found")
            should_skip_build = True

        elif config.skip_if_exists and version == "standard":
            should_skip_build = should_skip(config.skip_if_exists)
            if should_skip_build:
                log.info("Skip-if-exists file(s) found")

        # Get build function and call it with normalized parameter names.
        if not should_skip_build and config.build_function:
            build_func = get_build_func(config.build_function)
            build_kwargs = normalize_kwargs(build_kwargs)
            log.info(f"Building with {config.build_function}")
            log.info(f"With kwargs: {build_kwargs}")
            try:
                build_func(self.target_name, version, **build_kwargs)
            except Exception as e:
                if version == "editable" and config.optional_editable_build.lower() == "true":
                    warnings.warn(f"Encountered build error:\n{e}")
                else:
                    raise e
        else:
            log.info("Skipping build")

        # Ensure targets in distributable dists.
        if version == "standard":
            ensure_targets(config.ensured_targets)

        log.info("Finished running jupyter-builder")
        return True
