import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH
from cross_words import CrossWords
from delta_time import DeltaTime
from puzzle_reader import read_puzzle


class CrossWordsApp:

    def __init__(self) -> None:
        self._done: bool = False
        self._delta_time: DeltaTime = DeltaTime()

        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def run(self) -> None:
        cross_words: CrossWords = CrossWords(read_puzzle())

        while not self._done:
            self._delta_time.set()

            for event in pygame.event.get():
                cross_words.process_input(event)
                if event.type == pygame.QUIT:
                    self._done = True

            cross_words.render()
            cross_words.update(self._delta_time.get())
            pygame.display.update()
