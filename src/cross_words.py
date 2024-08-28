from dataclasses import dataclass
from enum import Enum, auto
from itertools import product
from typing import NamedTuple, Optional

import pygame
from pygame.event import Event
from pygame.font import Font, SysFont, get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from puzzle_reader import EMPTY_CELL, Puzzle, VOID_CELL

PADDING: int = 2
HOVER_ALPHA: int = 50
WRONG_PAD: int = 7
VALUE_FONT_SIZE: int = 20
CLUE_ID_FONT_SIZE: int = 10


class SelectionDirection(Enum):
    RIGHT = auto()
    DOWN = auto()


class CellState(Enum):
    EMPTY = auto()
    FILLED = auto()
    CORRECT = auto()
    WRONG = auto()


@dataclass(slots=True, init=False)
class CrossWordState:
    puzzle: Puzzle
    values: list[str]
    locked_in: list[bool]
    selected: Optional[int]

    def __init__(self, puzzle: Puzzle) -> None:
        self.puzzle = puzzle
        self.values = [VOID_CELL if cell == VOID_CELL else EMPTY_CELL
                       for cell in puzzle.answers.completed]
        self.locked_in = [False] * (puzzle.rows * puzzle.cols)
        self.selected = None


@dataclass(slots=True, init=False)
class CellDisplay:
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


class BoardDisplay(NamedTuple):
    placement: Rect
    surface: Surface
    grid: list[CellDisplay]


class CrossWords:

    def __init__(self, puzzle: Puzzle) -> None:
        self._state: CrossWordState = CrossWordState(puzzle)
        self._font_name: str = get_fonts()[0]

        self._display: BoardDisplay = self._create_display()

    def process_input(self, event: Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos: Vector2 = self._get_board_mouse_pos()
            for cell in self._display.grid:
                if cell.placement.collidepoint(mouse_pos):
                    if self._state.values[cell.index] == VOID_CELL:
                        return

                    cell_clues = self._state.puzzle.clues.by_index[cell.index]
                    print(cell_clues, cell.index, sep=", ")

                    if cell_clues.across is not None:
                        print("Across: ", self._state.puzzle.clues.across[cell_clues.across])
                        # print("Answer: ", self._state.puzzle.answers.across[cell_clues.across])

                    if cell_clues.down is not None:
                        print("Down: ", self._state.puzzle.clues.down[cell_clues.down])
                        # print("Answer: ", self._state.puzzle.answers.down[cell_clues.down])

                    if event.button == 3:
                        print("Across Answer: ", self._state.puzzle.answers.across[cell_clues.across])
                        print("Down Answer: ", self._state.puzzle.answers.down[cell_clues.down])

                    print("----------------------------")
                    self._state.selected = cell.index

        if event.type == pygame.KEYDOWN:

            if event.unicode.isalpha():
                self._set_selected_value(event.unicode.upper())
                self._move_selected(SelectionDirection.RIGHT)

            elif event.key == pygame.K_BACKSPACE:
                self._set_selected_value(EMPTY_CELL)

            elif event.key == pygame.K_SPACE:
                self._check_puzzle()

    def _check_puzzle(self) -> None:
        for index, value in enumerate(self._state.values):
            if value == VOID_CELL:
                continue

            if value == EMPTY_CELL:
                continue

            if value == self._state.puzzle.answers.completed[index]:
                self._display.grid[index].state = CellState.CORRECT

            else:
                self._display.grid[index].state = CellState.WRONG

    def _move_selected(self, direction: SelectionDirection) -> None:
        # FIXME:  Moving down does wrap around.
        if self._state.selected is None:
            return

        jump_size: int = 1 if direction is SelectionDirection.RIGHT else self._state.puzzle.cols
        next_selected: int = self._state.selected + jump_size

        def is_next_invalid() -> bool:
            return next_selected >= len(self._display.grid)

        if is_next_invalid():
            self._state.selected = None
            return

        if self._state.values[next_selected] == VOID_CELL:

            # move until it's not VOID_CELL
            while self._state.values[next_selected] == VOID_CELL:
                next_selected += jump_size

            if is_next_invalid():
                self._state.selected = None
                return

        self._state.selected = next_selected

    def _set_selected_value(self, value: str) -> None:
        if self._state.selected is None:
            return

        cell: CellDisplay = self._display.grid[self._state.selected]
        if cell.state is CellState.CORRECT:
            return

        cell.state = CellState.EMPTY if value == EMPTY_CELL else CellState.FILLED
        self._state.values[self._state.selected] = value

    def update(self, delta_time: float) -> None:
        pass

    def _create_display(self) -> BoardDisplay:
        grid: list[CellDisplay] = []

        window_rect: Rect = pygame.display.get_surface().get_rect()
        min_size: int = min(window_rect.width, window_rect.height)

        dimensions: Vector2 = Vector2(
            self._state.puzzle.rows,
            self._state.puzzle.cols,
        )

        cell_size: Vector2 = Vector2(min_size) // dimensions.elementwise()
        for row, col in product(range(int(dimensions.x)), range(int(dimensions.y))):
            cell: CellDisplay = CellDisplay(
                Vector2(col, row),
                cell_size,
                (row * int(dimensions.y) + col),
            )
            font: Font = SysFont(self._font_name, CLUE_ID_FONT_SIZE)
            cell.draw(self._state, font)
            grid.append(cell)

        surface: Surface = Surface(cell_size * dimensions.elementwise())
        placement: Rect = surface.get_rect(center=pygame.display.get_surface().get_rect().center)

        return BoardDisplay(placement, surface, grid)

    def _render_cell(self, cell: CellDisplay, font: Font) -> None:

        if self._state.values[cell.index] == VOID_CELL:
            return

        self._display.surface.blit(cell.surface, cell.placement)

        #  Rendering user placed value
        if (value := self._state.values[cell.index]) not in [EMPTY_CELL, VOID_CELL]:
            # FIXME: Probably not a good idea to render value every frame. Do it once when it changes.
            color: str = "blue" if cell.state is CellState.CORRECT else "black"
            value_sign: Surface = font.render(value, True, color, "white")
            self._display.surface.blit(value_sign, value_sign.get_rect(center=cell.placement.center))

        if cell.state is CellState.WRONG:
            pad: Vector2 = Vector2(WRONG_PAD)
            pygame.draw.line(self._display.surface, "red", Vector2(cell.placement.topleft) + pad,
                             Vector2(cell.placement.topleft) + Vector2(cell.surface.get_size()) - pad, 3)

        #  Rendering hover surface
        if cell.index == self._state.selected:
            self._display.surface.blit(cell.hover, cell.placement)

    def _get_board_mouse_pos(self) -> Vector2:
        return Vector2(pygame.mouse.get_pos()) - Vector2(self._display.placement.topleft)

    def render(self) -> None:
        font: Font = SysFont(self._font_name, VALUE_FONT_SIZE)
        for cell in self._display.grid:
            self._render_cell(cell, font)

        pygame.display.get_surface().blit(self._display.surface, self._display.placement)
