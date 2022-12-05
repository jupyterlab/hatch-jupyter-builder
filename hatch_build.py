import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

from hatch_jupyter_builder.plugin import JupyterBuildHook


class CustomHook(JupyterBuildHook):
    def initialize(self, version, build_data):
        self.config["pre_commit_hatch_script"] = "lint:fmt"
        super().initialize(version, build_data)


def get_build_hook():
    return CustomHook
