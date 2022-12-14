import yaml
import random
from collections.abc import Iterable
from typing import Optional, List, IO


class DataSource:
    """
    Represents a yaml data source used to generate roll tables.

    Attributes:

        source      - the IO source to parse
        frequency   - the frequency distribution to apply
        headers     - an array of header strings
        data        - The parsed YAML data

    Methods:

        load_source - Read and parse the source, populating the attributes

    """
    def __init__(self, source: IO, frequency: str = 'default') -> None:
        """
        Initialize a DataSource instance.

        Args:
            source      - an IO object to read source from
            frequency   - the name of the frequency distribution to use; must
                          be defined in the source file's metadata.
        """
        self.source = source
        self.frequency = frequency
        self.headers = []
        self.frequencies = None
        self.data = None
        self.load_source()

    def load_source(self) -> None:
        """
        Cache the yaml source and the parsed or generated metadata.
        """
        if self.data:
            return

        self.data = yaml.safe_load(self.source)
        metadata = self.data.pop('metadata', {})

        num_keys = len(self.data.keys())
        default_freq = num_keys / 100

        if 'headers' in metadata:
            self.headers = metadata['headers']

        frequencies = {
            'default': dict([(k, default_freq) for k in self.data.keys()])
        }
        if 'frequencies' in metadata:
            frequencies.update(**metadata['frequencies'])
        self.frequencies = frequencies[self.frequency]


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

    def __init__(self, sources: List[str], frequency: str = 'default',
                 die: Optional[int] = 20) -> None:
        self._sources = sources
        self._frequency = frequency
        self._die = die
        self._data = None
        self._rows = None
        self._headers = None
        self._header_excludes = None
        self._generated_values = None
        self._config()

    def as_yaml(self, expanded=False) -> dict:
        struct = {}
        for row in self.rows[1:]:
            struct[row[0]] = {}
            # pad rows with empty cols as necessary
            cols = row[1:] + [''] * (len(self.headers) - len(row[1:]))
            for idx, col in enumerate(cols):
                struct[row[0]][self.headers[idx] if idx < len(self.headers) else '_'] = col
        return yaml.dump(struct)

    @property
    def die(self) -> int:
        return self._die

    @property
    def headers(self) -> List:
        return self._headers

    @property
    def _values(self) -> List:
        if not self._generated_values:
            def values_from_datasource(ds):
                weights = []
                options = []
                for (option, weight) in ds.frequencies.items():
                    weights.append(weight)
                    options.append(option)
                freqs = random.choices(options, weights=weights, k=self.die)
                values = []
                for option in freqs:
                    if not ds.data[option]:
                        values.append([option])
                        continue
                    choice = random.choice(ds.data[option])
                    if hasattr(choice, 'keys'):
                        c = [option]
                        for (k, v) in choice.items():
                            c.extend([k, v])
                        values.append(c)
                    else:
                        values.append([option, choice])
                return sorted(values)

            ds_values = [values_from_datasource(t) for t in self._data]

            self._generated_values = []
            for face in range(self._die):
                value = []
                for index, ds in enumerate(ds_values):
                    value += ds_values[index][face]
                self._generated_values.append(value)
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
        for face in range(self._die):
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
        for face in range(self._die):
            row = self._values[face]
            self._rows.append(self._column_filter([f'd{face+1}'] + row))
        return self._rows

    @property
    def as_markdown(self) -> str:
        return ''

    def _config(self):
        """
        Parse data sources, generate headers, and create the column filters
        """

        # create the datasource objects
        self._data = []
        for src in self._sources:
            ds = DataSource(src, frequency=self._frequency)
            ds.load_source()
            self._data.append(ds)

        # merge the headers
        self._headers = []
        for ds in self._data:
            self._headers += ds.headers

        # identify which columsn to hide in the output by recording where a
        # None header appears
        self._header_excludes = []
        for i in range(len(self._headers)):
            if self.headers[i] is None:
                self._header_excludes.append(i+1)  # +1 to account for the 'Roll' column

    def _column_filter(self, row):
        cols = [col for (pos, col) in enumerate(row) if pos not in self._header_excludes]
        # pad the row with empty columns if there are more headers than columns
        return cols + [''] * (1 + len(self.headers) - len(row))

    def _flatten(self, obj: List) -> List:
        for member in obj:
            if isinstance(member, Iterable) and not isinstance(member, (str, bytes)):
                yield from self._flatten(member)
            else:
                yield member

    def __repr__(self) -> str:
        rows = list(self.rows)
        print(rows)
        str_format = '\t'.join(['{:10s}'] * len(rows[0]))
        return "\n".join([str_format.format(*row) for row in rows])
