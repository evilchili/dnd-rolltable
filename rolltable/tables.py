from pathlib import Path
from typing import Any

from rolltable.types import RollTable


def from_sources(names: list[str] = []) -> list:
    return RollTable([(Path(__file__).parent / "sources" / name).read_text() for name in names])


index = dict(
    psychadelic_effects=from_sources(["psychadelic_effects.yaml"]),
    trinkets=from_sources(["trinkets.yaml"]),
    wild_magic=from_sources(["wild_magic.yaml"]),
    spells=from_sources(["spells.yaml"]),
    encounters=from_sources(["encounters.yaml"]),
)


def __getattr__(name: str) -> Any:
    try:
        return index[name]
    except KeyError:
        if name in globals():
            return globals()[name]
        raise AttributeError(f"No such attribute: {name}")
