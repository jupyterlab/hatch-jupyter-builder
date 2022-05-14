# hatch-jupyter-builder

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-jupyter-builder.svg)](https://pypi.org/project/hatch-jupyter-builder)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-jupyter-builder.svg)](https://pypi.org/project/hatch-jupyter-builder)

---

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [Usage and Configuration](#usage_and_configuration)

## Installation

```console
pip install hatch-jupyter-builder
```

## License

`hatch-jupyter` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Usage and Configuration

```toml
[tool.hatch.build.targets.wheel.hooks.jupyter]
dependencies = ["hatch-jupyter-builder"]
build_function = "hatch_jupyter_builder.npm_builder"
ensured_targets = ["foo/generated.txt"]

[tool.hatch.build.targets.wheel.hooks.jupyter_builder.build_kwargs]
build_cmd = "build:src"
```

The only required fields are `dependencies` and `build_function`.
The build function is defined as an importable string with a module and a function name, separated by a dot. The function must accept a
`target_name` (either "wheel" or "sdist"), and a `version` (either "standard" or "editable") as its only positional arguments.

The optional `ensured_targets` is a list of expected files after the build.

The optional `build_kwargs` is a set of keyword arguments to pass to the build
function.

This library provides a convenenice `npm_builder` function which can be
used to build `npm` assets as part of the build.
