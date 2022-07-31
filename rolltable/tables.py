import yaml
import random
from collections.abc import Generator
from typing import Optional, Mapping, List, IO


class RollTable:
    """
    Generate a roll table using weighted distributions of random options.

    Instance Attributes:

    data        - The parsed source data, minus any metadata
    die         - the size of the die for which to create a table (default: 20)
    frequencies - frequency distribution applied when selecting random values
    headers     - array of column headers (default: do not print headers)
                  (default: uniform across all options)
    rows        - An array of table rows derived from the values
    values      - An array of randomly-selected values for each die roll

    Instance Methods:

    load_source - Read and parse the source. Will be called automatically when necessary.
    """

    def __init__(self, source: IO, frequency: str = 'default',
                 die: Optional[int] = 20, collapsed: bool = True):
        """
        Initialize a RollTable instance.

        Args:
            source      - an IO object to read source from
            frequency   - the name of the frequency distribution to use; must
                          be defined in the source file's metadata.
            die         - specify a die size
            collapsed   - If True, collapse multiple die values with the same
                          options into a single line.
        """
        self._frequency = frequency
        self._die = die
        self._collapsed = collapsed
        self._headers = None
        self._frequencies = None
        self._source = source
        self._data = None
        self._values = None
        self._rows = None

    @property
    def frequencies(self):
        if not self._data:
            self.load_source()
        return self._frequencies

    @property
    def data(self) -> Mapping:
        if not self._data:
            self.load_source()
        return self._data

    @property
    def die(self) -> int:
        return self._die

    @property
    def headers(self) -> List:
        if not self._data:
            self.load_source()
        return self._headers

    @property
    def values(self) -> List:
        if not self._values:
            weights = []
            options = []
            for (option, weight) in self.frequencies.items():
                weights.append(weight)
                options.append(option)
            freqs = random.choices(options, weights=weights, k=self.die)
            self._values = []
            for option in freqs:
                self._values += [(option, random.choice(self.data[option]))]
            if hasattr(self._values[0][1], 'keys'):
                self._values = sorted(self._values, key=lambda val: list(val[1].keys())[0])
            else:
                self._values = sorted(self._values)
        return self._values

    @property
    def rows(self) -> List:
        if not self._rows:
            rows = []
            if self.headers:
                rows.append(['Roll'] + self.headers)
            if self._collapsed:
                for line in self._collapsed_rows():
                    rows.append(line)
            else:
                for (i, item) in enumerate(self.values):
                    (cat, option) = item
                    if hasattr(option, 'items'):
                        (k, v) = list(option.items())[0]
                        rows.append([f'd{i+1}', cat, k, v])
                    else:
                        rows.append([f'd{i+1}', cat, option])
            self._rows = rows
        return self._rows

    def load_source(self) -> None:
        """
        Cache the yaml source and the parsed or generated metadata.
        """
        if self._data:
            return

        self._data = yaml.safe_load(self._source)
        metadata = self._data.pop('metadata', {})

        num_keys = len(self._data.keys())
        default_freq = num_keys / 100

        if 'headers' in metadata:
            self._headers = metadata['headers']

        frequencies = {
            'default': dict([(k, default_freq) for k in self._data.keys()])
        }
        if 'frequencies' in metadata:
            frequencies.update(**metadata['frequencies'])
        self._frequencies = frequencies[self._frequency]

    def _collapsed_rows(self) -> Generator[list]:
        """
        Generate an array of column values for each row of the table but
        sort the values and squash multiple rows with the same values into one,
        with a range for the die roll instead of a single die. That is,

            d1 foo bar baz
            d2 foo bar baz

        becomes

            d1-d2 foo bar baz
        """
        def collapsed(last_val, offset, val, i):
            (cat, option) = last_val
            if hasattr(option, 'items'):
                (k, v) = list(*option.items())
            else:
                k = option
                v = ''
            if offset + 1 == i:
                return [f'd{i}', cat, k, v]
            else:
                return [f'd{offset+1}-d{i}', cat, k, v]

        last_val = None
        offset = 0
        for (i, val) in enumerate(self.values):
            if not last_val:
                last_val = val
                offset = i
                continue
            if val != last_val:
                yield collapsed(last_val, offset, val, i)
                last_val = val
                offset = i
        yield collapsed(last_val, offset, val, i+1)

    def __repr__(self) -> str:
        """
        Return the rows as a single string.
        """
        rows = list(self.rows)
        str_format = '\t'.join(['{:10s}'] * len(rows[0]))
        return "\n".join([str_format.format(*row) for row in rows])


class CombinedTable(RollTable):
    """
    Create a table that is a union of other tables.
    """

    def __init__(self, tables: List[str], die: Optional[int] = 20):
        self._die = die
        self._tables = tables
        self._rows = None
        self._headers = None

        # reset any cached values
        for t in self._tables:
            t._rows = None
            t._values = None
            t._collapsed = False
            t._die = self._die

    @property
    def tables(self) -> List:
        return self._tables

    @property
    def rows(self) -> List:
        """
        Compute the rows of the table by concatenating the rows of the individual tables.
        """
        if not self._rows:

            # if one table has headers, they must all have them, so fill with empty strings.
            if sum([1 for t in self.tables if t.headers]) < len(self.tables):
                for t in self.tables:
                    if not t.headers:
                        t._headers = ['.'] * len(t.values[0])

            self._rows = []
            for i in range(self._die):
                row = [self.tables[0].rows[i][0]]
                for x in range(len(self.tables)):
                    for col in self.tables[x].rows[i][1:]:
                        row.append(col)
                self._rows.append(row)
        return self._rows


if __name__ == '__main__':
    import sys
    print(RollTable(path=sys.argv[1], die=int(sys.argv[2])))
