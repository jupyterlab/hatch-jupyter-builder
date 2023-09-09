# Configuration

The [build hook plugin](https://hatch.pypa.io/latest/plugins/build-hook/) name is `jupyter-builder`. The minimal set of options is:

- **_pyproject.toml_**

  ```toml
  [tool.hatch.build.hooks.jupyter-builder]
  dependencies = ["hatch-jupyter-builder"]
  build-function = "hatch_jupyter_builder.npm_builder"
  ```

Or with all options given:

- **_pyproject.toml_**

  ```toml
    [tool.hatch.build.hooks.jupyter-builder]
    dependencies = ["hatch-jupyter-builder"]
    build-function = "hatch_jupyter_builder.npm_builder"
    ensured-targets = ["foo/generated.txt"]
    skip-if-exists = ["foo/generated.txt"]
    install-pre-commit-hook = true
    optional-editable-build = true

    [tool.hatch.build.hooks.jupyter-builder.build-kwargs]
    build_cmd = "build:src"

    [tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
    build_cmd = "build"
  ```

## Options

### build-function

The build function is defined as an importable string with a module and a function name, separated by a period. The function must accept a
`target_name` (either "wheel" or "sdist"), and a `version` (either "standard" or "editable") as its only positional arguments. E.g.

- **_builder.py_**

  ```python
  def build_func(target_name, version):
      ...
  ```

Would be defined as `build-function = "builder.build_func"`

### ensured-targets

The optional `ensured-targets` is a list of expected file paths after building a
"standard" version sdist or wheel.

### skip-if-exists

The optional `skip-if-exists` is a list of paths whose presence would cause
the build step to be skipped. This option is ignored in `editable` mode.
The `ensured-targets` will still be checked, if given.

### build-kwargs

The optional `build-kwargs` is a set of keyword arguments to pass to the build
function.

### editable-build-kwargs

You can also use `editable-build-kwargs` if the parameters should differ
in editable mode. If only the build command is different, you can use
`editable_build_cmd` in `build-kwargs` instead.

### optional-editable-build

The optional `optional-editable-build` parameter can be set to `true` to
show a warning instead of erroring if the build fails in editable mode.
This can be used when build artifacts are optional for local development.

### install-pre-commit-hook

The optional `install-pre-commit-hook` boolean causes a `pre-commit` hook to be installed during an editable install.

## Npm Builder Function

This library provides a convenenice `npm_builder` function which can be
used to build `npm` assets as part of the build. See the :ref:`npm_builder_function` for more information on usage.
