import json
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Iterator,
    NamedTuple,
    Optional,
)

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
    rows: int
    cols: int


class Puzzle(NamedTuple):
    title: str
    date: str
    rows: int
    cols: int
    answers: Answers
    clues: Clues


def create_puzzle(puzzle_data: dict[str, Any]) -> Optional[Puzzle]:
    rows: int = int(puzzle_data["size"]["rows"])
    cols: int = int(puzzle_data["size"]["cols"])

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

    state: list[str] = [cell if cell == VOID_CELL else EMPTY_CELL for cell in puzzle_data["grid"]]
    by_index: dict[int, CellClue] = {_: CellClue() for _ in range(cols * rows)}
    for index, val in enumerate(puzzle_data["gridnums"]):
        if val == 0:
            continue

        if val in clues_across:
            next_index: int = index
            while not state[next_index]:

                by_index[next_index].across = val
                next_index += 1

                if next_index >= cols * rows:
                    break

        if val in clues_down:
            next_index: int = index
            while not state[next_index]:

                by_index[next_index].down = val
                next_index += cols

                if next_index >= cols * rows:
                    break

    for index, cell in enumerate(state):
        if cell == VOID_CELL:
            continue

        if by_index[index].across is None or by_index[index].down is None:
            # FIXME: this will usually mean some edge case I will not add support for ;)
            #        e.g when there are words in NULL_CELLS https://www.xwordinfo.com/Crossword?date=12/1/2013&g=48&d=A
            #        puzzle: 2013-12-1
            return None

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

    return Puzzle(
        puzzle_data["title"],
        puzzle_data["date"],
        rows,
        cols,
        answers,
        clues
    )


def puzzles() -> Iterator[Puzzle]:
    path: Path = Path(DATA_PATH)
    if not path.exists():
        raise ValueError(f"Data Path does not exist {path.absolute()}")

    for month in path.iterdir():
        if not month.is_dir():
            continue

        for day in month.iterdir():
            if day.is_dir():
                continue

            with open(day.absolute(), "r") as puzzle_file:
                puzzle_data: dict[str, Any] = json.load(puzzle_file)

            puzzle: Optional[Puzzle] = create_puzzle(puzzle_data)
            if puzzle is None:
                continue

            yield puzzle


def get_that_one() -> Puzzle:
    # path: Path = Path("data/2013/06/16.json")
    path: Path = Path("data/2013/01/17.json")
    # path: Path = Path("data/2013/12/01.json")
    # path: Path = Path("data/2013/08/29.json")
    with open(path.absolute(), "r") as puzzle_file:
        puzzle_data: dict[str, Any] = json.load(puzzle_file)

    return create_puzzle(puzzle_data)
