from rolltable import tables
import typer
from rich import print
from rich.table import Table
from pathlib import Path
from typing import List


app = typer.Typer()


@app.command("roll-table")
def create(
    sources: List[Path] = typer.Argument(
        ...,
        help="Path to one or more yaml-formatted source file."),
    frequency: str = typer.Option(
        'default',
        help='use the specified frequency from the source file'),
    die: int = typer.Option(
        20,
        help='The size of the die for which to create a table'),
    collapsed: bool = typer.Option(
        True,
        help='If True, collapse multiple die values with the same option.'),
    yaml: bool = typer.Option(
        False,
        help='Render output as yaml.')
):
    """
    CLI for creating roll tables.
    """

    rt = tables.RollTable([Path(s).read_text() for s in sources], frequency=frequency, die=die)

    if yaml:
        print(rt.as_yaml)
        return

    rows = rt.rows if collapsed else rt.expanded_rows
    table = Table(*rows[0])
    for row in rows[1:]:
        table.add_row(*row)
    print(table)


if __name__ == '__main__':
    app()
