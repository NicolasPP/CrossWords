import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH

from cross_words import CrossWords
from puzzle_reader import read_puzzle


class CrossWordsApp:

    def __init__(self) -> None:
        self._done: bool = False

        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    def run(self) -> None:
        cross_words: CrossWords = CrossWords(read_puzzle())

        while not self._done:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._done = True

            cross_words.render()
            pygame.display.flip()
