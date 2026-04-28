import logging
import sys
from parser import ConfigLoader
from generate_level import Level
import pygame

logging.basicConfig(level=logging.WARNING)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config_file.json>")
        raise SystemExit(1)

    config = ConfigLoader(sys.argv[1])
    config.load()
    lvl = Level(1, config)

    C_S = 1200 // lvl.width
    HEADER = 150
    FOOTER = 75
    SIDE_MARGIN = 150
    WINDOW_W = C_S * lvl.width + SIDE_MARGIN
    WINDOW_H = C_S * lvl.height + HEADER + FOOTER

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 80)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        text = font.render("PAC-MAN", True, (255, 255, 0))
        screen.blit(text, (1200 // 2, HEADER // 2))

        for y, row in enumerate(lvl.layout):
            for x, cell in enumerate(row):
                # offset_y = HEADER pour decaler le labyrinthe sous le header
                ox = x * C_S + (SIDE_MARGIN // 2)
                oy = y * C_S + HEADER

                # North / Top
                if cell & 1:
                    pygame.draw.line(
                        screen, (255, 255, 255),
                        (ox, oy),
                        (ox + C_S, oy),
                        2
                    )
                # East / Right
                if cell & 2:
                    pygame.draw.line(
                        screen, (255, 255, 255),
                        (ox + C_S, oy),
                        (ox + C_S, oy + C_S),
                        2
                    )
                # South / Bottom
                if cell & 4:
                    pygame.draw.line(
                        screen, (255, 255, 255),
                        (ox, oy + C_S),
                        (ox + C_S, oy + C_S),
                        2
                    )
                # West / Left
                if cell & 8:
                    pygame.draw.line(
                        screen, (255, 255, 255),
                        (ox, oy),
                        (ox, oy + C_S),
                        2
                    )
                # Cellule pleine = mur solide
                if cell == 15:
                    pygame.draw.rect(
                        screen, (255, 255, 255),
                        (ox, oy, C_S, C_S)
                    )

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
