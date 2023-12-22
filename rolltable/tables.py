import yaml
import random
from csv2md.table import Table
from collections.abc import Iterable
from typing import Optional, List, IO, Union


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
        self.metadata = None
        self.load_source()

    def load_source(self) -> None:
        """
        Cache the yaml source and the parsed or generated metadata.
        """
        if self.data:
            return
        self.read_source()
        self.init_headers()
        self.init_frequencies()

    def read_source(self) -> None:
        self.data = yaml.safe_load(self.source)
        self.metadata = self.data.pop('metadata', {})

    def init_headers(self) -> None:
        if 'headers' in self.metadata:
            self.headers = self.metadata['headers']

    def init_frequencies(self) -> None:
        num_keys = len(self.data.keys())
        default_freq = num_keys / 100

        frequencies = {
            'default': dict([(k, default_freq) for k in self.data.keys()])
        }
        if 'frequencies' in self.metadata:
            frequencies.update(**self.metadata['frequencies'])
        self.frequencies = frequencies[self.frequency]

    def random_frequencies(self, count: int = 1) -> list:
        """
        Choose random option names from the frequency table.
        """
        weights = []
        options = []
        for (option, weight) in self.frequencies.items():
            weights.append(weight)
            options.append(option)
        return random.choices(options, weights=weights, k=count)

    def random_values(self, count: int = 1) -> list:
        """
        Return a list of random values from the data set, as a list of lists.
        """
        return [
            self.get_entries(option, rand=True) for option in self.random_frequencies(count)
        ]

    def get_entries(self, option, rand: bool = True) -> list:
        """
        For a random item or each item in the specified option in the data source,
        return a flattened list of the option, the select item, and the item's value (if any).
        """

        # If there is no data for the specified option, stop now.
        flattened = [option]
        if not self.data[option]:
            return flattened

        if hasattr(self.data[option], 'keys'):
            # if the option is a dict, we assume the values are lists; we select a random item
            # and prepend the key to the value list as our random selection. For example, given:
            #
            #  >>> self.data[option] == {'One': ['bar', 'baz'], 'Two': ['qaz', 'qux']}
            #
            # choices might then be: ['One', 'bar', 'baz']
            #
            if rand:
                k, v = random.choice(list(self.data[option].items()))
                choices = [[k] + v]
            else:
                choices = [
                    [k] + v for k, v in list(self.data[option].items())
                ]
        else:
            # If the option is either a list or a string, just select it.
            if rand:
                choices = [random.choice(self.data[option])]
            else:
                choices = self.data[option]

        for choice in choices:
            # If the randomly-selected choice is a dict, choose a random item and return a list consisting
            # of the option name, the key, and the value, flattening the # value if it is also a list.
            if hasattr(choice, 'keys'):
                for (k, v) in choice.items():
                    if type(v) is list:
                        flattened.extend([k, *v])
                    else:
                        flattened.extend([k, v])
                continue

            # if the member is a list, return the flattened list
            if type(choice) is list:
                flattened.extend(choice)
                continue

            # otherwise, return a list consisting of option and choice
            flattened.append(choice)
        return flattened

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
        self._die = die
        self._hide_rolls = hide_rolls
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
        return yaml.dump(struct, sort_keys=False)

    @property
    def datasources(self) -> List:
        return self._data

    @property
    def die(self) -> int:
        return self._die

    @property
    def headers(self) -> List:
        return self._headers

    @property
    def _values(self) -> List:
        if not self._generated_values:
            ds_values = [t.random_values(self.die) for t in self._data]
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
        return Table(self.rows).markdown()

    def _config(self):
        """
        Parse data sources, generate headers, and create the column filters
        """

        # create the datasource objects
        self._data = []
        for src in self._sources:
            if type(src) is str:
                ds = DataSource(src, frequency=self._frequency)
                ds.load_source()
                self._data.append(ds)
            else:
                self._data.append(src)

        # merge the headers
        self._headers = []
        for ds in self._data:
            self._headers += ds.headers

        # identify which columsn to hide in the output by recording where a
        # None header appears
        self._header_excludes = []
        for i in range(len(self._headers)):
            if self.headers[i] is None:
                self._header_excludes.append(i)

    def _column_filter(self, row):
        cols = [col or '' for (pos, col) in enumerate(row) if pos not in self._header_excludes]
        # pad the row with empty columns if there are more headers than columns
        cols = cols + [''] * (1 + len(self.headers) - len(row))
        # strip the leading column if we're hiding the dice rolls
        return cols[1:] if self._hide_rolls else cols

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
