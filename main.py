import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    game = Game(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if not game.handle_event(event):
                running = False

        game.render()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
