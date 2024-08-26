from dataclasses import dataclass
from typing import NamedTuple, Optional

import pygame
from pygame.event import Event
from pygame.font import Font, SysFont, get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from puzzle_reader import Puzzle, VOID_CELL

PADDING: int = 2
HOVER_ALPHA: int = 50


@dataclass(slots=True)
class CellDisplay:
    placement: Rect
    surface: Surface
    hover: Surface
    index: int
    value: Optional[str] = None

    def draw(self, puzzle: Puzzle, font: Font) -> None:

        size: Vector2 = Vector2(self.surface.get_size())
        padding: Vector2 = Vector2(PADDING)
        content: Surface = Surface(size - padding)

        if puzzle.board.state[self.index] == VOID_CELL:
            self.surface.fill("black")
            return

        content.fill("white")

        clue_number: int = puzzle.clues.grid[self.index]
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
        self._font: Font = SysFont(get_fonts()[0], 10)

        self._puzzle: Puzzle = puzzle
        self._selected: Optional[int] = None
        self._display: BoardDisplay = self._create_display()

    def process_input(self, event: Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos: Vector2 = self._get_board_mouse_pos()
            for cell in self._display.grid:
                if cell.placement.collidepoint(mouse_pos):
                    if self._puzzle.board.state[cell.index] == VOID_CELL:
                        return

                    cell_clues = self._puzzle.clues.by_index[cell.index]
                    print(cell_clues, cell.index, self._puzzle.answers.completed[cell.index], sep=", ")

                    if cell_clues.across is not None:
                        print("Across: ", self._puzzle.clues.across[cell_clues.across])
                        print("Answer: ", self._puzzle.answers.across[cell_clues.across])

                    if cell_clues.down is not None:
                        print("Down: ", self._puzzle.clues.down[cell_clues.down])
                        print("Answer: ", self._puzzle.answers.down[cell_clues.down])

                    print("----------------------------")
                    self._selected = cell.index

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_BACKSPACE:
                self._set_selected_value(None)
                return

            elif event.unicode.isalpha():
                self._set_selected_value(event.unicode.upper())
                self._jump_to_next_selected()
                return

    def _jump_to_next_selected(self) -> None:
        if self._selected is None:
            return

        next_selected: int = self._selected + 1
        if next_selected >= len(self._display.grid):
            self._selected = None
            return

        if self._puzzle.board.state[next_selected] == VOID_CELL:
            while self._puzzle.board.state[next_selected] == VOID_CELL:
                next_selected += 1

        if next_selected >= len(self._display.grid):
            self._selected = None
        else:
            self._selected = next_selected

    def _set_selected_value(self, value: Optional[str]) -> None:
        if self._selected is None:
            return

        self._display.grid[self._selected].value = value

    def update(self, delta_time: float) -> None:
        pass

    def _create_display(self) -> BoardDisplay:
        grid: list[CellDisplay] = []

        window_rect: Rect = pygame.display.get_surface().get_rect()
        min_size: int = min(window_rect.width, window_rect.height)
        size: int = min_size // self._puzzle.board.rows
        actual_size: int = size * self._puzzle.board.rows
        surface: Surface = Surface((actual_size, actual_size))
        placement: Rect = surface.get_rect(center=pygame.display.get_surface().get_rect().center)

        for row in range(self._puzzle.board.rows):
            for col in range(self._puzzle.board.cols):
                hover: Surface = Surface((size, size))
                hover.fill("black")
                hover.set_alpha(HOVER_ALPHA)
                cell: CellDisplay = CellDisplay(
                    Rect(col * size, row * size, size, size),
                    Surface((size, size)),
                    hover,
                    (row * self._puzzle.board.cols + col),
                )
                cell.draw(self._puzzle, self._font)
                grid.append(cell)

        return BoardDisplay(placement, surface, grid)

    def _render_cell(self, cell: CellDisplay) -> None:

        if self._puzzle.board.state[cell.index] == VOID_CELL:
            return

        self._display.surface.blit(cell.surface, cell.placement)

        if cell.value is not None:
            value_sign: Surface = self._font.render(cell.value, True, "black", "white")
            self._display.surface.blit(value_sign, value_sign.get_rect(center=cell.placement.center))

        #  Rendering hover surface
        if cell.index == self._selected:
            self._display.surface.blit(cell.hover, cell.placement)

    def _get_board_mouse_pos(self) -> Vector2:
        return Vector2(pygame.mouse.get_pos()) - Vector2(self._display.placement.topleft)

    def render(self) -> None:
        for cell in self._display.grid:
            self._render_cell(cell)

        pygame.display.get_surface().blit(self._display.surface, self._display.placement)
