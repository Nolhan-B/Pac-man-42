import pygame
from constants import Direction
import sys
import logging
from player import Player
from game_engine import Engine
from config_parser import ConfigLoader

logger = logging.getLogger(__name__)


class Renderer:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.header = 150
        self.footer = 75
        self.side_margin = 150
        self.c_s = 0
        # font init doit etre appele avant SysFont,
        # et pygame.init() doit avoir tourne avant
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)
        try:
            self.pacman_sprite = pygame.image.load(
                "assets/pacman.png"
            ).convert_alpha()
        except Exception:
            logger.warning(
                "pacman sprite not loaded, using yellow rect instead."
            )
            self.pacman_sprite = pygame.Surface((30, 30))
            self.pacman_sprite.fill((255, 255, 0))

    def draw_all(self, engine, window_w):
        self.screen.fill((0, 0, 0))
        self._draw_maze(engine.current_level.layout)
        for ghost in engine.ghosts:
            self.draw_ghost(ghost)
        self.draw_pac_man(engine.player, engine.current_level.layout)
        self._draw_hud(engine, window_w)
        pygame.display.flip()

    def draw_pac_man(self, player, layout):
        px, py = player.get_position()
        if px is None:
            return

        offset_x, offset_y = 0, 0

        can_move = (
            player.current_direction is not None
            and player._can_move(player.current_direction, layout)
        )
        if can_move:
            progress = player.move_timer / 30.0
            if player.current_direction == Direction.NORTH:
                offset_y = -progress * self.c_s
            elif player.current_direction == Direction.SOUTH:
                offset_y = progress * self.c_s
            elif player.current_direction == Direction.WEST:
                offset_x = -progress * self.c_s
            elif player.current_direction == Direction.EAST:
                offset_x = progress * self.c_s

        sprite_resized = pygame.transform.smoothscale(
            self.pacman_sprite, (self.c_s, self.c_s)
        )
        rotations = {
            Direction.EAST: 0, Direction.NORTH: 90,
            Direction.WEST: 180, Direction.SOUTH: 270
        }
        angle = rotations.get(player.current_direction, 0)
        sprite_final = pygame.transform.rotate(sprite_resized, angle)

        pixel_x = px * self.c_s + (self.side_margin // 2) + offset_x
        pixel_y = py * self.c_s + self.header + offset_y
        self.screen.blit(sprite_final, (pixel_x, pixel_y))

    def _draw_maze(self, layout):
        for y, row in enumerate(layout):
            for x, cell in enumerate(row):
                ox = x * self.c_s + (self.side_margin // 2)
                oy = y * self.c_s + self.header
                self._draw_walls(ox, oy, cell)
                self._draw_items(ox, oy, cell)

    def _draw_walls(self, ox, oy, cell):
        color = (33, 33, 255)
        thickness = 2
        if cell & 1:
            pygame.draw.line(
                self.screen, color,
                (ox, oy), (ox + self.c_s, oy), thickness
            )
        if cell & 2:
            pygame.draw.line(
                self.screen, color,
                (ox + self.c_s, oy),
                (ox + self.c_s, oy + self.c_s), thickness
            )
        if cell & 4:
            pygame.draw.line(
                self.screen, color,
                (ox, oy + self.c_s),
                (ox + self.c_s, oy + self.c_s), thickness
            )
        if cell & 8:
            pygame.draw.line(
                self.screen, color,
                (ox, oy), (ox, oy + self.c_s), thickness
            )
        if cell == 15:
            pygame.draw.rect(
                self.screen, color, (ox, oy, self.c_s, self.c_s)
            )

    def _draw_items(self, ox, oy, cell):
        center = (ox + self.c_s // 2, oy + self.c_s // 2)
        gum_color = (255, 184, 174)
        if cell & 16:
            pygame.draw.circle(self.screen, gum_color, center, 3)
        if cell & 32:
            pygame.draw.circle(self.screen, gum_color, center, 8)

    def draw_ghost(self, ghost):
        gx, gy = ghost.get_position()
        offset_x, offset_y = 0, 0

        if ghost.direction is not None:
            progress = ghost.move_timer / 30.0
            progress = min(1.0, progress)
            dist_restante = self.c_s * (1.0 - progress)
            if ghost.direction == Direction.NORTH:
                offset_y = dist_restante
            elif ghost.direction == Direction.SOUTH:
                offset_y = -dist_restante
            elif ghost.direction == Direction.WEST:
                offset_x = dist_restante
            elif ghost.direction == Direction.EAST:
                offset_x = -dist_restante

        px = (
            gx * self.c_s
            + (self.side_margin // 2)
            + (self.c_s // 2)
            + offset_x
        )
        py = gy * self.c_s + self.header + (self.c_s // 2) + offset_y
        pygame.draw.circle(
            self.screen, ghost.color,
            (int(px), int(py)), self.c_s // 2.5
        )

    def _draw_hud(self, engine: Engine, window_w: int) -> None:
        # footer commence apres le labyrinthe
        footer_y = (
            self.header + engine.current_level.height * self.c_s + 10
        )

        score_text = self.font.render(
            f"Score: {engine.player.score}", True, (255, 255, 255)
        )
        lives_text = self.font.render(
            f"Vies: {engine.player.lives}", True, (255, 255, 255)
        )
        level_text = self.font.render(
            f"Niveau: {engine.level_id + 1}", True, (255, 255, 255)
        )

        total_width = (
            score_text.get_width()
            + lives_text.get_width()
            + level_text.get_width()
        )
        spacing = 60
        total = total_width + spacing * 2
        start_x = (window_w - total) // 2

        self.screen.blit(score_text, (start_x, footer_y))
        self.screen.blit(
            lives_text,
            (start_x + score_text.get_width() + spacing, footer_y)
        )
        self.screen.blit(
            level_text,
            (
                start_x
                + score_text.get_width()
                + lives_text.get_width()
                + spacing * 2,
                footer_y
            )
        )


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config_file.json>")
        raise SystemExit(1)

    config = ConfigLoader(sys.argv[1])
    config.load()

    player = Player(config)
    engine = Engine(0, config, player)
    engine.load_level(0)

    C_S = 30
    WINDOW_W = (engine.current_level.width * C_S) + 150
    WINDOW_H = (engine.current_level.height * C_S) + 150 + 75

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))

    renderer = Renderer(screen, config)
    renderer.c_s = C_S

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.set_next_direction(Direction.NORTH)
                elif event.key == pygame.K_DOWN:
                    player.set_next_direction(Direction.SOUTH)
                elif event.key == pygame.K_LEFT:
                    player.set_next_direction(Direction.WEST)
                elif event.key == pygame.K_RIGHT:
                    player.set_next_direction(Direction.EAST)

        engine.run()
        renderer.draw_all(engine, WINDOW_W)
        clock.tick(60)


if __name__ == "__main__":
    main()
