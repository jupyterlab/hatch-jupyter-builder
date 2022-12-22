"""The cli implementation for hatch_jupyter_builder."""
import argparse
import sys
from typing import Optional

from .compare_migrated import cli as compare_cli
from .migrate import cli as migrate_cli


def make_parser(
    parser: Optional[argparse.ArgumentParser] = None, prog: Optional[str] = None
) -> argparse.ArgumentParser:
    """Make an arg parser."""
    if parser is None:
        parser = argparse.ArgumentParser(prog=prog)
    parsers = parser.add_subparsers()

    migrate_parser = parsers.add_parser("migrate")
    migrate_cli.make_parser(migrate_parser)
    migrate_parser.set_defaults(func=migrate_cli.run)

    compare_parser = parsers.add_parser("compare-migrated")
    compare_cli.make_parser(compare_parser)
    compare_parser.set_defaults(func=compare_cli.run)

    return parser


def run(args: Optional[argparse.Namespace] = None) -> None:
    """Run the main script."""
    if args is None:
        prog = (
            f"{sys.executable} -m hatch_jupyter_builder"
            if sys.argv[0].endswith("__main__.py")
            else None
        )
        parser = make_parser(prog=prog)
        args = parser.parse_args()
    args.func()
