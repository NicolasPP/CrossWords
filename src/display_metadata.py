import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

import pygame
from pygame.font import Font, SysFont, get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from config import HOVER_ALPHA, LINE_SEP
from cross_word_state import CrossWordState
from puzzle_reader import Clues


class ScrollDirection(Enum):
    UP = auto()
    DOWN = auto()


@dataclass(slots=True)
class ClueDisplay:
    surface: Surface
    placement: Rect
    id: int
    is_selected: bool = field(init=False)
    hover_surface: Surface = field(init=False)

    def __post_init__(self) -> None:
        self.is_selected = False
        self.hover_surface = Surface(self.surface.get_size())
        self.hover_surface.fill("black")
        self.hover_surface.set_alpha(HOVER_ALPHA)


@dataclass(slots=True, init=False)
class ClueSet:

    window: Surface
    window_placement: Rect

    surface: Surface
    clues: dict[int, ClueDisplay]

    scroll_pos: Vector2

    def __init__(self, window: Surface, window_placement: Rect, clue_set: dict[int, str], font: Font) -> None:
        self.window = window
        self.window_placement = window_placement
        self.clues = {}

        ids: list[int] = sorted(list(clue_set.keys()))
        prev_placement: Optional[Rect] = None
        for id_ in ids:

            clue: list[str] = split_text(clue_set[id_], window.get_width(), font)
            clue_surface: Surface = multi_line_render(clue, window.get_width(), font)
            placement: Rect = clue_surface.get_rect(topleft=(0, 0))

            if prev_placement is not None:
                placement = clue_surface.get_rect(topleft=prev_placement.bottomleft)
                placement.y += LINE_SEP * 4

            self.clues[id_] = ClueDisplay(clue_surface, placement, id_)
            prev_placement = placement

        surface: Surface = Surface((
            window.get_width(),
            Vector2(prev_placement.midbottom).y
        ))
        surface.fill("white")

        for clue_display in self.clues.values():
            surface.blit(clue_display.surface, clue_display.placement)

        self.surface = surface
        self.scroll_pos = Vector2(0)

    def clear_selection(self) -> None:
        for clue in self.clues.values():
            clue.is_selected = False

    def get_collided(self, mouse_pos: Vector2) -> Optional[ClueDisplay]:
        if not self.window_placement.collidepoint(mouse_pos):
            return None

        mouse_pos -= self.window_placement.topleft
        mouse_pos.y -= self.scroll_pos.y
        for clue in self.clues.values():
            if clue.placement.collidepoint(mouse_pos):
                return clue

        return None

    def render_selected(self) -> None:
        for clue in self.clues.values():
            if not clue.is_selected:
                continue

            self.window.blit(
                clue.hover_surface,
                clue.placement.topleft + self.scroll_pos
            )

    def scroll(self, direction: ScrollDirection) -> None:
        dir_mult: int = 1 if direction == ScrollDirection.UP else -1
        speed: int = 18
        next_pos: int = self.scroll_pos.y + (speed * dir_mult)

        min_pos: int = (self.surface.get_height() - self.window.get_height()) * -1
        if next_pos >= 0:
            next_pos = 0

        elif next_pos <= min_pos:
            next_pos = min_pos

        self.scroll_pos.y = next_pos


def multi_line_render(lines: list[str], max_width: int, font: Font) -> Surface:
    surface: Surface = Surface((
        max_width,
        sum([Vector2(font.size(ln)).y for ln in lines]) + LINE_SEP,
    ))
    surface.fill("white")
    prev_placement: Optional[Rect] = None
    for line in lines:
        surf: Surface = font.render(line, True, "black")

        placement: Rect = surf.get_rect(topleft=(0, 0))
        if prev_placement is not None:
            placement = surf.get_rect(topleft=prev_placement.bottomleft)
            placement.y += LINE_SEP

        surface.blit(surf, placement)
        prev_placement = placement

    return surface


def split_text(text: str, max_width: int, font: Font) -> list[str]:
    lines: list[str] = []
    line: str = ""

    def get_render_size(data: str) -> Vector2:
        return Vector2(font.size(data))

    for word in text.split():
        sep: str = " " if line else ""
        next_line: str = line + sep + word

        render_size: Vector2 = get_render_size(next_line)
        if render_size.x > max_width:
            lines.append(line)
            line = word

        else:
            line = next_line

    if line not in lines:
        lines.append(line)

    return lines


def get_max_size(longest: str, max_lines: int, font_name: str, max_width) -> int:
    size: int = 0
    font: Font = SysFont(font_name, size)

    def get_render_size() -> Vector2:
        return Vector2(font.size(longest))

    render_size: Vector2 = get_render_size()
    while (render_size.x // max_width) < max_lines:
        size += 1
        font = SysFont(font_name, size)
        render_size = get_render_size()

    return size


@dataclass(slots=True, init=False)
class CluesDisplay:
    surface: Surface
    placement: Rect

    across: ClueSet
    down: ClueSet

    def __init__(self, parent: Surface, date_placement: Rect, padding: Vector2, clues: Clues) -> None:
        surface: Surface = Surface((
            parent.get_width() - padding.x * 2,
            parent.get_height() - Vector2(date_placement.midbottom).y - padding.y * 2
        ))
        surface.fill("white")

        placement: Rect = surface.get_rect(midtop=date_placement.midbottom)
        placement.y += padding.y

        size: Vector2 = Vector2(
            (surface.get_width() - (padding.x * 3)) // 2,
            surface.get_height() - (padding.y * 2)
        )

        max_lines: int = 2
        longest_clue: str = max(
            list(clues.across.values()) + list(clues.down.values()),
            key=lambda clue: len(clue)
        )
        font_name: str = get_fonts()[0]
        clue_font_size: int = get_max_size(longest_clue, max_lines, font_name, size.x)
        clue_font: Font = SysFont(font_name, clue_font_size)

        across_window: Surface = Surface(size)
        across_window.fill("white")
        across_placement: Rect = across_window.get_rect(topleft=padding)
        across: ClueSet = ClueSet(across_window, across_placement, clues.across, clue_font)

        down_window: Surface = Surface(size)
        down_window.fill("white")
        down_placement: Rect = down_window.get_rect(topleft=across.window_placement.topright)
        down_placement.x += padding.x
        down: ClueSet = ClueSet(down_window, down_placement, clues.down, clue_font)

        self.surface = surface
        self.placement = placement

        self.across = across
        self.down = down

    def set_selected(self, across: Optional[int] = None, down: Optional[int] = None) -> None:
        self.across.clear_selection()
        self.down.clear_selection()

        if across is not None:
            self.across.clues[across].is_selected = True

        if down is not None:
            self.down.clues[down].is_selected = True


@dataclass(slots=True, init=False)
class MetadataDisplay:
    is_default_title: bool

    surface: Surface
    placement: Rect

    title: Surface
    title_placement: Rect

    date: Surface
    date_placement: Rect

    clues_display: CluesDisplay

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

        clues_display: CluesDisplay = CluesDisplay(surface, date_placement, padding, state.puzzle.clues)

        self.is_default_title = is_default_title

        self.surface = surface
        self.placement = surface.get_rect(topleft=top_left)

        self.title = title
        self.title_placement = title_placement

        self.date = date
        self.date_placement = date_placement

        self.clues_display = clues_display

    def render(self) -> None:
        self.clues_display.across.window.fill("white")
        self.clues_display.down.window.fill("white")
        self.clues_display.across.window.blit(self.clues_display.across.surface, self.clues_display.across.scroll_pos)
        self.clues_display.down.window.blit(self.clues_display.down.surface, self.clues_display.down.scroll_pos)

        self.clues_display.across.render_selected()
        self.clues_display.down.render_selected()

        self.clues_display.surface.blit(self.clues_display.across.window, self.clues_display.across.window_placement)
        self.clues_display.surface.blit(self.clues_display.down.window, self.clues_display.down.window_placement)

        self.surface.blit(self.clues_display.surface, self.clues_display.placement)


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
