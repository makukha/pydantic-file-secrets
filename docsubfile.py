import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Self
from unittest import TestCase

import bracex
from docsub import click
from doctestcase import to_markdown
from importloc import Location, get_subclasses, random_name
from tabulate import tabulate


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


@dataclass
class TestResult:
    envname: str  # tox env name
    frag: tuple[str, ...]  # mapping of fragment prefixes to suffixes
    marks: set[str]  # pass marks

    @classmethod
    def from_tox_env(
        cls,
        envdir: Path,
        fragment_groups: list[list[str]],
        fragment_sep: str = '-',
        passmark_prefix: str = '.pass-',
    ) -> Self | None:
        # parse fragments
        fragments = set(envdir.name.split(fragment_sep))
        if len(fragments) != len(fragment_groups):
            return None
        frag = []
        for g in fragment_groups:
            match = fragments & set(g)
            if len(match) != 1:
                return None
            frag.append(match.pop())
        # load pass marks
        marks = set()
        for markfile in envdir.glob(f'{passmark_prefix}*'):
            marks.add(markfile.name.removeprefix(passmark_prefix))
        #
        return cls(envname=envdir.name, frag=tuple(frag), marks=marks)


@x.command()
@click.argument('toxdir', type=click.Path(file_okay=False, path_type=Path))
@click.option('-f', '--fragments', type=str)
@click.option('-i', '--icons', type=str)
def testres(toxdir: Path, fragments: str, icons: str) -> None:
    """
    Print matrix of tox test results.
    """
    if not toxdir.exists():
        raise ValueError('Test results are not available.')
    fgroup = [list(reversed(bracex.expand(g))) for g in fragments.split(';')]
    if len(fgroup) > 2:
        raise ValueError('Maximum 2 fragments are allowed')
    markicons = json.loads(icons)

    # load results
    results: list[TestResult] = []
    for toxenv in toxdir.iterdir():
        if not toxenv.is_dir():
            continue
        res = TestResult.from_tox_env(toxenv, fragment_groups=fgroup)
        if res is not None:
            results.append(res)

    # print matrix

    failicon = next(iter(markicons.values()))

    def result_icon(res: TestResult, default=failicon) -> str | None:
        for mark, icon in reversed(markicons.items()):
            if mark in res.marks:
                return icon
        return default

    headers = ['', *fgroup[1]]
    body = []
    for row in fgroup[0]:
        res = [r for r in results if r.frag[0] == row]
        res.sort(key=lambda r: fgroup[1].index(r.frag[1]))
        body.append([row, *(result_icon(r) for r in res)])
    table = tabulate(
        tabular_data=body,
        headers=headers,
        tablefmt='github',
        colalign=['left'] + ['center'] * len(fgroup[1]),
        maxcolwidths=[max(len(c) for c in fgroup[0]) + 2, *(len(c) for c in fgroup[1])],
    )

    click.echo(table)
