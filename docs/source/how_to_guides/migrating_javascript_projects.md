# Migrating Python Projects that used JavaScript

For existing projects that shipped with JavaScript, which includes
Jupyter Lab Extensions, Jupyter Widgets, and Jupyter Notebook Extensions,
we provide a script to help automate the process.

Create a new branch for your migration and run the following:

```bash
pip install hatch_jupyter_builder
python -m hatch_jupyter_builder.migrate .
```

The migration script will do its best to convert metadata
from `setup.py` and `setup.cfg` into appropriate modernized
`pyproject.toml` metadata. Much of the migration is done by
`hatch` itself, including the mapping of `data-files` configuration
to [`shared-data`](https://hatch.pypa.io/latest/plugins/builder/wheel/#options).

If the package was using `jupyter_packaging`, we also provide
appropriate `hatch_jupyter_builder` config.

If there are things that are found that cannot be automatically
migrated, a warning will print at the end of the migration script.
Typically this will be a notice to put the actual version string
in your `_version.py` file.

The migration assumes that you will be using [`tbump`](https://github.com/your-tools/tbump) to manage versions.
`tbump` is a project that is used by many of the core Jupyter projects
to maintain version for a project. For example, if you have a `_version.py`
and a `package.json` file that are meant to share a version, `tbump`
can handle keeping them in sync.

The configuration and behavior of the `npm_builder` helper function is
similar to the one provided by `jupyter_packaging`.

As an additional assurance, you can compare the files produced by the
migrated configuration to those you previously produced.

To do this, clone your repository to another folder, and run the following:

```bash
python -m hatch_jupyter_builder.compare_migrated . <clean-checkout-path> wheel
```

This will build the wheel in both directories and compare their contents.
You can repeat the process with the `sdist` option as well.

For some examples of migrated packages that provide JavaScript, see:

- [notebook](https://github.com/jupyter/notebook/blob/main/pyproject.toml) (JupyterLab and Server Extensions)
- [jupyter_server](https://github.com/jupyter-server/jupyter_server/blob/main/pyproject.toml) (build step to include CSS for default pages).
