from dataclasses import dataclass
from typing import Optional

from puzzle_reader import EMPTY_CELL, Puzzle, VOID_CELL


@dataclass(slots=True, init=False)
class CrossWordState:
    puzzle: Puzzle
    values: list[str]
    locked_in: list[bool]
    selected: Optional[int]
    selected_across: Optional[int]
    selected_down: Optional[int]

    def __init__(self, puzzle: Puzzle) -> None:
        self.puzzle = puzzle
        self.values = [VOID_CELL if cell == VOID_CELL else EMPTY_CELL
                       for cell in puzzle.answers.completed]
        self.locked_in = [False] * (puzzle.rows * puzzle.cols)
        self.selected = None
        self.selected_across = None
        self.selected_down = None
