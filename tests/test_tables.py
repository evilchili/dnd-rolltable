import pytest

from rolltable import tables


@pytest.mark.parametrize('table, expected', [
    (tables.wild_magic, ['A third eye', 'Advantage on perception checks']),
    (tables.trinkets, ['ivory mimic']),
    (tables.psychadelic_effects, ['Cosmic', 'mind expands', 'it will become so']),
    (tables.encounters, ['None', 'Easy', 'Difficult', 'Dangerous', 'Deadly'])
])
def test_flat(table, expected):
    table.die = 1000
    assert 'd1000' in str(table)
    for txt in expected:
        assert txt in str(table)


def test_encounter_frequencies():
    table = tables.encounters


def test_markdown():
    tables.trinkets.die = 1
    md = tables.trinkets.as_markdown()
    assert '| Roll | Trinket ' in md
    assert '| ---- |' in md
    assert 'd1' in md
