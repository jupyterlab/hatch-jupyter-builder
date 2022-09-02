# Migrating Python Projects that used Data Files

For existing projects that used `setuptools` and optionally the
`get_data_files()` function from `jupyter_packaging`, we offer a migration
script that will convert your project to use `hatchling`.
These projects can include Jupyter Kernels or Jupyter Server Extensions
that ship with `data_files`.

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

If there are things that are found that cannot be automatically
migrated, a warning will print at the end of the migration script.
Typically this will be a notice to put the actual version string
in your `_version.py` file.

The migration assumes that you will be using [`tbump`](https://github.com/your-tools/tbump) to manage versions.
`tbump` is a project that is used by many of the core Jupyter projects
to maintain version for a project. For example, if you have a `_version.py`
and a `package.json` file that are meant to share a version, `tbump`
can handle keeping them in sync.

If some other custom logic that was in your `setup.py`, you may need
to include a `hatch_build.py` file, similar to the one used by [`ipykernel`](https://github.com/ipython/ipykernel/blob/main/hatch_build.py). You will need to add a [custom metadata hook](https://hatch.pypa.io/latest/plugins/metadata-hook/custom/#custom-metadata-hook) as well.

As an additional assurance, you can compare the files produced by the
migrated configuration to those you previously produced.

To do this, clone your repository to another folder, and run the following:

```bash
python -m hatch_jupyter_builder.compare_migrated . <clean-checkout-path> wheel
```

This will build the wheel in both directories and compare their contents.
You can repeat the process with the `sdist` option as well.

For some other examples of migrated packages, see

- [ipyparallel](https://github.com/ipython/ipyparallel/blob/main/pyproject.toml) (includes a `hatch_build.py` file with a custom script to provide a Lab and Notebook extension)

- [jupyter-server-terminals](https://github.com/jupyter-server/jupyter_server_terminals/blob/main/pyproject.toml) - a Jupyter Server extension

- [jupyter_client](https://github.com/jupyter/jupyter_client/blob/main/pyproject.toml) (regular python package with no `shared-data`)
