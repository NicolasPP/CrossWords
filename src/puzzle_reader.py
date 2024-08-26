import json
from pathlib import Path
from typing import Any

from config import DATA_PATH


def read_puzzle() -> dict[str, Any]:
    path: Path = Path(DATA_PATH)

    if not path.exists():
        raise ValueError(f"Data Path does not exist {path.absolute()}")

    with open(path / "01.json", "r") as puzzle_file:
        puzzle: dict[str, Any] = json.load(puzzle_file)

        for field in list(puzzle):
            if puzzle[field] is None:
                del puzzle[field]

    return puzzle
