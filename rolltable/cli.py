from rolltable import tables
import typer
from rich import print
from rich.table import Table


app = typer.Typer()


@app.command("roll-table")
def create(
    source: str = typer.Argument(
        ...,
        help="Path to the yaml-formatted source file."),
    frequency: str = typer.Option(
        'default',
        help='use the specified frequency from the source file'),
    die: int = typer.Option(
        20,
        help='The size of the die for which to create a table'),
    collapse: bool = typer.Option(
        True,
        help='If True, collapse multiple die values with the same option.')
):
    """
    CLI for creating roll tables.
    """
    with open(source, 'r') as src:
        rt = tables.RollTable(source=src, frequency=frequency, die=die,
                              collapsed=collapse)
        rt.load_source()
    table = Table(*rt.rows[0])
    for row in rt.rows[1:]:
        table.add_row(*row)
    print(table)


if __name__ == '__main__':
    app()
