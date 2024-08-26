from typing import Iterator

import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH
from cross_words import CrossWords
from delta_time import DeltaTime
from puzzle_reader import Puzzle, puzzles


class CrossWordsApp:

    def __init__(self) -> None:
        self._done: bool = False
        self._delta_time: DeltaTime = DeltaTime()

        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self._puzzles: Iterator[Puzzle] = puzzles()

    def run(self) -> None:

        cross_words: CrossWords = CrossWords(next(self._puzzles))

        while not self._done:
            self._delta_time.set()

            for event in pygame.event.get():
                cross_words.process_input(event)
                if event.type == pygame.QUIT:
                    self._done = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        cross_words = CrossWords(next(self._puzzles))
                        pygame.display.get_surface().fill("black")

            cross_words.render()
            cross_words.update(self._delta_time.get())
            pygame.display.update()
