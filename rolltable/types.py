import yaml
from csv2md.table import Table
from collections.abc import Iterable
from typing import Optional, List, Union
from random_sets.datasources import DataSource

import rich.table


class RollTable:
    """
    Generate a roll table using weighted distributions of random options.

    Instance Attributes:

    sources         - One or more yaml strings to parse as data sources
    frequency       - The frequency distribution to apply when populating the table
    die             - The size of the die for which to create a table (default: 20)
    headers         - An array of header strings
    rows            - An array of table headers and rows
    expanded_rows   - An array of table headers and rows, one per die roll value

    Usage:

        table = RollTable(['source.yaml'], die=4)
        print(table)
        >>> Roll    Item
            d1      Foo
            d2-d4   Bar
    """

    def __init__(self, sources: Union[List[str], List[DataSource]], frequency: str = 'default',
                 die: Optional[int] = 20, hide_rolls: bool = False) -> None:
        self._sources = sources
        self._frequency = frequency
        self.die = die
        self.hide_rolls = hide_rolls
        self.data = None
        self._rows = None
        self._headers = None
        self._header_excludes = None
        self._generated_values = None
        self._config()

    @property
    def datasources(self) -> List:
        return self._data

    @property
    def headers(self) -> List:
        return self._headers

    @property
    def _values(self) -> List:
        """
            For each data source, select N random values, where N is the size of the die.
            we then zip those random values so that each member of the generated list
            contains one value from each data source. So if _data is:

            [
               ['axe', 'shortsword', 'dagger'],
               ['fire', 'ice', 'poison'],
            ]

            and the die is 2, the resulting generated values might be:

            [
              ['axe', 'fire'],
              ['dagger', 'ice'],
            ]
        """
        if not self._generated_values:
            self._generated_values = list(zip(*[
                t.random_values(self.die) for t in self._data
            ]))
        return self._generated_values

    @property
    def rows(self) -> List:
        def formatted(lastrow, offset, row, i):
            thisrow = [f'd{i}' if offset + 1 == i else f'd{offset+1}-d{i}']
            thisrow += self._flatten(lastrow)
            return self._column_filter(thisrow)

        lastrow = None
        offset = 0
        self._rows = [self._column_filter(['Roll'] + self.headers)]

        for face in range(self.die):
            row = self._values[face]
            if not lastrow:
                lastrow = row
                offset = face
                continue
            if row != lastrow:
                self._rows.append(formatted(lastrow, offset, row, face))
                lastrow = row
                offset = face
        self._rows.append(formatted(lastrow, offset, row, face+1))
        return self._rows

    @property
    def expanded_rows(self) -> List:
        self._rows = [self._column_filter(['Roll'] + self.headers)]
        for face in range(self.die):
            row = self._values[face]
            self._rows.append(self._column_filter([f'd{face+1}'] + row))
        return self._rows

    def reset(self) -> None:
        self._generated_values = None

    def as_markdown(self) -> str:
        return Table(self.rows).markdown()

    def as_yaml(self, expanded: bool = False) -> dict:
        struct = {}
        for row in self.rows[1:]:
            struct[row[0]] = {}
            # pad rows with empty cols as necessary
            cols = row[1:] + [''] * (len(self.headers) - len(row[1:]))
            for idx, col in enumerate(cols):
                struct[row[0]][self.headers[idx] if idx < len(self.headers) else '_'] = col
        return yaml.dump(struct, sort_keys=False)

    def as_table(self, width: int = 120, expanded: bool = False) -> str:
        rows = self.expanded_rows if expanded else self.rows
        table = rich.table.Table(*rows[0], width=width)
        for row in rows[1:]:
            table.add_row(*row)
        return table

    def set_headers(self, *headers) -> None:
        self._headers = list(headers)

        # identify which columns to hide in the output by recording where a
        # None header appears
        self._header_excludes = []
        for i in range(len(self._headers)):
            if self.headers[i] is None:
                self._header_excludes.append(i+1)

    def _config(self):
        """
        Parse data sources, generate headers, and create the column filters
        """

        # create the datasource objects
        self._data = []
        for src in self._sources:
            if type(src) is str:
                src = [src]
            for one_source in src:
                ds = DataSource(one_source, frequency=self._frequency)
                ds.load_source()
                self._data.append(ds)

        # merge the headers
        headers = []
        for ds in self._data:
            headers += ds.headers
        self.set_headers(*headers)

    def _column_filter(self, row):
        cols = [col or '' for (pos, col) in enumerate(row) if pos not in self._header_excludes]
        # pad the row with empty columns if there are more headers than columns
        cols = cols + [''] * (1 + len(self.headers) - len(row))
        # strip the leading column if we're hiding the dice rolls
        return cols[1:] if self.hide_rolls else cols

    def _flatten(self, obj: List) -> List:
        for member in obj:
            if isinstance(member, Iterable) and not isinstance(member, (str, bytes)):
                yield from self._flatten(member)
            else:
                yield member

    def __repr__(self) -> str:
        rows = list(self.rows)
        str_format = '\t'.join(['{:10s}'] * len(rows[0]))
        return "\n".join([str_format.format(*[r or '' for r in row]) for row in rows])
