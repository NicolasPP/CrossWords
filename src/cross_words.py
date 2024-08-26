from typing import Any, NamedTuple

from pygame.font import Font, SysFont, get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

import pygame

PADDING: int = 2
HOVER_ALPHA: int = 50


class Cell(NamedTuple):
    placement: Rect
    surface: Surface
    hover: Surface
    index: int


class Board(NamedTuple):
    placement: Rect
    surface: Surface
    grid: list[Cell]


class CrossWords:

    def __init__(self, puzzle: dict[str, Any]) -> None:
        self._puzzle: dict[str, Any] = puzzle
        self._font: Font = SysFont(get_fonts()[0], 10)
        self._board: Board = self._create_board()

    def update(self, delta_time: float) -> None:
        pass

    def _create_board(self) -> Board:
        grid: list[Cell] = []
        rows: int = self._puzzle["size"]["rows"]
        cols: int = self._puzzle["size"]["cols"]

        window_rect: Rect = pygame.display.get_surface().get_rect()
        min_size: int = min(window_rect.width, window_rect.height)
        size: int = min_size // rows
        actual_size: int = size * rows
        surface: Surface = Surface((actual_size, actual_size))
        placement: Rect = surface.get_rect(center=pygame.display.get_surface().get_rect().center)

        for row in range(rows):
            for col in range(cols):
                hover: Surface = Surface((size, size))
                hover.fill("black")
                hover.set_alpha(HOVER_ALPHA)
                cell: Cell = Cell(
                    Rect(col * size, row * size, size, size),
                    Surface((size, size)),
                    hover,
                    (row * cols + col)
                )

                self._draw_cell(cell)
                surface.blit(cell.surface, cell.placement)

                grid.append(cell)

        return Board(placement, surface, grid)

    def render(self) -> None:
        mouse_pos: Vector2 = Vector2(pygame.mouse.get_pos()) - Vector2(self._board.placement.topleft)
        for cell in self._board.grid:
            self._board.surface.blit(cell.surface, cell.placement)

            #  Rendering hover surface
            if cell.placement.collidepoint(mouse_pos):
                self._board.surface.blit(cell.hover, cell.placement)

        pygame.display.get_surface().blit(self._board.surface, self._board.placement)

    def _draw_cell(self, cell: Cell) -> None:
        clue_number: int = self._puzzle["gridnums"][cell.index]
        grid_value: str = self._puzzle["grid"][cell.index]

        size: Vector2 = Vector2(cell.surface.get_size())
        padding: Vector2 = Vector2(PADDING)
        content: Surface = Surface(size - padding)

        if grid_value == ".":
            cell.surface.fill("black")
            return

        content.fill("white")

        if clue_number != 0:
            clue_sign: Surface = self._font.render(
                str(clue_number),
                True,
                "black",
                "white"
            )
            content.blit(clue_sign, padding)

        cell.surface.blit(content, content.get_rect(center=cell.surface.get_rect().center))
