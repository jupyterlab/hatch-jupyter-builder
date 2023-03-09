import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--migration-tests",
        default=False,
        type=bool,
        help="only run tests with the 'migration_test' pytest mark.",
    )


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "migration_test")


def pytest_runtest_setup(item):
    is_migration_test = any(mark for mark in item.iter_markers(name="migration_test"))

    if item.config.getoption("--migration-tests") is True:
        if not is_migration_test:
            pytest.skip("Only running tests marked as 'migration_test'.")
    elif is_migration_test:
        pytest.skip(
            "Skipping this test because it's marked 'migration_test'. Run integration tests using the `--migration-tests` flag."
        )
