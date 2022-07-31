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

### Command-Line Help
```
% poetry run roll-table --help

 Usage: roll-table [OPTIONS] SOURCES...

 CLI for creating roll tables.

╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    sources      SOURCES...  Path to one or more yaml-formatted source file. [default: None] [required]          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --frequency                               TEXT                             use the specified frequency from the   │
│                                                                            source file                            │
│                                                                            [default: default]                     │
│ --die                                     INTEGER                          The size of the die for which to       │
│                                                                            create a table                         │
│                                                                            [default: 20]                          │
│ --collapsed             --no-collapsed                                     If True, collapse multiple die values  │
│                                                                            with the same option.                  │
│                                                                            [default: collapsed]                   │
│ --install-completion                      [bash|zsh|fish|powershell|pwsh]  Install completion for the specified   │
│                                                                            shell.                                 │
│                                                                            [default: None]                        │
│ --show-completion                         [bash|zsh|fish|powershell|pwsh]  Show completion for the specified      │
│                                                                            shell, to copy it or customize the     │
│                                                                            installation.                          │
│                                                                            [default: None]                        │
│ --help                                                                     Show this message and exit.            │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
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
