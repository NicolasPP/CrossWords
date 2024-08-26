import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH

from cross_words import CrossWords
from puzzle_reader import read_puzzle

if __name__ == "__main__":
    pygame.font.init()

    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    done: bool = False
    cross_words: CrossWords = CrossWords(read_puzzle())
    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        cross_words.render()
        pygame.display.flip()
