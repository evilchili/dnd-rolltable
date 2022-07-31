# RollTables

RollTables is a python library for generating tables suitable for selecting random options using dice rolls.

## Quick Start

Clone the repo and install the virtual env:
```
% git clone https://github.com/evilchili/dnd-rolltable
% cd dnd-rolltable
% poetry install
```

Invoke the CLI:
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
