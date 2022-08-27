# hatch-jupyter-builder

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-jupyter-builder.svg)](https://pypi.org/project/hatch-jupyter-builder)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-jupyter-builder.svg)](https://pypi.org/project/hatch-jupyter-builder)

---

This provides a [build hook](https://hatch.pypa.io/latest/config/build/#build-hooks) plugin for [Hatch](https://github.com/pypa/hatch) that adds a build step for use with Jupyter packages.

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [Usage and Configuration](#usage_and_configuration)
- [Local Development](#local_development)

## Installation

```console
pip install hatch-jupyter-builder
```

## Local Development

To test this package locally with another package, use the following:

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder@file://<path_to_this_repo>"]
```

## Migration

This library can be used to migrate from a `setuptools` based package to
use `hatch_jupyter_builder`. It will attempt to migrate `jupyter-packaging`
config as well, if present.

To migrate, run the following:

```bash
python -m hatch_jupyter_builder.migrate .
```

The migration script will do most of the migration automatically, but
will prompt you for anything it cannot do itself.

To compare dist files with a reference checkout, run the following:

```bash
python -m hatch_jupyter_builder.compare_migration <source_dir> <target_dir> sdist
```

Use `wheel` to compare wheel file contents.

See the [documentation for more information on migration](https://hatch-jupyter-builder.readthedocs.io/en/latest/source/how_to_guides/index.html).

## License

`hatch-jupyter-builder` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
