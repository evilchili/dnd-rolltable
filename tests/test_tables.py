import pytest

from rolltable import tables


@pytest.mark.parametrize('table, expected', [
    (tables.wild_magic, ['d1000 ', 'A third eye', 'Advantage on perception checks']),
    (tables.trinkets, ['d1000 ', 'ivory mimic']),
    (tables.psychadelic_effects, ['d1000', 'Cosmic', 'mind expands', 'it will become so']),
])
def test_flat(table, expected):
    table.die = 1000
    for txt in expected:
        assert txt in str(table)
