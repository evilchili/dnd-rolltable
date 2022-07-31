# RollTables

RollTables is a python library for generating tables suitable for selecting random options using dice rolls.

## Quick Start

```
# example.yaml

# metadata is optional
metadata:
  # headers are optional
  headers:
    # The first column header always applies to the frequency label;
    # you can hide this (or any other column) by setting the header to null
    - Rarity  
    - Color      
    - Notes
  # frequencies are optional; by default distribution will be uniform
  frequencies:
    # multiple distributions may be specified besides 'default'
    default:
      - common:  0.5
      - uncommon: 0.3
      - rare: 0.15
      - wondrous: 0.05
# 'common' is the text label for the frequency distribution
common:
  # each time a 'common' value is selected for the table, it will be
  # chosen at random from the following values
  - red
  - orange
  - yellow
uncommon:
  - green
  - blue
rare:
  - indigo
  - violet
wondrous:
  # choices can be definitions; both key and the value will be added as columns
  - octarine: the color of magic
```
    
```
% poetry run roll-table example.yaml
┏━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Roll    ┃ Rarity   ┃ Color    ┃ Notes              ┃
┡━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ d1-d5   │ common   │ red      │                    │
│ d6-d10  │ common   │ yellow   │                    │
│ d11-d12 │ rare     │ indigo   │                    │
│ d13     │ rare     │ violet   │                    │
│ d14-d15 │ uncommon │ blue     │                    │
│ d16-d19 │ uncommon │ green    │                    │
│ d20     │ wondrous │ octarine │ the color of magic │
└─────────┴──────────┴──────────┴────────────────────┘
```

### Library Use
 
```
from rolltable import tables

sources = [
    Path('spells.yaml').read_text(),
    Path('weapons.yaml').read_text(),
    Path('items.yaml').read_text()
]
rt = tables.RollTable(sources, die=100)
```
