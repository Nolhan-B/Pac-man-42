import pygame
from constants import Direction, GameState, State
import sys
import logging
from player import Player
from game_engine import Engine
from parser import ConfigLoader
import math

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
        self.tick: int = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.font_mid: pygame.font.Font = pygame.font.SysFont("Arial", 32, bold=True)
        FRAMES = 8
        try:
            self.pacman_frames = [
                pygame.image.load(f"assets/pacman_{i}.png").convert_alpha()
                for i in range(FRAMES)
            ]
            self.pacman_frames_west = [
                pygame.image.load(f"assets/pacman_west_{i}.png").convert_alpha()
                for i in range(FRAMES)
            ]
        except Exception:
            logger.warning("pacman sprite not loaded, "
                           "using yellow rect instead.")
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
        try:
            bg_img = pygame.image.load("assets/menu_bg.png").convert()
            self.menu_bg = (
                pygame.transform.smoothscale(bg_img,
                                             (self.screen.get_width(),
                                              self.screen.get_height())))
        except Exception:
            logger.warning("Menu background not found.")
            self.menu_bg = None
        try:
            self.banner_img = pygame.image.load("assets/banner.png").convert_alpha()
        except Exception:
            logger.warning("Banner PNG not found.")
            self.banner_img = None
        try:
            self.instruction_banner = pygame.image.load("assets/instruction_banner.png").convert_alpha()
        except Exception:
            logger.warning("Instruction banner PNG not found.")
            self.instruction_banner = None
        try:

            img = pygame.image.load("assets/game_over_banner.png").convert_alpha()
            target_w = self.screen.get_width() * 0.7
            ratio = target_w / img.get_width()
            target_h = int(img.get_height() * ratio)
            self.banner_game_over = pygame.transform.smoothscale(img, (int(target_w), target_h))     
        except Exception:
            logger.warning("Game Over banner PNG not found.")
            self.banner_game_over = None
        try:
            ready_img = pygame.image.load("assets/ready.png").convert_alpha()
            go_img = pygame.image.load("assets/go.png").convert_alpha()
            target_w = self.screen.get_width() * 0.5
            ratio_r = target_w / ready_img.get_width()
            self.banner_ready = pygame.transform.smoothscale(
                ready_img, (int(target_w), int(ready_img.get_height() * ratio_r))
            )
            ratio_g = target_w / go_img.get_width()
            self.banner_go = pygame.transform.smoothscale(
                go_img, (int(target_w), int(go_img.get_height() * ratio_g))
            )
        except Exception:
            logger.warning("Countdown banners not found.")
            self.banner_ready = None
            self.banner_go = None

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
        countdown: int,
        show_cheats: bool,
        cheats: dict = None
    ) -> None:
        self.screen.fill((0, 0, 0))

        # offset calcule une seule fois, passe a tous les draws
        ox, oy = self._get_maze_offset(engine, window_w)

        self._draw_maze(engine.current_level.layout, ox, oy)
        for ghost in engine.ghosts:
            self.draw_ghost(ghost, ox, oy)
        if getattr(engine, 'dying', False):
            if self.draw_death_animation(engine, engine.player, engine.death_animation_timer, ox, oy) is True:
                engine.life_just_lost = True
        else:
            # On ne dessine le Pac-Man normal que s'il est vivant
            self.draw_pac_man(engine.player, engine.current_level.layout, ox, oy,
                              engine.invincibility_timer)
        self._draw_hud(engine, window_w)

        if show_cheats:
            self._draw_cheats_overlay(cheats)

        if game_state == GameState.COUNTDOWN:
            self._draw_countdown(countdown, window_w)
        elif game_state == GameState.GAME_OVER:
            self._draw_game_over(window_w)

        pygame.display.flip()

    def draw_menu(
        self, window_w: int, window_h: int, selection: int
    ) -> None:
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
        overlay = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120)) # 120 = opacité (0-255)
        self.screen.blit(overlay, (0, 0))
        if self.banner_img:
            # On redimensionne la bannière pour qu'elle prenne 70% de la largeur
            target_w = int(window_w * 0.7)
            ratio = target_w / self.banner_img.get_width()
            target_h = int(self.banner_img.get_height() * ratio)
            
            scaled_banner = pygame.transform.smoothscale(self.banner_img, (target_w, target_h))
            b_x = (window_w - target_w) // 2
            self.screen.blit(scaled_banner, (b_x, window_h // 30))
        else:
            # Fallback texte si pas de bannière
            title = self.font_big.render("PAC-MAN", True, (255, 220, 0))
            self.screen.blit(title, ((window_w - title.get_width()) // 2, window_h // 4))

        options: list[str] = ["Play", "Highscores", "Instructions", "Exit"]
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
        current_banner = self.banner_ready if countdown > 0 else self.banner_go
        fallback_label = "Ready?" if countdown > 0 else "GO !"

        if current_banner:
            x = (window_w - current_banner.get_width()) // 2
            y = (self.screen.get_height() - current_banner.get_height()) // 2
            self.screen.blit(current_banner, (x, y))
        else:
            text: pygame.Surface = self.font_big.render(
                fallback_label, True, (255, 220, 0)
            )
            x = (window_w - text.get_width()) // 2
            y = (self.screen.get_height() - text.get_height()) // 2
            self.screen.blit(text, (x, y))

    def _draw_game_over(self, window_w: int) -> None:

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        next_y = 0

        if self.banner_game_over:
            bx = (window_w - self.banner_game_over.get_width()) // 2
            by = (self.screen.get_height() - self.banner_game_over.get_height()) // 2
            self.screen.blit(self.banner_game_over, (bx, by))
            # Le prochain texte sera sous l'image
            next_y = by + self.banner_game_over.get_height() + 20
        else:

            text = self.font_big.render("GAME OVER", True, (255, 50, 50))
            tx = (window_w - text.get_width()) // 2
            ty = (self.screen.get_height() - text.get_height()) // 2
            self.screen.blit(text, (tx, ty))
            next_y = ty + text.get_height() + 20

        # 3. Le texte d'instruction (Unifié pour éviter les répétitions)
        sub = self.font.render( 
            "Appuie sur ENTREE pour revenir au menu",
            True, (255, 255, 255) 
        )
        sub_x = (window_w - sub.get_width()) // 2
        self.screen.blit(sub, (sub_x, next_y))

    def draw_pac_man(self, player, layout, maze_ox, maze_oy,
                     invincibility_timer):
        if invincibility_timer > 0 and (invincibility_timer // 4) % 2 == 0:
            return
        px, py = player.get_position()
        if px is None:
            return

        padding = 12
        draw_size = self.c_s - padding

        offset_x: float = 0
        offset_y: float = 0
        can_move = (
            player.current_direction is not None
            and player._can_move(player.current_direction, layout)
        )
        if can_move:
            self.tick += 1
            progress = player.move_timer / player.speed
            if player.current_direction == Direction.NORTH:
                offset_y = -progress * self.c_s
            elif player.current_direction == Direction.SOUTH:
                offset_y = progress * self.c_s
            elif player.current_direction == Direction.WEST:
                offset_x = -progress * self.c_s
            elif player.current_direction == Direction.EAST:
                offset_x = progress * self.c_s

        FRAMES = 8
        t = self.tick % (FRAMES * 2)
        frame_idx = t if t < FRAMES else (FRAMES * 2 - 1 - t)

        rotations = {
            Direction.EAST:  0,
            Direction.NORTH: 90,
            Direction.SOUTH: 270,
        }
        if player.current_direction == Direction.WEST:
            sprite = pygame.transform.smoothscale(
                self.pacman_frames_west[frame_idx], (draw_size, draw_size)
            )
        else:
            sprite = pygame.transform.smoothscale(
                self.pacman_frames[frame_idx], (draw_size, draw_size)
            )
            angle = rotations.get(player.current_direction, 0)
            if angle:
                sprite = pygame.transform.rotate(sprite, angle)

        # On ajoute padding // 2 à la position pour recentrer le sprite dans la case
        pixel_x = px * self.c_s + maze_ox + offset_x + (padding // 2)
        pixel_y = py * self.c_s + maze_oy + offset_y + (padding // 2)
        self.screen.blit(sprite, (pixel_x, pixel_y))

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
        thickness: int = 8
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
            # Si le timer est bas: clignottement
            if ((ghost.frightened_timer < 120)
               and (ghost.frightened_timer // 10) % 2 == 0):
                #  sprite normal pour le clignotement
                sprite = self.ghost_sprites.get(ghost.color)
            else:
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
        # Le regard suis la direction
        if ghost.direction == Direction.WEST:
            sprite_resized = pygame.transform.flip(sprite_resized, True, False)
        px: float = gx * self.c_s + maze_ox + offset_x
        py: float = gy * self.c_s + maze_oy + offset_y

        self.screen.blit(sprite_resized, (int(px), int(py)))

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
            f"Level: {engine.level_id + 1}", True, (255, 255, 255)
        )

        total_width: int = (
            score_text.get_width()
            + lives_text.get_width()
            + level_text.get_width()
        )
        spacing: int = 60
        total: int = total_width + spacing * 2
        start_x: int = (window_w - total) // 2

        hint = self.font.render("Press [TAB] to display keybinds", True, (50, 50, 50))
        self.screen.blit(hint, (10, 10))

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

    def _draw_cheats_overlay(self, cheats: dict) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        def status(val: bool) -> str:
            return "ON" if val else "OFF"

        lines = [
            "CHEATS",
            "",
            f"I → Invincible : {status(cheats['invincible'])}",
            f"F → Freeze ghosts : {status(cheats['freeze'])}",
            f"S → Speed : {status(cheats['speed'])}",
            "N → Next level",
            "V → +1 Life",
            "",
            "TAB → Fermer"
        ]

        for i, line in enumerate(lines):
            font = self.font_big if i == 0 else self.font

            # couleur dynamique ON/OFF
            if "ON" in line:
                color = (0, 255, 0)
            elif "OFF" in line:
                color = (255, 80, 80)
            else:
                color = (255, 255, 255)

            text = font.render(line, True, color)
            x = (self.screen.get_width() - text.get_width()) // 2
            y = 150 + i * 40
            self.screen.blit(text, (x, y))

    def draw_death_animation(self, engine: Engine, player: Player, timer: int, maze_ox: int, maze_oy: int) -> bool:
        # Le timer descend de 60 à 0
        ouverture = (60 - timer) * 6 

        px, py = player.get_position()
        center_x = int(px * self.c_s + maze_ox + self.c_s // 2)
        center_y = int(py * self.c_s + maze_oy + self.c_s // 2)
        radius = self.c_s // 2

        # On dessine un camembert
        rect = pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # On commence à 0 et on réduit l'angle de fin
        start_angle = math.radians(ouverture / 2)
        end_angle = math.radians(360 - ouverture / 2)

        if ouverture < 360:
            # Dessine le corps jaune qui s'efface
            pygame.draw.arc(self.screen, (255, 255, 0), rect, start_angle, end_angle, radius)

        return timer == 1

    def draw_instructions(self, window_w: int, window_h: int) -> None:
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        overlay = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Un peu plus sombre pour faire ressortir le texte
        self.screen.blit(overlay, (0, 0))

        y = 20
        if self.instruction_banner:
            target_w = int(window_w * 0.7)
            ratio = target_w / self.instruction_banner.get_width()
            target_h = int(self.instruction_banner.get_height() * ratio)
            scaled = pygame.transform.smoothscale(self.instruction_banner, (target_w, target_h))
            self.screen.blit(scaled, ((window_w - target_w) // 2, y))
            y += target_h + 30
        else:
            title = self.font_big.render("HOW TO PLAY", True, (255, 220, 0))
            self.screen.blit(title, ((window_w - title.get_width()) // 2, y))
            y += 100

        # On définit des sections claires
        sections = [
            ("--- GOAL ---", [
                "Eat all pac-gums to win!",
                "Avoid ghosts unless they are blue."
            ]),
            ("--- CONTROLS ---", [
                "ARROWS : Move Pac-Man",
                "P / ESC : Pause game",
                "TAB : Open Cheat Menu"
            ])
        ]

        for title_text, lines in sections:
            # Titre de section en moyen et gras
            t_surf = self.font_mid.render(title_text, True, (255, 220, 0))
            self.screen.blit(t_surf, ((window_w - t_surf.get_width()) // 2, y))
            y += 45

            for line in lines:
                l_surf = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(l_surf, ((window_w - l_surf.get_width()) // 2, y))
                y += 35
            y += 20 # Espace entre les sections

        hint = self.font.render("Press ESC to return", True, (200, 200, 200))
        self.screen.blit(hint, ((window_w - hint.get_width()) // 2, window_h - 50))

        pygame.display.flip()

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

    print("\n" * 5)
    print(config.levels)
    print("\n" * 5)

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
    engine.c_s = C_S

    clock: pygame.time.Clock = pygame.time.Clock()

    game_state: GameState = GameState.MENU
    menu_selection: int = 0
    countdown: int = 3
    frame_timer: int = 0
    show_cheats: bool = False
    cheats = {
        "invincible": False,
        "freeze": False,
        "speed": False,
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if game_state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        menu_selection = (menu_selection - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        menu_selection = (menu_selection + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        if menu_selection == 0:
                            player, engine = _reset_game(config)
                            countdown = 1
                            frame_timer = 0
                            game_state = GameState.COUNTDOWN
                        elif menu_selection == 1:
                            pass  # highscores, a implementer
                        elif menu_selection == 2:
                            game_state = GameState.INSTRUCTIONS
                        elif menu_selection == 3:
                            pygame.quit()
                            sys.exit()

                elif game_state == GameState.INSTRUCTIONS:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        game_state = GameState.MENU

                elif game_state == GameState.PLAYING:
                    if event.key == pygame.K_TAB:
                        show_cheats = not show_cheats

                    elif event.key == pygame.K_i:
                        cheats["invincible"] = not cheats["invincible"]

                    elif event.key == pygame.K_f:
                        cheats["freeze"] = not cheats["freeze"]

                    elif event.key == pygame.K_s:
                        cheats["speed"] = not cheats["speed"]

                    elif event.key == pygame.K_n:
                        engine.next_level()

                    elif event.key == pygame.K_v:
                        player.lives += 1

                    elif event.key == pygame.K_UP:
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

        elif game_state == GameState.INSTRUCTIONS:
            renderer.draw_instructions(WINDOW_W, WINDOW_H)

        elif game_state == GameState.COUNTDOWN:
            frame_timer += 1
            if frame_timer >= 60:
                frame_timer = 0
                countdown -= 1
            if countdown < 0:
                game_state = GameState.PLAYING
            renderer.draw_all(engine, WINDOW_W, game_state, countdown, show_cheats, cheats)

        elif game_state == GameState.PLAYING:
            # Invincible
            if cheats["invincible"]:
                engine.cheat_invincible = True
            else:
                engine.cheat_invincible = False

            # Speed
            if cheats["speed"]:
                engine.cheat_speed = True
            else:
                engine.cheat_speed = False

            # Freeze ghosts
            if cheats["freeze"]:
                engine.cheat_freeze = True
            else:
                engine.cheat_freeze = False

            engine.run()
            if not engine.running:
                game_state = GameState.GAME_OVER
            elif engine.life_just_lost:
                engine.life_just_lost = False
                countdown = 1
                frame_timer = 0
                game_state = GameState.COUNTDOWN
            elif engine.level_just_changed:
                engine.level_just_changed = False
                countdown = 1
                frame_timer = 0
                game_state = GameState.COUNTDOWN
            renderer.draw_all(engine, WINDOW_W, game_state, countdown, show_cheats, cheats)

        elif game_state == GameState.GAME_OVER:
            renderer.draw_all(engine, WINDOW_W, game_state, countdown, show_cheats, cheats)

        clock.tick(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C Detected !\nGood bye!")

