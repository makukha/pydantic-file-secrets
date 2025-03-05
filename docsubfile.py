import re
from unittest import TestCase

from docsub import click
from doctestcase import to_markdown
from importloc import Location, get_subclasses, random_name


@click.group()
def x() -> None:
    pass


@x.command()
@click.argument('testpath', type=click.Path(exists=True, dir_okay=False))
@click.argument('nameregex')
def cases(testpath: click.Path, nameregex: str) -> None:
    """
    Print usage section based on test case docstrings.
    """
    cases = get_subclasses(Location(str(testpath)).load(random_name), TestCase)
    cases.sort(key=lambda c: c.__firstlineno__)  # type: ignore[attr-defined]
    for case in cases:
        if re.fullmatch(nameregex, case.__name__):
            click.echo(to_markdown(case, include_title=False))


@x.command()
@click.argument('obj', type=str)
def dirtree(obj: str) -> None:
    """
    Print directory tree from Dir object.
    """
    tree = Location(obj).load(on_conflict='reuse')
    tree.print_rich(hide_root=True)
