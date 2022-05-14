# hatch-jupyter-builder

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-jupyter-builder.svg)](https://pypi.org/project/hatch-jupyter-builder)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-jupyter-builder.svg)](https://pypi.org/project/hatch-jupyter-builder)

---

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [Configuration](#license)

## Installation

```console
pip install hatch-jupyter-builder
```

## License

`hatch-jupyter` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Configuration

```toml
[tool.hatch.build.targets.wheel.hooks.jupyter]
dependencies = ["hatch-jupyter-builder"]
build_function = "hatch_jupyter_builder.npm_builder"
ensured_targets = ["foo/generated.txt"]

[tool.hatch.build.targets.wheel.hooks.jupyter_builder.build_kwargs]
build_cmd = "build:src"
```
