from dataclasses import dataclass
from enum import Enum, auto

import pygame
from pygame.font import Font
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from config import BOARD_PADDING, HOVER_ALPHA, PADDING
from cross_word_state import CrossWordState
from puzzle_reader import Puzzle, VOID_CELL


class CellState(Enum):
    EMPTY = auto()
    FILLED = auto()
    CORRECT = auto()
    WRONG = auto()


@dataclass(slots=True, init=False)
class CellDisplay:

    @staticmethod
    def get_size(puzzle: Puzzle) -> Vector2:
        window_rect: Rect = pygame.display.get_surface().get_rect()
        min_size: int = min(window_rect.width, window_rect.height) - BOARD_PADDING * 2
        dimensions: Vector2 = Vector2(puzzle.rows, puzzle.cols)
        return Vector2(min_size) // dimensions.elementwise()

    placement: Rect
    surface: Surface
    hover: Surface
    index: int
    state: CellState

    def __init__(self, position: Vector2, size: Vector2, index: int) -> None:
        self.placement = Rect(*(position.elementwise() * size).xy, *size.xy)
        self.surface = Surface(size)
        self.hover = Surface(size)
        self.index = index
        self.state = CellState.EMPTY

        self.hover.fill("black")
        self.hover.set_alpha(HOVER_ALPHA)

    def draw(self, state: CrossWordState, font: Font) -> None:

        size: Vector2 = Vector2(self.surface.get_size())
        padding: Vector2 = Vector2(PADDING)
        content: Surface = Surface(size - padding)

        if state.values[self.index] == VOID_CELL:
            self.surface.fill("black")
            return

        content.fill("white")

        clue_number: int = state.puzzle.clues.grid[self.index]
        if clue_number != 0:
            clue_sign: Surface = font.render(
                str(clue_number),
                True,
                "black",
                "white"
            )
            content.blit(clue_sign, padding)

        self.surface.blit(content, content.get_rect(center=self.surface.get_rect().center))
