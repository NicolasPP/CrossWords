import math
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
BOARD_PADDING: int = 6
TITLE_FONT_SIZE: int = 30
DATE_FONT_SIZE: int = 15


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


@dataclass(slots=True)
class MetadataDisplay:
    placement: Rect
    surface: Surface

    title: Surface
    date: Surface


class BoardDisplay(NamedTuple):
    placement: Rect
    surface: Surface


class CrossWords:

    def __init__(self, puzzle: Puzzle) -> None:
        self._state: CrossWordState = CrossWordState(puzzle)
        self._font_name: str = get_fonts()[0]

        self._cells: list[CellDisplay] = self._create_cells_display()
        self._board: BoardDisplay = self._create_board_display()
        self._clues: MetadataDisplay = self._create_metadata_display()

    def process_input(self, event: Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos: Vector2 = self._get_board_mouse_pos()
            for cell in self._cells:
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
                self._cells[index].state = CellState.CORRECT

            else:
                self._cells[index].state = CellState.WRONG

    def _move_selected(self, direction: SelectionDirection) -> None:
        # FIXME:  Moving down does wrap around.
        if self._state.selected is None:
            return

        jump_size: int = 1 if direction is SelectionDirection.RIGHT else self._state.puzzle.cols
        next_selected: int = self._state.selected + jump_size

        def is_next_invalid() -> bool:
            return next_selected >= len(self._cells)

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

        cell: CellDisplay = self._cells[self._state.selected]
        if cell.state is CellState.CORRECT:
            return

        cell.state = CellState.EMPTY if value == EMPTY_CELL else CellState.FILLED
        self._state.values[self._state.selected] = value

    def update(self, delta_time: float) -> None:
        pass

    def _create_metadata_display(self) -> MetadataDisplay:
        padding: Vector2 = Vector2(self._board.placement.topleft)
        top_left: Vector2 = Vector2(self._board.placement.topright)
        top_left.x += padding.x

        window_rect: Rect = pygame.display.get_surface().get_rect()
        width: int = window_rect.width - top_left.x - padding.x
        height: int = window_rect.height - padding.y * 2
        surface: Surface = Surface((width, height))
        surface.fill("white")

        title_font_size: int = get_desired_font_size(self._font_name, self._state.puzzle.title,
                                                     math.floor(width * 0.7))
        title_font: Font = SysFont(self._font_name, title_font_size)
        title: Surface = title_font.render(self._state.puzzle.title, True, "black", "white")

        date_font_size: int = get_desired_font_size(self._font_name, self._state.puzzle.date,
                                                    math.floor(width * 0.2))
        date_font: Font = SysFont(self._font_name, date_font_size)
        date: Surface = date_font.render(self._state.puzzle.date, True, "black", "white")

        title_placement: Rect = title.get_rect(midtop=(width // 2, padding.y))
        surface.blit(title, title_placement)

        date_placement: Rect = date.get_rect(midtop=title_placement.midbottom)
        date_placement.y += padding.y
        surface.blit(date, date_placement)

        return MetadataDisplay(surface.get_rect(topleft=top_left), surface, title, date)

    def _create_cells_display(self) -> list[CellDisplay]:
        cells: list[CellDisplay] = []
        rows: int = self._state.puzzle.rows
        cols: int = self._state.puzzle.cols

        cell_size: Vector2 = CellDisplay.get_size(self._state.puzzle)
        for row, col in product(range(rows), range(cols)):
            cell: CellDisplay = CellDisplay(
                Vector2(col, row),
                cell_size,
                (row * cols + col),
            )
            font: Font = SysFont(self._font_name, CLUE_ID_FONT_SIZE)
            cell.draw(self._state, font)
            cells.append(cell)

        return cells

    def _create_board_display(self) -> BoardDisplay:
        window_rect: Rect = pygame.display.get_surface().get_rect()
        min_size: int = min(window_rect.width, window_rect.height) - BOARD_PADDING * 2
        dimensions: Vector2 = Vector2(
            self._state.puzzle.rows,
            self._state.puzzle.cols,
        )
        cell_size: Vector2 = CellDisplay.get_size(self._state.puzzle)
        board_size: Vector2 = cell_size * dimensions.elementwise()
        surface: Surface = Surface(board_size)
        left_over: float = min_size - board_size.x
        placement: Rect = surface.get_rect(topleft=Vector2(BOARD_PADDING + left_over // 2))
        return BoardDisplay(placement, surface)

    def _render_cell(self, cell: CellDisplay, font: Font) -> None:

        if self._state.values[cell.index] == VOID_CELL:
            return

        self._board.surface.blit(cell.surface, cell.placement)

        #  Rendering user placed value
        if (value := self._state.values[cell.index]) not in [EMPTY_CELL, VOID_CELL]:
            # FIXME: Probably not a good idea to render value every frame. Do it once when it changes.
            color: str = "blue" if cell.state is CellState.CORRECT else "black"
            value_sign: Surface = font.render(value, True, color, "white")
            self._board.surface.blit(value_sign, value_sign.get_rect(center=cell.placement.center))

        if cell.state is CellState.WRONG:
            pad: Vector2 = Vector2(WRONG_PAD)
            pygame.draw.line(self._board.surface, "red", Vector2(cell.placement.topleft) + pad,
                             Vector2(cell.placement.topleft) + Vector2(cell.surface.get_size()) - pad, 3)

        #  Rendering hover surface
        if cell.index == self._state.selected:
            self._board.surface.blit(cell.hover, cell.placement)

    def _get_board_mouse_pos(self) -> Vector2:
        return Vector2(pygame.mouse.get_pos()) - Vector2(self._board.placement.topleft)

    def render(self) -> None:
        font: Font = SysFont(self._font_name, VALUE_FONT_SIZE)
        for cell in self._cells:
            self._render_cell(cell, font)

        pygame.display.get_surface().blit(self._clues.surface, self._clues.placement)
        pygame.display.get_surface().blit(self._board.surface, self._board.placement)


def get_desired_font_size(font_name: str, text: str, desired_width: int) -> Optional[int]:
    font_size: int = 1
    font: Font = SysFont(font_name, font_size)

    def get_render_size() -> Vector2:
        return Vector2(font.size(text))

    render_size: Vector2 = get_render_size()

    while render_size.x < desired_width:
        font_size += 1

        font = SysFont(font_name, font_size)
        render_size = get_render_size()

    return font_size
