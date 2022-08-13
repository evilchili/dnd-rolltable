from rolltable import tables

fixture_metadata = """
metadata:
  headers:
    - Header 1
    - Header 2
    - Header 3
  die: 10
  frequencies:
    default:
      Option 1: 0.3
      Option 2: 0.5
      Option 3: 0.2
    nondefault:
      Option 1: 0.0
      Option 2: 0.1
      Option 3: 0.9
"""

fixture_source = """
Option 1:
    - choice 1: description 1
    - choice 2: description 2
    - choice 3: description 3
Option 2:
    - choice 1: description 4
    - choice 2: description 5
    - choice 3: description 6
Option 3:
    - choice 1: description 7
    - choice 2: description 8
    - choice 3: description 9
"""

fixture_one_choice = """
option 1:
    -  choice 1: description 1
"""

fixture_repeated_choices = """
option 1:
  - choice 1: description 1
  - choice 1: description 1
  - choice 1: description 1
"""

fixture_no_descriptions = """
metadata:
    headers:
        - option
        - choice
option 1:
    -  choice 1
"""

fixture_combined_A = """
A1:
  - A choice 1
  - A choice 2
  - A choice 3
A2:
  - A choice 4
  - A choice 5
  - A choice 6
A3:
  - A choice 7
  - A choice 8
  - A choice 9
"""

fixture_combined_B = """
metadata:
    headers:
        - HeaderB
        - HeaderB_Choice
B1:
  - B choice 1
B2:
  - B choice 2
B3:
  - B choice 3
"""

fixture_no_options = """
metadata:
    headers:
        - headerA
        - headerB
B1:
B2:
B3:
"""

fixture_lists = """
#
# one  two  three  four
# foo  bar  baz    quz
#
metadata:
  headers:
    - one
    - two
    - three
    - four
foo:
  - bar:
    - baz
    - quz
"""


def test_lists():
    t = tables.RollTable([fixture_lists], die=1)
    assert str(t)


def test_combined_tables():
    combined = tables.RollTable([fixture_combined_A, fixture_combined_B], die=6)
    assert str(combined)


def test_table_end_to_end():
    assert str(tables.RollTable([fixture_source]))


def test_table_end_to_end_with_metadata():
    assert str(tables.RollTable([fixture_metadata + fixture_source]))


def test_table_frequency():
    t = tables.RollTable([fixture_metadata + fixture_source], frequency='nondefault')
    assert t._data[0].frequencies['Option 1'] == 0.0
    assert t._data[0].frequencies['Option 2'] == 0.1
    assert t._data[0].frequencies['Option 3'] == 0.9


def test_one_option():
    t = tables.RollTable([fixture_one_choice], die=1)
    assert t._values == [['option 1', 'choice 1', 'description 1']]


def test_collapsed():
    t = tables.RollTable([fixture_repeated_choices], die=6)
    assert len(list(t.rows)) == 2  # (+1 for headers)


def test_not_collapsed():
    t = tables.RollTable([fixture_repeated_choices], die=6)
    assert len(list(t.expanded_rows)) == 7  # (+1 for headers)


def test_no_descriptions():
    t = tables.RollTable([fixture_no_descriptions], die=1)
    assert 'd1' in str(t)
    assert 'option 1' in str(t)


def test_no_options():
    t = tables.RollTable([fixture_no_options])
    assert str(t)


def test_yaml():
    assert tables.RollTable([fixture_no_options]).as_yaml()
    assert tables.RollTable([fixture_one_choice]).as_yaml()
    assert tables.RollTable([fixture_metadata + fixture_source]).as_yaml()
    assert tables.RollTable([fixture_source]).as_yaml()
