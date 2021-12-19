from board import Board
from constants import *
import drawer


pygame.init()


def main():
    clock = pygame.time.Clock()

    board = Board()

    running = True

    pygame.display.set_caption("Chess by Ismail Choudhury")

    # game loop
    while running:
        # board.ai.move(board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or board.check_quit():
                running = False

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                board.click(pos[0], pos[1])

        drawer.draw(board)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()


pygame.quit()





