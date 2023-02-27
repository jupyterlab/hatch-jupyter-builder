"""Jupyter LabExtension Entry Points."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import sys
from copy import copy

from jupyter_core.application import JupyterApp, base_aliases, base_flags
from jupyterlab.labapp import LabApp
from traitlets import Bool, List, Unicode, default

from .debuglog import DebugLogFileMixin
from .extension_utils import (
    HERE,
)
from .federated_labextensions import build_labextension, develop_labextension_py, watch_labextension

flags = dict(base_flags)

develop_flags = copy(flags)
develop_flags["overwrite"] = (
    {"DevelopLabExtensionApp": {"overwrite": True}},
    "Overwrite files",
)

aliases = dict(base_aliases)
aliases["debug-log-path"] = "DebugLogFileMixin.debug_log_path"

VERSION = ""  # FIXME Get the package version

LABEXTENSION_COMMAND_WARNING = "Users should manage prebuilt extensions with package managers like pip and conda, and extension authors are encouraged to distribute their extensions as prebuilt packages"


class BaseExtensionApp(JupyterApp, DebugLogFileMixin):
    version = VERSION
    flags = flags
    aliases = aliases
    name = "lab"

    labextensions_path = List(
        Unicode(),
        help="The standard paths to look in for prebuilt JupyterLab extensions",
    )

    @default("labextensions_path")
    def _default_labextensions_path(self):
        lab = LabApp()
        lab.load_config_file()
        return lab.extra_labextensions_path + lab.labextensions_path

    def start(self):
        with self.debug_logging():
            self.run_task()

    def run_task(self):
        pass

    def _log_format_default(self):
        """A default format for messages"""
        return "%(message)s"


class DevelopLabExtensionApp(BaseExtensionApp):
    description = "(developer) Develop labextension"
    flags = develop_flags

    user = Bool(False, config=True, help="Whether to do a user install")
    sys_prefix = Bool(True, config=True, help="Use the sys.prefix as the prefix")
    overwrite = Bool(False, config=True, help="Whether to overwrite files")
    symlink = Bool(True, config=False, help="Whether to use a symlink")

    labextensions_dir = Unicode(
        "",
        config=True,
        help="Full path to labextensions dir (probably use prefix or user)",
    )

    def run_task(self):
        """Add config for this labextension"""
        self.extra_args = self.extra_args or [os.getcwd()]
        for arg in self.extra_args:
            develop_labextension_py(
                arg,
                user=self.user,
                sys_prefix=self.sys_prefix,
                labextensions_dir=self.labextensions_dir,
                logger=self.log,
                overwrite=self.overwrite,
                symlink=self.symlink,
            )


class BuildLabExtensionApp(BaseExtensionApp):
    description = "(developer) Build labextension"

    static_url = Unicode("", config=True, help="Sets the url for static assets when building")

    development = Bool(False, config=True, help="Build in development mode")

    source_map = Bool(False, config=True, help="Generate source maps")

    core_path = Unicode(
        os.path.join(HERE, "staging"),
        config=True,
        help="Directory containing core application package.json file",
    )

    aliases = {
        "static-url": "BuildLabExtensionApp.static_url",
        "development": "BuildLabExtensionApp.development",
        "source-map": "BuildLabExtensionApp.source_map",
        "core-path": "BuildLabExtensionApp.core_path",
    }

    def run_task(self):
        self.extra_args = self.extra_args or [os.getcwd()]
        build_labextension(
            self.extra_args[0],
            logger=self.log,
            development=self.development,
            static_url=self.static_url or None,
            source_map=self.source_map,
            core_path=self.core_path or None,
        )


class WatchLabExtensionApp(BaseExtensionApp):
    description = "(developer) Watch labextension"

    development = Bool(True, config=True, help="Build in development mode")

    source_map = Bool(False, config=True, help="Generate source maps")

    core_path = Unicode(
        os.path.join(HERE, "staging"),
        config=True,
        help="Directory containing core application package.json file",
    )

    aliases = {
        "development": "BuildLabExtensionApp.development",
        "source-map": "BuildLabExtensionApp.source_map",
        "core-path": "BuildLabExtensionApp.core_path",
    }

    def run_task(self):
        self.extra_args = self.extra_args or [os.getcwd()]
        labextensions_path = self.labextensions_path
        watch_labextension(
            self.extra_args[0],
            labextensions_path,
            logger=self.log,
            development=self.development,
            source_map=self.source_map,
            core_path=self.core_path or None,
        )


_EXAMPLES = """
jupyter labextension develop                     # (developer) develop a prebuilt labextension
jupyter labextension build                       # (developer) build a prebuilt labextension
jupyter labextension watch                       # (developer) watch a prebuilt labextension
"""


class LabExtensionApp(JupyterApp):
    """Base jupyter labextension command entry point"""

    name = "jupyter labextension"
    version = VERSION
    description = "Work with JupyterLab extensions"
    examples = _EXAMPLES

    subcommands = {
        "develop": (DevelopLabExtensionApp, "(developer) Develop labextension(s)"),
        "build": (BuildLabExtensionApp, "(developer) Build labextension"),
        "watch": (WatchLabExtensionApp, "(developer) Watch labextension"),
    }

    def start(self):
        """Perform the App's functions as configured"""
        super().start()

        # The above should have called a subcommand and raised NoStart; if we
        # get here, it didn't, so we should self.log.info a message.
        subcmds = ", ".join(sorted(self.subcommands))
        self.exit("Please supply at least one subcommand: %s" % subcmds)


main = LabExtensionApp.launch_instance

if __name__ == "__main__":
    sys.exit(main())
