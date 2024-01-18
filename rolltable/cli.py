from rolltable.types import RollTable
import typer
from enum import Enum
from rich import print
from pathlib import Path
from typing import List


app = typer.Typer()


class OUTPUT_FORMATS(Enum):
    text = 'text'
    yaml = 'yaml'
    markdown = 'markdown'


@app.command("psychadelic-effects")
def psycheffects():
    """
    Generate a roll table of psychadelic effects.
    """
    rt = RollTable([(Path(__file__).parent / 'sources' / 'psychadelic_effects.yaml').read_text()])
    print(rt.as_table())


@app.command("trinkets")
def trinkets():
    """
    Generate a roll table of random junk.
    """
    rt = RollTable([(Path(__file__).parent / 'sources' / 'trinkets.yaml').read_text()])
    print(rt.as_table())


@app.command("wild-magic")
def wildmagic():
    """
    Generate a wild magic surge table.
    """
    rt = RollTable([(Path(__file__).parent / 'sources' / 'wild_magic.yaml').read_text()])
    print(rt.as_table())


@app.command("spells")
def spells():
    """
    Generate a random spell table.
    """
    rt = RollTable([(Path(__file__).parent / 'sources' / 'spells.yaml').read_text()])
    rt.set_headers('Level', 'Name', 'School', None, None, None, None, None)
    print(rt.as_table())


@app.command("custom")
def custom(
    sources: List[Path] = typer.Argument(
        ...,
        help="Path to one or more yaml-formatted source file."),
    frequency: str = typer.Option(
        'default',
        help='use the specified frequency from the source file'),
    die: int = typer.Option(
        20,
        help='The size of the die for which to create a table'),
    hide_rolls: bool = typer.Option(
        False,
        help='If True, do not show the Roll column.',
    ),
    collapsed: bool = typer.Option(
        True,
        help='If True, collapse multiple die values with the same option.'),
    width: int = typer.Option(
        120,
        help='Width of the table.'),
    output: OUTPUT_FORMATS = typer.Option(
        'text',
        help='The output format to use.',
    )
):
    """
    Create roll tables from custom sources.
    """

    rt = RollTable([Path(s).read_text() for s in sources], frequency=frequency, die=die, hide_rolls=hide_rolls)

    if output == OUTPUT_FORMATS.yaml:
        print(rt.as_yaml())
    elif output == OUTPUT_FORMATS.markdown:
        print(rt.as_markdown())
    else:
        print(rt.as_table(width=width, expanded=not collapsed))


if __name__ == '__main__':
    app()
