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


def test_combined_tables():
    tA = tables.RollTable(fixture_combined_A)
    tB = tables.RollTable(fixture_combined_B)

    combined = tables.CombinedTable(tables=[tA, tB], die=6)
    assert 'A1' in str(combined)
    assert 'B1' in str(combined)


def test_table_end_to_end():
    assert str(tables.RollTable(fixture_source))


def test_table_end_to_end_with_metadata():
    assert str(tables.RollTable(fixture_metadata + fixture_source))


def test_table_frequency():
    t = tables.RollTable(fixture_metadata + fixture_source, frequency='nondefault')
    assert t.frequencies['Option 1'] == 0.0
    assert t.frequencies['Option 2'] == 0.1
    assert t.frequencies['Option 3'] == 0.9


def test_one_option():
    t = tables.RollTable(fixture_one_choice, die=1)
    assert t.values == [('option 1', {'choice 1': 'description 1'})]


def test_collapsed():
    t = tables.RollTable(fixture_repeated_choices, die=6, collapsed=True)
    assert len(list(t.rows)) == 1


def test_not_collapsed():
    t = tables.RollTable(fixture_repeated_choices, die=6, collapsed=False)
    assert len(list(t.rows)) == 6


def test_no_descriptions():
    t = tables.RollTable(fixture_no_descriptions, die=1)
    assert 'd1' in str(t)
    assert 'option 1' in str(t)
