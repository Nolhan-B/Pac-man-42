import pygame
from constants import Direction, GameState, State
import sys
import logging
from player import Player
from game_engine import Engine
from parser import ConfigLoader

logger = logging.getLogger(__name__)


class Renderer:
    def __init__(self, screen: pygame.Surface, config: ConfigLoader) -> None:
        self.screen = screen
        self.config = config
        self.header: int = 150
        self.footer: int = 75
        self.c_s: int = 0
        self.ghost_sprites = {}
        ghost_list = ["red", "blue", "yellow", "pink"]
        pygame.font.init()
        self.font: pygame.font.Font = pygame.font.SysFont("Arial", 24)
        self.font_big: pygame.font.Font = pygame.font.SysFont(
            "Arial", 80, bold=True
        )
        self.font_menu: pygame.font.Font = pygame.font.SysFont("Arial", 40)
        try:
            self.pacman_sprite: pygame.Surface = pygame.image.load(
                "assets/pacman.png"
            ).convert_alpha()
        except Exception:
            logger.warning(
                "pacman sprite not loaded, using yellow rect instead."
            )
            self.pacman_sprite = pygame.Surface((30, 30))
            self.pacman_sprite.fill((255, 255, 0))
        for color in ghost_list:
            try:
                img = pygame.image.load(
                    f"assets/ghost_{color}.png").convert_alpha()
                self.ghost_sprites[color] = img
            except Exception:
                logger.warning(
                    "Ghost sprite not loaded, using default instead."
                )
                surf = pygame.Surface((30, 30))
                surf.fill(pygame.Color(color))
                self.ghost_sprites[color] = surf
        try:
            self.ghost_sprites["frightened"] = (
                pygame.image.load("assets/frightened.png").convert_alpha())
        except Exception:
            logger.warning(
                "Frightened sprite not loaded, using default instead."
            )
            surf = pygame.Surface((30, 30))
            surf.fill((0, 0, 255))  # Bleu par défaut
            self.ghost_sprites["frightened"] = surf
        try:
            self.ghost_sprites["dead"] = (
                pygame.image.load("assets/ghost_dead.png").convert_alpha())
        except Exception:
            surf = pygame.Surface((30, 30))
            surf.fill((255, 255, 255))
            self.ghost_sprites["dead"] = surf

    def _get_maze_offset(self, engine: Engine,
                         window_w: int) -> tuple[int, int]:
        available_w = window_w
        available_h = self.screen.get_height() - self.header - self.footer
        # C_S s'adapte a la taille du level en cours
        self.c_s = min(
            available_w // engine.current_level.width,
            available_h // engine.current_level.height
        )
        maze_px_w = engine.current_level.width * self.c_s
        maze_px_h = engine.current_level.height * self.c_s
        ox = (window_w - maze_px_w) // 2
        oy = self.header + (available_h - maze_px_h) // 2
        return ox, oy

    def draw_all(
        self,
        engine: Engine,
        window_w: int,
        game_state: GameState,
        countdown: int
    ) -> None:
        self.screen.fill((0, 0, 0))

        # offset calcule une seule fois, passe a tous les draws
        ox, oy = self._get_maze_offset(engine, window_w)

        self._draw_maze(engine.current_level.layout, ox, oy)
        for ghost in engine.ghosts:
            self.draw_ghost(ghost, ox, oy)
        self.draw_pac_man(engine.player, engine.current_level.layout, ox, oy)
        self._draw_hud(engine, window_w)

        if game_state == GameState.COUNTDOWN:
            self._draw_countdown(countdown, window_w)
        elif game_state == GameState.GAME_OVER:
            self._draw_game_over(window_w)

        pygame.display.flip()

    def draw_menu(
        self, window_w: int, window_h: int, selection: int
    ) -> None:
        self.screen.fill((0, 0, 0))

        title: pygame.Surface = self.font_big.render(
            "PAC-MAN", True, (255, 220, 0)
        )
        self.screen.blit(
            title, ((window_w - title.get_width()) // 2, window_h // 4)
        )

        options: list[str] = ["Jouer", "Highscores", "Quitter"]
        for i, option in enumerate(options):
            color = (255, 220, 0) if i == selection else (255, 255, 255)
            prefix = "> " if i == selection else "  "
            text: pygame.Surface = self.font_menu.render(
                f"{prefix}{option}", True, color
            )
            y = window_h // 2 + i * 60
            self.screen.blit(
                text, ((window_w - text.get_width()) // 2, y)
            )

        hint: pygame.Surface = self.font.render(
            "Fleches pour naviguer  |  ENTREE pour valider",
            True, (150, 150, 150)
        )
        self.screen.blit(
            hint, ((window_w - hint.get_width()) // 2, window_h - 60)
        )

        pygame.display.flip()

    def _draw_countdown(self, countdown: int, window_w: int) -> None:
        overlay: pygame.Surface = pygame.Surface(
            self.screen.get_size(), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        label: str = str(countdown) if countdown > 0 else "GO !"
        text: pygame.Surface = self.font_big.render(
            label, True, (255, 220, 0)
        )
        x = (window_w - text.get_width()) // 2
        y = (self.screen.get_height() - text.get_height()) // 2
        self.screen.blit(text, (x, y))

    def _draw_game_over(self, window_w: int) -> None:
        overlay: pygame.Surface = pygame.Surface(
            self.screen.get_size(), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        text: pygame.Surface = self.font_big.render(
            "GAME OVER", True, (255, 50, 50)
        )
        x = (window_w - text.get_width()) // 2
        y = (self.screen.get_height() - text.get_height()) // 2
        self.screen.blit(text, (x, y))

        sub: pygame.Surface = self.font.render(
            "Appuie sur ENTREE pour revenir au menu",
            True, (255, 255, 255)
        )
        self.screen.blit(
            sub, ((window_w - sub.get_width()) // 2, y + 100)
        )

    def draw_pac_man(
        self,
        player: Player,
        layout: list[list[int]],
        maze_ox: int,
        maze_oy: int
    ) -> None:
        px, py = player.get_position()
        if px is None:
            return

        offset_x: float = 0
        offset_y: float = 0

        can_move: bool = (
            player.current_direction is not None
            and player._can_move(player.current_direction, layout)
        )
        if can_move:
            progress: float = player.move_timer / player.speed
            if player.current_direction == Direction.NORTH:
                offset_y = -progress * self.c_s
            elif player.current_direction == Direction.SOUTH:
                offset_y = progress * self.c_s
            elif player.current_direction == Direction.WEST:
                offset_x = -progress * self.c_s
            elif player.current_direction == Direction.EAST:
                offset_x = progress * self.c_s

        sprite_resized: pygame.Surface = pygame.transform.smoothscale(
            self.pacman_sprite, (self.c_s, self.c_s)
        )
        rotations: dict[Direction, int] = {
            Direction.EAST: 0, Direction.NORTH: 90,
            Direction.WEST: 180, Direction.SOUTH: 270
        }
        angle: int = rotations.get(player.current_direction, 0)
        sprite_final: pygame.Surface = pygame.transform.rotate(
            sprite_resized, angle
        )

        pixel_x: float = px * self.c_s + maze_ox + offset_x
        pixel_y: float = py * self.c_s + maze_oy + offset_y
        self.screen.blit(sprite_final, (pixel_x, pixel_y))

    def _draw_maze(
        self, layout: list[list[int]], maze_ox: int, maze_oy: int
    ) -> None:
        for y, row in enumerate(layout):
            for x, cell in enumerate(row):
                ox: int = x * self.c_s + maze_ox
                oy: int = y * self.c_s + maze_oy
                self._draw_walls(ox, oy, cell)
                self._draw_items(ox, oy, cell)

    def _draw_walls(self, ox: int, oy: int, cell: int) -> None:
        color: tuple[int, int, int] = (33, 33, 255)
        thickness: int = 2
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

    def _draw_items(self, ox: int, oy: int, cell: int) -> None:
        center: tuple[int, int] = (
            ox + self.c_s // 2, oy + self.c_s // 2
        )
        gum_color: tuple[int, int, int] = (255, 184, 174)
        if cell & 16:
            pygame.draw.circle(self.screen, gum_color, center, 3)
        if cell & 32:
            pygame.draw.circle(self.screen, gum_color, center, 8)

    def draw_ghost(
        self, ghost: "Ghost", maze_ox: int, maze_oy: int
    ) -> None:
        gx, gy = ghost.get_position()
        offset_x: float = 0
        offset_y: float = 0

        if ghost.direction is not None:
            progress: float = ghost.move_timer / 30.0
            progress = min(1.0, progress)
            dist_restante: float = self.c_s * (1.0 - progress)
            if ghost.direction == Direction.NORTH:
                offset_y = dist_restante
            elif ghost.direction == Direction.SOUTH:
                offset_y = -dist_restante
            elif ghost.direction == Direction.WEST:
                offset_x = dist_restante
            elif ghost.direction == Direction.EAST:
                offset_x = -dist_restante

        # Sélection du sprite selon l'état actuel du fantôme
        if ghost._state == State.FRIGHTENED:
            sprite = self.ghost_sprites["frightened"]
        elif ghost._state == State.DEAD:
            sprite = self.ghost_sprites["dead"]
        else:
            sprite = self.ghost_sprites.get(ghost.color)

        if sprite is None:
            sprite = pygame.Surface((30, 30))
            sprite.fill((255, 0, 255))

        sprite_resized: pygame.Surface = pygame.transform.smoothscale(
            sprite, (self.c_s, self.c_s)
        )

        px: float = gx * self.c_s + maze_ox + offset_x
        py: float = gy * self.c_s + maze_oy + offset_y

        self.screen.blit(sprite_resized, (int(px), int(py)))

    # def draw_ghost(
    #     self, ghost: "Ghost", maze_ox: int, maze_oy: int  # type: ignore
    # ) -> None:
    #     gx, gy = ghost.get_position()
    #     offset_x: float = 0
    #     offset_y: float = 0

    #     if ghost.direction is not None:
    #         progress: float = ghost.move_timer / 30.0
    #         progress = min(1.0, progress)
    #         dist_restante: float = self.c_s * (1.0 - progress)
    #         if ghost.direction == Direction.NORTH:
    #             offset_y = dist_restante
    #         elif ghost.direction == Direction.SOUTH:
    #             offset_y = -dist_restante
    #         elif ghost.direction == Direction.WEST:
    #             offset_x = dist_restante
    #         elif ghost.direction == Direction.EAST:
    #             offset_x = -dist_restante

    #     px: float = gx * self.c_s + maze_ox + (self.c_s // 2) + offset_x
    #     py: float = gy * self.c_s + maze_oy + (self.c_s // 2) + offset_y
    #     pygame.draw.circle(
    #         self.screen, ghost.color,
    #         (int(px), int(py)), self.c_s // 2.5
    #     )

    def _draw_hud(self, engine: Engine, window_w: int) -> None:
        footer_y: int = (
            self.screen.get_height() - self.footer + 10
        )

        score_text: pygame.Surface = self.font.render(
            f"Score: {engine.player.score}", True, (255, 255, 255)
        )
        lives_text: pygame.Surface = self.font.render(
            f"Vies: {engine.player.lives}", True, (255, 255, 255)
        )
        level_text: pygame.Surface = self.font.render(
            f"Niveau: {engine.level_id + 1}", True, (255, 255, 255)
        )

        total_width: int = (
            score_text.get_width()
            + lives_text.get_width()
            + level_text.get_width()
        )
        spacing: int = 60
        total: int = total_width + spacing * 2
        start_x: int = (window_w - total) // 2

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


def _reset_game(config: ConfigLoader) -> tuple[Player, Engine]:
    # recrée un player et un engine tout frais pour une nouvelle partie
    player: Player = Player(config)
    engine: Engine = Engine(0, config, player)
    engine.load_level(0)
    return player, engine


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config_file.json>")
        raise SystemExit(1)

    config: ConfigLoader = ConfigLoader(sys.argv[1])
    config.load()

    player, engine = _reset_game(config)

    C_S: int = 30
    max_w: int = max(lvl["width"] for lvl in config.levels)
    max_h: int = max(lvl["height"] for lvl in config.levels)
    WINDOW_W: int = max_w * C_S + 150
    WINDOW_H: int = max_h * C_S + 150 + 75

    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))

    renderer: Renderer = Renderer(screen, config)
    renderer.c_s = C_S

    clock: pygame.time.Clock = pygame.time.Clock()

    game_state: GameState = GameState.MENU
    menu_selection: int = 0
    countdown: int = 3
    frame_timer: int = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if game_state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        menu_selection = (menu_selection - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        menu_selection = (menu_selection + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if menu_selection == 0:
                            player, engine = _reset_game(config)
                            countdown = 3
                            frame_timer = 0
                            game_state = GameState.COUNTDOWN
                        elif menu_selection == 1:
                            pass  # highscores, a implementer
                        elif menu_selection == 2:
                            pygame.quit()
                            sys.exit()

                elif game_state == GameState.PLAYING:
                    if event.key == pygame.K_UP:
                        player.set_next_direction(Direction.NORTH)
                    elif event.key == pygame.K_DOWN:
                        player.set_next_direction(Direction.SOUTH)
                    elif event.key == pygame.K_LEFT:
                        player.set_next_direction(Direction.WEST)
                    elif event.key == pygame.K_RIGHT:
                        player.set_next_direction(Direction.EAST)

                elif game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        game_state = GameState.MENU

        if game_state == GameState.MENU:
            renderer.draw_menu(WINDOW_W, WINDOW_H, menu_selection)

        elif game_state == GameState.COUNTDOWN:
            frame_timer += 1
            if frame_timer >= 60:
                frame_timer = 0
                countdown -= 1
            if countdown < 0:
                game_state = GameState.PLAYING
            renderer.draw_all(engine, WINDOW_W, game_state, countdown)

        elif game_state == GameState.PLAYING:
            engine.run()
            if not engine.running:
                game_state = GameState.GAME_OVER
            renderer.draw_all(engine, WINDOW_W, game_state, countdown)

        elif game_state == GameState.GAME_OVER:
            renderer.draw_all(engine, WINDOW_W, game_state, countdown)

        clock.tick(60)


if __name__ == "__main__":
    main()