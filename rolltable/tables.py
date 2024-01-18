from pathlib import Path
from rolltable.types import RollTable
from typing import Any


def from_sources(names: list[str] = []) -> list:
    return RollTable([
        (Path(__file__).parent / "sources" / name).read_text()
        for name in names
    ])


index = dict(
    psychadelic_effects=from_sources(['psychadelic_effects.yaml']),
    trinkets=from_sources(['trinkets.yaml']),
    wild_magic=from_sources(['wild_magic.yaml']),
    spells=from_sources(['spells.yaml'])
)


def __getattr__(name: str) -> Any:
    return index[name]
