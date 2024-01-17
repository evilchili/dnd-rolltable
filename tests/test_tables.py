import pytest

from pathlib import Path
from rolltable.types import RollTable


sources = Path(__file__).parent / '..' / 'rolltable' / 'sources'

flat_list = (sources / 'trinkets.yaml').read_text()
dict_of_dicts = (sources / 'wild_magic.yaml').read_text()
dict_of_lists = (sources / 'psychadelic_effects.yaml').read_text()


@pytest.mark.parametrize('data, expected', [
    ([dict_of_dicts], ['d1000 ', 'A third eye', 'Advantage on perception checks']),
    ([flat_list], ['d1000 ', 'ivory mimic']),
    ([dict_of_lists], ['d1000', 'Cosmic', 'mind expands', 'it will become so']),
])
def test_flat(data, expected):
    rt = RollTable(data, die=1000)
    for txt in expected:
        assert txt in str(rt)
