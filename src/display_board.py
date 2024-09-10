from dataclasses import dataclass

import pygame
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from config import BOARD_PADDING
from cross_word_state import CrossWordState


@dataclass(slots=True, init=False)
class BoardDisplay:
    placement: Rect
    surface: Surface

    def __init__(self, state: CrossWordState, cell_size: Vector2) -> None:
        window_rect: Rect = pygame.display.get_surface().get_rect()
        min_size: int = min(window_rect.width, window_rect.height) - BOARD_PADDING * 2
        dimensions: Vector2 = Vector2(state.puzzle.rows, state.puzzle.cols)
        board_size: Vector2 = cell_size * dimensions.elementwise()
        surface: Surface = Surface(board_size)
        left_over: float = min_size - board_size.x

        self.surface = surface
        self.placement = surface.get_rect(topleft=Vector2(BOARD_PADDING + left_over // 2))
