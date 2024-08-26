import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH

pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
done: bool = False
while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    pygame.display.flip()
