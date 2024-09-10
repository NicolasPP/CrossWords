from enum import Enum, auto
from itertools import product
from typing import Optional

import pygame
from pygame import mouse
from pygame.event import Event
from pygame.font import Font, SysFont, get_fonts
from pygame.math import Vector2
from pygame.surface import Surface

from config import CLUE_ID_FONT_SIZE, VALUE_FONT_SIZE, WRONG_PAD
from cross_word_state import CrossWordState
from display_board import BoardDisplay
from display_cell import CellDisplay, CellState
from display_metadata import MetadataDisplay, ScrollDirection
from puzzle_reader import CellClue, EMPTY_CELL, Puzzle, VOID_CELL


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

    def _process_metadata_click(self, event: Event) -> None:
        mouse_pos: Vector2 = Vector2(pygame.mouse.get_pos()) - Vector2(self._metadata.placement.topleft)
        if not self._metadata.clues_display.placement.collidepoint(mouse_pos):
            return

        scroll_direction: Optional[ScrollDirection] = None
        if event.button == 5:
            scroll_direction = ScrollDirection.DOWN

        elif event.button == 4:
            scroll_direction = ScrollDirection.UP

        mouse_pos -= self._metadata.clues_display.placement.topleft
        if scroll_direction is not None:
            if self._metadata.clues_display.across.window_placement.collidepoint(mouse_pos):
                self._metadata.clues_display.across.scroll(scroll_direction)

            if self._metadata.clues_display.down.window_placement.collidepoint(mouse_pos):
                self._metadata.clues_display.down.scroll(scroll_direction)
            return

        if (across_clue := self._metadata.clues_display.across.get_collided(mouse_pos)) is not None:
            self._metadata.clues_display.set_selected(across_clue)

        if (down_clue := self._metadata.clues_display.down.get_collided(mouse_pos)) is not None:
            self._metadata.clues_display.set_selected(down_clue)

    def _process_board_click(self, event: Event) -> None:
        mouse_pos: Vector2 = Vector2(pygame.mouse.get_pos()) - Vector2(self._board.placement.topleft)
        for cell in self._cells:
            if cell.placement.collidepoint(mouse_pos):
                if self._state.values[cell.index] == VOID_CELL:
                    return

                if self._state.selected == cell.index:
                    if self._state.selected_down is not None:
                        self._set_selected(cell.index, SelectionDirection.RIGHT)

                    elif self._state.selected_across is not None:
                        self._set_selected(cell.index, SelectionDirection.DOWN)

                else:
                    self._set_selected(cell.index, SelectionDirection.RIGHT)

    def process_input(self, event: Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos: Vector2 = Vector2(mouse.get_pos())
            if self._board.placement.collidepoint(mouse_pos):
                self._process_board_click(event)

            if self._metadata.placement.collidepoint(mouse_pos):
                self._process_metadata_click(event)

        if event.type == pygame.KEYDOWN:

            if event.unicode.isalpha():
                self._set_selected_value(event.unicode.upper())
                self._move_selected()

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

    def _move_selected(self) -> None:
        if self._state.selected is None:
            return

        direction: SelectionDirection = SelectionDirection.RIGHT
        if self._state.selected_down is not None:
            direction = SelectionDirection.DOWN

        jump_size: int = 1 if direction is SelectionDirection.RIGHT else self._state.puzzle.cols
        next_selected: int = self._state.selected + jump_size

        def is_next_invalid() -> bool:
            return next_selected >= len(self._cells)

        if is_next_invalid():
            self._set_selected(None, direction)
            return

        if (self._state.selected + 1) % self._state.puzzle.cols == 0:
            self._set_selected(None, direction)
            return

        if self._state.values[next_selected] == VOID_CELL:
            self._set_selected(None, direction)
            return

        self._set_selected(next_selected, direction)

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

        # Rendering selected clue
        cell_clue: CellClue = self._state.puzzle.clues.by_index[cell.index]
        if self._state.selected_down is not None and cell_clue.down == self._state.selected_down:
            self._board.surface.blit(cell.hover, cell.placement)

        if self._state.selected_across is not None and cell_clue.across == self._state.selected_across:
            self._board.surface.blit(cell.hover, cell.placement)

        # Rendering hover surface
        if cell.index == self._state.selected:
            self._board.surface.blit(cell.hover, cell.placement)

    def _set_selected(self, cell_index: Optional[int], direction: SelectionDirection) -> None:
        self._state.selected = cell_index
        self._state.selected_down = None
        self._state.selected_across = None

        if cell_index is None:
            return

        if direction is SelectionDirection.RIGHT:
            self._state.selected_across = self._state.puzzle.clues.by_index[self._state.selected].across

        elif direction is SelectionDirection.DOWN:
            self._state.selected_down = self._state.puzzle.clues.by_index[self._state.selected].down

    def render(self) -> None:
        # TODO: dont create a font every iteration
        font: Font = SysFont(self._font_name, VALUE_FONT_SIZE)
        for cell in self._cells:
            self._render_cell(cell, font)

        self._metadata.render()

        pygame.display.get_surface().blit(self._metadata.surface, self._metadata.placement)
        pygame.display.get_surface().blit(self._board.surface, self._board.placement)
