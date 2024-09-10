from enum import Enum, auto
from itertools import product

import pygame
from pygame.event import Event
from pygame.font import Font, SysFont, get_fonts
from pygame.math import Vector2
from pygame.surface import Surface

from config import CLUE_ID_FONT_SIZE, VALUE_FONT_SIZE, WRONG_PAD
from cross_word_state import CrossWordState
from display_board import BoardDisplay
from display_cell import CellDisplay, CellState
from display_metadata import MetadataDisplay
from puzzle_reader import EMPTY_CELL, Puzzle, VOID_CELL


class SelectionDirection(Enum):
    RIGHT = auto()
    DOWN = auto()


class CrossWords:

    def __init__(self, puzzle: Puzzle) -> None:
        self._state: CrossWordState = CrossWordState(puzzle)
        self._font_name: str = get_fonts()[0]

        self._board: BoardDisplay = BoardDisplay(self._state, CellDisplay.get_size(self._state.puzzle))
        self._metadata: MetadataDisplay = MetadataDisplay(self._board.placement, self._state)

        self._cells: list[CellDisplay] = []
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
            self._cells.append(cell)

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
        # TODO: dont create a font every iteration
        font: Font = SysFont(self._font_name, VALUE_FONT_SIZE)
        for cell in self._cells:
            self._render_cell(cell, font)

        self._metadata.render()

        pygame.display.get_surface().blit(self._metadata.surface, self._metadata.placement)
        pygame.display.get_surface().blit(self._board.surface, self._board.placement)
