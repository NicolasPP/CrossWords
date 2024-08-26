import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple, Optional

from config import DATA_PATH

VOID_CELL: str = "."
EMPTY_CELL: str = ""


@dataclass(slots=True)
class CellClue:
    across: Optional[int] = None
    down: Optional[int] = None


class Clues(NamedTuple):
    across: dict[int, str]
    down: dict[int, str]
    by_index: dict[int, CellClue]
    grid: list[int]


class Answers(NamedTuple):
    across: dict[int, str]
    down: dict[int, str]
    completed: list[str]


class Board(NamedTuple):
    state: list[str]
    rows: int
    cols: int


class Puzzle(NamedTuple):
    board: Board
    answers: Answers
    clues: Clues


def create_puzzle(puzzle_data: dict[str, Any]) -> Puzzle:
    board: Board = Board(
        [cell if cell == VOID_CELL else EMPTY_CELL for cell in puzzle_data["grid"]],
        puzzle_data["size"]["rows"],
        puzzle_data["size"]["cols"],
    )

    answers_across: dict[int, str] = {}
    clues_across: dict[int, str] = {}
    assert len(puzzle_data["answers"]["across"]) == len(puzzle_data["clues"]["across"])
    for clue_across, answer_across in zip(puzzle_data["clues"]["across"], puzzle_data["answers"]["across"]):
        id_, _ = clue_across.split(".", maxsplit=1)
        clues_across[int(id_)] = clue_across
        answers_across[int(id_)] = answer_across

    answers_down: dict[int, str] = {}
    clues_down: dict[int, str] = {}
    assert len(puzzle_data["answers"]["down"]) == len(puzzle_data["clues"]["down"])
    for clue_down, answer_down in zip(puzzle_data["clues"]["down"], puzzle_data["answers"]["down"]):
        id_, _ = clue_down.split(".", maxsplit=1)
        clues_down[int(id_)] = clue_down
        answers_down[int(id_)] = answer_down

    by_index: dict[int, CellClue] = {_: CellClue() for _ in range(board.cols * board.rows)}
    for index, val in enumerate(puzzle_data["gridnums"]):
        if val == 0:
            continue

        if val in clues_across:
            next_index: int = index
            while not board.state[next_index]:

                by_index[next_index].across = val
                next_index += 1

                if next_index >= board.cols * board.rows:
                    break

        if val in clues_down:
            next_index: int = index
            while not board.state[next_index]:

                by_index[next_index].down = val
                next_index += board.cols

                if next_index >= board.cols * board.rows:
                    break

    answers: Answers = Answers(
        answers_across,
        answers_down,
        puzzle_data["grid"]
    )

    clues: Clues = Clues(
        clues_across,
        clues_down,
        by_index,
        puzzle_data["gridnums"]
    )

    return Puzzle(board, answers, clues)


def read_puzzle() -> Puzzle:
    path: Path = Path(DATA_PATH)

    if not path.exists():
        raise ValueError(f"Data Path does not exist {path.absolute()}")

    with open(path / "01.json", "r") as puzzle_file:
        puzzle_data: dict[str, Any] = json.load(puzzle_file)

    return create_puzzle(puzzle_data)
