import math
from dataclasses import dataclass
from typing import Optional

import pygame
from pygame.font import Font, SysFont, get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from cross_word_state import CrossWordState


@dataclass(slots=True, init=False)
class MetadataDisplay:
    is_default_title: bool

    surface: Surface
    placement: Rect

    title: Surface
    title_placement: Rect

    date: Surface
    date_placement: Rect

    clues: Surface
    clues_placement: Rect

    def __init__(self, board_placement: Rect, state: CrossWordState) -> None:
        window_rect: Rect = pygame.display.get_surface().get_rect()
        is_default_title: bool = state.puzzle.title.startswith("NY TIMES")
        font_name: str = get_fonts()[0]

        padding: Vector2 = Vector2(board_placement.topleft)
        top_left: Vector2 = Vector2(board_placement.topright)
        top_left.x += padding.x

        # creating main surface
        width: int = window_rect.width - top_left.x - padding.x
        height: int = window_rect.height - padding.y * 2
        surface: Surface = Surface((width, height))
        surface.fill("white")

        title_font_size: int = get_desired_font_size(font_name, state.puzzle.title,
                                                     math.floor(width * 0.6))
        title_font: Font = SysFont(font_name, title_font_size)
        title: Surface = title_font.render(state.puzzle.title, True, "black", "white")

        date_width_factor: float = 0.4 if is_default_title else 0.2
        date_font_size: int = get_desired_font_size(font_name, state.puzzle.date,
                                                    math.floor(width * date_width_factor))
        date_font: Font = SysFont(font_name, date_font_size)
        date: Surface = date_font.render(state.puzzle.date, True, "black", "white")

        title_placement: Rect = title.get_rect(midtop=(width // 2, padding.y))

        date_rect_dest: dict[str, tuple[float, float]] = \
            {"midtop": (width // 2, padding.y)} if is_default_title else {"midtop": title_placement.midbottom}
        date_placement: Rect = date.get_rect(**date_rect_dest)

        if is_default_title:
            surface.blit(date, date_placement)

        else:
            surface.blit(title, title_placement)
            date_placement.y += padding.y
            surface.blit(date, date_placement)

        clues_height: int = surface.get_height() - Vector2(date_placement.midbottom).y - padding.y * 2
        clues: Surface = Surface((surface.get_width() - padding.x * 2, clues_height))
        clues_placement: Rect = clues.get_rect(midtop=date_placement.midbottom)
        clues_placement.y += padding.y

        surface.blit(clues, clues_placement)

        self.is_default_title = is_default_title

        self.surface = surface
        self.placement = surface.get_rect(topleft=top_left)

        self.title = title
        self.title_placement = title_placement

        self.date = date
        self.date_placement = date_placement

        self.clues = clues
        self.clues_placement = clues_placement


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
