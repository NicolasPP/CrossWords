from typing import Any, NamedTuple

from pygame.font import Font, SysFont, get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

import pygame


class Board(NamedTuple):
    placement: Rect
    surface: Surface
    grid: list[Rect]


class CrossWords:

    def __init__(self, puzzle: dict[str, Any]) -> None:
        self._puzzle: dict[str, Any] = puzzle
        self._board: Board = self._create_board()

    def _create_board(self) -> Board:
        grid: list[Rect] = []
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
                grid.append(Rect(
                    col * size,
                    row * size,
                    size,
                    size
                ))

        return Board(placement, surface, grid)

    def render(self) -> None:

        for index, cell in enumerate(self._board.grid):
            surf: Surface = Surface(cell.size)

            self._render_clue_num(surf, cell, index)
            self._board.surface.blit(surf, cell)

        display_surface: Surface = pygame.display.get_surface()
        display_surface.blit(self._board.surface,
                             self._board.placement)

    def _render_clue_num(self, surf: Surface, cell: Rect, index: int) -> None:

        font: Font = SysFont(get_fonts()[0], 10)

        clue_number: int = self._puzzle["gridnums"][index]

        size: Vector2 = Vector2(surf.get_size())
        new_surf: Surface = Surface(size - Vector2(1))

        if self._puzzle["grid"][index] != ".":
            new_surf.fill("white")
            if clue_number != 0:

                new_surf.blit(
                    font.render(str(clue_number), True, "black", "white"),
                    Vector2(3)
                )

            hover: Surface = Surface(new_surf.get_size())
            hover.fill("black")
            hover.set_alpha(50)
            mouse_pos: Vector2 = Vector2(pygame.mouse.get_pos()) - Vector2(self._board.placement.topleft)
            if cell.collidepoint(mouse_pos):
                new_surf.blit(hover, (0, 0))

            surf.blit(new_surf, new_surf.get_rect(center=surf.get_rect().center))
