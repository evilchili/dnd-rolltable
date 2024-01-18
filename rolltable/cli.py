from rolltable.types import RollTable
from rolltable import tables
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


def make_callback(roll_table_instance):
    def inner():
        print(roll_table_instance.as_table())
    return inner


# step through all the predfined tables and create a cli for each
for name, table in tables.index.items():
    help_text = name.replace('_', ' ').title()
    app.command(name=name, help=f"Create a roll table of {help_text}")(
        make_callback(table)
    )


if __name__ == '__main__':
    app()
