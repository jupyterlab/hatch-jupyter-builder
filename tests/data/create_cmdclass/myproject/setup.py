# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.


import os
from glob import glob
from os.path import join as pjoin

from jupyter_packaging import (
    combine_commands,
    create_cmdclass,
    ensure_targets,
    get_version,
    install_npm,
    skip_if_exists,
)
from setuptools import find_packages, setup

HERE = os.path.dirname(os.path.abspath(__file__))


# The name of the project
name = "myproject"

# Get the version
version = get_version(pjoin(name, "_version.py"))


# Representative files that should exist after a successful build
jstargets = [
    pjoin(HERE, name, "nbextension", "index.js"),
    pjoin(HERE, name, "labextension", "package.json"),
]


package_data_spec = {name: ["nbextension/**js*", "labextension/**"]}


data_files_spec = [
    ("share/jupyter/nbextensions/myproject", "myproject/nbextension", "**"),
    ("share/jupyter/labextensions/myproject", "myproject/labextension", "**"),
    ("share/jupyter/labextensions/myproject", ".", "install.json"),
    ("etc/jupyter/nbconfig/notebook.d", ".", "myproject.json"),
]


cmdclass = create_cmdclass(
    "jsdeps", package_data_spec=package_data_spec, data_files_spec=data_files_spec
)
npm_install = combine_commands(
    install_npm(HERE, build_cmd="build:prod"),
    ensure_targets(jstargets),
)
cmdclass["jsdeps"] = skip_if_exists(jstargets, npm_install)


setup_args = dict(
    name=name,
    description="A Custom Jupyter Widget Library",
    version=version,
    scripts=glob(pjoin("scripts", "*")),
    cmdclass=cmdclass,
    packages=find_packages(),
    author="me",
    author_email="me@me.com",
    url="https://github.com/myorg/myproject",
    license="BSD",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "Widgets", "IPython"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Jupyter",
    ],
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "ipywidgets>=7.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=4.6",
            "pytest-cov",
            "nbval",
        ],
        "examples": [
            # Any requirements for the examples to run
        ],
        "docs": [
            "jupyter_sphinx",
            "nbsphinx",
            "nbsphinx-link",
            "pytest_check_links",
            "pypandoc",
            "recommonmark",
            "sphinx>=1.5",
            "sphinx_rtd_theme",
        ],
    },
    entry_points={},
)

if __name__ == "__main__":
    setup(**setup_args)
