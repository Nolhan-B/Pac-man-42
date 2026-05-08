from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from constants import Direction, State
import pygame
import math
from asset_manager import AssetManager


class BaseRenderer(ABC):

    def __init__(self, screen: pygame.Surface, assets: AssetManager) -> None:
        self.screen = screen
        self.assets = assets

    @abstractmethod
    def draw(self, *args: Any, **kwargs: Any) -> None:
        pass


class MazeRenderer(BaseRenderer):

    def __init__(self, screen: pygame.Surface, assets: AssetManager) -> None:
        super().__init__(screen, assets)
        self.maze_surface: Optional[pygame.Surface] = None

    def pre_render(
        self, layout: List[List[int]], w: int, h: int, c_s: int
    ) -> None:
        if c_s <= 0:
            return

        self.maze_surface = pygame.Surface(
            (w * c_s, h * c_s), pygame.SRCALPHA
        )

        for y, row in enumerate(layout):
            for x, cell in enumerate(row):
                ox = x * c_s
                oy = y * c_s
                shape = cell & 15
                if shape > 0:
                    self._draw_lines(self.maze_surface, ox, oy, shape, c_s)

    def _draw_background_grid(
        self, win_w: int, win_h: int, c_s: int
    ) -> None:
        """Dessine une grille de points subtile en arrière-plan."""
        grid_color = (30, 30, 40)

        for y in range(0, win_h, c_s):
            for x in range(0, win_w, c_s):

                pygame.draw.rect(self.screen, grid_color, (x, y, 1, 1))

    def _draw_lines(
        self, surface: pygame.Surface, ox: int, oy: int, shape: int, c_s: int
    ) -> None:
        color = (33, 33, 255)
        t = 8
        if shape & 1:
            pygame.draw.line(surface, color, (ox, oy), (ox + c_s, oy), t)
        if shape & 2:
            pygame.draw.line(
                surface, color, (ox + c_s, oy), (ox + c_s, oy + c_s), t
            )
        if shape & 4:
            pygame.draw.line(
                surface, color, (ox, oy + c_s), (ox + c_s, oy + c_s), t
            )
        if shape & 8:
            pygame.draw.line(surface, color, (ox, oy), (ox, oy + c_s), t)
        if shape == 15:
            pygame.draw.rect(surface, color, (ox, oy, c_s, c_s))

    def draw(
        self, layout: List[List[int]], mx: int, my: int, c_s: int
    ) -> None:
        if self.maze_surface:
            self.screen.blit(self.maze_surface, (mx, my))
        else:
            w, h = len(layout[0]), len(layout)
            self.pre_render(layout, w, h, c_s)
            if self.maze_surface:
                self.screen.blit(self.maze_surface, (mx, my))

        self._draw_items(layout, mx, my, c_s)

    def _draw_items(
        self, layout: List[List[int]], mx: int, my: int, c_s: int
    ) -> None:
        """Dessine les gommes avec animations de pulsation et brillance."""
        ticks = pygame.time.get_ticks()
        dot_color = (255, 184, 174)

        for y, row in enumerate(layout):
            for x, cell in enumerate(row):
                if not (cell & 48):  # 16 (Normal) | 32 (Super) = 48
                    continue

                # Calcul du centre de la case
                cx = x * c_s + mx + c_s // 2
                cy = y * c_s + my + c_s // 2

                # SUPER PAC-GUM (Bit 32)
                if cell & 32:
                    # dessine un cercle qui pulse autour du pacgum
                    pulse = 0.8 + 0.2 * math.sin(ticks * 0.008)
                    radius = int(8 * pulse)

                    # un peu de transparence
                    pygame.draw.circle(
                        self.screen, (255, 255, 255, 80),
                        (cx, cy), radius + 3
                    )
                    # la gomme elle meme
                    pygame.draw.circle(self.screen, dot_color, (cx, cy), radius)
                    # Reflet brillant au centre
                    pygame.draw.circle(
                        self.screen, (255, 255, 255), (cx - 2, cy - 2), 2
                    )

                # PAC-GUM NORMALE (Bit 16)
                elif cell & 16:
                    # juste un point (peut etre un asset plus tard)
                    size = 4
                    rect = (cx - size // 2, cy - size // 2, size, size)
                    pygame.draw.rect(self.screen, dot_color, rect)


class ActorRenderer(BaseRenderer):

    def __init__(self, screen: pygame.Surface, assets: AssetManager) -> None:
        super().__init__(screen, assets)
        self.tick: int = 0

    def draw(self, engine: Any, mx: int, my: int, c_s: int) -> None:
        """Main draw call for all actors."""
        for ghost in engine.ghosts:
            self.draw_ghost(ghost, mx, my, c_s)

        if getattr(engine, "dying", False):
            self.draw_death(
                engine.player, mx, my, c_s, engine.death_animation_timer
            )
        else:
            self.draw_pacman(
                engine.player, engine.current_level.layout,
                mx, my, c_s, engine.invincibility_timer
            )

    def draw_pacman(
        self, p: Any, layout: List[List[int]], mx: int, my: int,
        c_s: int, inv_timer: int
    ) -> None:
        if inv_timer > 0 and (inv_timer // 4) % 2 == 0:
            return

        px, py = p.get_position()
        if px is None:
            return

        pad = 12
        d_s = c_s - pad
        ox, oy = 0.0, 0.0

        if p.current_direction and p._can_move(p.current_direction, layout):
            self.tick += 1
            pr = p.move_timer / p.speed
            if p.current_direction == Direction.NORTH:
                oy = -pr * c_s
            elif p.current_direction == Direction.SOUTH:
                oy = pr * c_s
            elif p.current_direction == Direction.WEST:
                ox = -pr * c_s
            elif p.current_direction == Direction.EAST:
                ox = pr * c_s

        t = self.tick % 16
        f_idx = t if t < 8 else 15 - t

        # Fallback de sécurité si l'asset manque
        if not self.assets.pacman:
            surf = pygame.Surface((d_s, d_s))
            surf.fill((255, 255, 0))
            fx = px * c_s + mx + ox + (pad // 2)
            fy = py * c_s + my + oy + (pad // 2)
            self.screen.blit(surf, (fx, fy))
            return

        rots = {Direction.EAST: 0, Direction.NORTH: 90, Direction.SOUTH: 270}

        if p.current_direction == Direction.WEST:
            raw = self.assets.pacman_west[f_idx]
            spr = pygame.transform.smoothscale(raw, (d_s, d_s))
        else:
            raw = self.assets.pacman[f_idx]
            spr = pygame.transform.smoothscale(raw, (d_s, d_s))
            ang = rots.get(p.current_direction, 0)
            if ang:
                spr = pygame.transform.rotate(spr, ang)

        fx = px * c_s + mx + ox + (pad // 2)
        fy = py * c_s + my + oy + (pad // 2)
        self.screen.blit(spr, (fx, fy))

    def draw_ghost(self, g: Any, mx: int, my: int, c_s: int) -> None:
        gx, gy = g.get_position()
        ox, oy = 0.0, 0.0

        if g.direction is not None:
            pr = min(1.0, g.move_timer / 30.0)
            rem = c_s * (1.0 - pr)
            if g.direction == Direction.NORTH:
                oy = rem
            elif g.direction == Direction.SOUTH:
                oy = -rem
            elif g.direction == Direction.WEST:
                ox = rem
            elif g.direction == Direction.EAST:
                ox = -rem

        raw = None
        if g._state == State.FRIGHTENED:
            limit = g.frightened_timer < 120
            if limit and (g.frightened_timer // 10) % 2 == 0:
                raw = self.assets.ghosts.get(g.color)
            else:
                raw = self.assets.ghosts.get("frightened")
        elif g._state == State.DEAD:
            raw = self.assets.ghosts.get("dead")
        else:
            raw = self.assets.ghosts.get(g.color)

        if not raw:
            raw = pygame.Surface((30, 30))
            raw.fill((255, 0, 255))

        spr = pygame.transform.smoothscale(raw, (c_s, c_s))
        if g.direction == Direction.WEST:
            spr = pygame.transform.flip(spr, True, False)

        fx = gx * c_s + mx + ox
        fy = gy * c_s + my + oy
        self.screen.blit(spr, (int(fx), int(fy)))

    def draw_death(self, p: Any, mx: int, my: int, c_s: int, t: int) -> bool:
        ouv = (60 - t) * 6
        px, py = p.get_position()
        cx = int(px * c_s + mx + c_s // 2)
        cy = int(py * c_s + my + c_s // 2)
        rad = c_s // 2

        rect = pygame.Rect(cx - rad, cy - rad, rad * 2, rad * 2)
        sa = math.radians(ouv / 2)
        ea = math.radians(360 - ouv / 2)

        if ouv < 360:
            pygame.draw.arc(self.screen, (255, 255, 0), rect, sa, ea, rad)

        return t == 1


class UIRenderer(BaseRenderer):

    def __init__(self, screen: pygame.Surface, assets: AssetManager) -> None:
        super().__init__(screen, assets)
        path = "assets/PressStart2P.ttf"
        try:
            self.f_sm = pygame.font.Font(path, 14)
            self.f_hint = pygame.font.Font(path, 16)
            self.f_md = pygame.font.Font(path, 18)
            self.f_lg = pygame.font.Font(path, 22)
            self.f_menu = pygame.font.Font(path, 28)
            self.f_xl = pygame.font.Font(path, 36)
        except OSError:
            self.f_sm = pygame.font.SysFont("Arial", 14)
            self.f_hint = pygame.font.SysFont("Arial", 16)
            self.f_md = pygame.font.SysFont("Arial", 18)
            self.f_lg = pygame.font.SysFont("Arial", 22)
            self.f_menu = pygame.font.SysFont("Arial", 28)
            self.f_xl = pygame.font.SysFont("Arial", 36)

    def draw(
        self, engine: Any, win_w: int, footer_h: int,
        game_state: Any, countdown: int, timer: int
    ) -> None:
        self.draw_hud(engine, win_w, footer_h)
        if game_state.name == "COUNTDOWN":
            banner = "ready" if countdown > 0 else "go"
            self.draw_banner(banner, win_w, timer)
        if game_state.name == "GAME_OVER":
            self.draw_banner("game_over", win_w, 0)

    def draw_hud(self, engine: Any, window_w: int, footer_h: int) -> None:
        f_y = self.screen.get_height() - footer_h + 10
        sec = max(0, int(engine.time_left))
        t_col = (255, 255, 255)

        if sec < 10 and (int(engine.time_left * 5) % 2 == 0):
            t_col = (255, 0, 0)

        t_txt = self.f_sm.render(f"Time: {sec}s", True, t_col)
        s_txt = self.f_sm.render(
            f"Score: {engine.player.score}", True, (255, 255, 255)
        )
        l_txt = self.f_sm.render(
            f"Vies: {engine.player.lives}", True, (255, 255, 255)
        )
        lv_txt = self.f_sm.render(
            f"Level: {engine.level_id + 1}", True, (255, 255, 255)
        )

        sp = 50
        tw = (
            s_txt.get_width() + t_txt.get_width()
            + l_txt.get_width() + lv_txt.get_width() + (sp * 3)
        )
        curr_x = (window_w - tw) // 2

        hint = self.f_sm.render(
            "Press [TAB] to display keybinds", True, (50, 50, 50)
        )
        self.screen.blit(hint, (10, 10))

        for surf in [s_txt, t_txt, l_txt, lv_txt]:
            self.screen.blit(surf, (curr_x, f_y))
            curr_x += surf.get_width() + sp

    def draw_banner(self, name: str, window_w: int, timer: int) -> None:
        img = self.assets.banners.get(name)
        progress = (60 - timer) / 60.0

        if name == "go":
            scale_factor = 1.2 - (0.2 * progress)
            offset_y = -50 + (50 * progress)
        else:
            scale_factor = 1.0
            offset_y = 0.0

        if img:
            base_w = int(window_w * (0.7 if name == "game_over" else 0.5))
            tw = int(base_w * scale_factor)
            ratio = tw / img.get_width()
            th = int(img.get_height() * ratio)
            scaled = pygame.transform.smoothscale(img, (tw, th))
            x = (window_w - scaled.get_width()) // 2
            y = (self.screen.get_height() - scaled.get_height()) // 2
            self.screen.blit(scaled, (x, int(y + offset_y)))
        else:
            labels = {"ready": "READY?", "go": "GO!", "game_over": "GAME OVER"}
            txt = labels.get(name, name.upper())
            col = (255, 50, 50) if name == "game_over" else (255, 220, 0)
            surf = self.f_xl.render(txt, True, col)
            x = (window_w - surf.get_width()) // 2
            y = (self.screen.get_height() - surf.get_height()) // 2
            self.screen.blit(surf, (x, int(y + offset_y)))

    def draw_menu(self, window_w: int, window_h: int, sel: int) -> None:
        if self.assets.menu_bg:
            self.screen.blit(self.assets.menu_bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        ov = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        self.screen.blit(ov, (0, 0))

        if "main" in self.assets.banners:
            img = self.assets.banners["main"]

            # gestion des taille
            max_w = window_w * 1.25
            max_h = window_h * 0.60

            # evite de deformer
            ratio = min(max_w / img.get_width(), max_h / img.get_height())
            tw = int(img.get_width() * ratio)
            th = int(img.get_height() * ratio)

            scaled = pygame.transform.smoothscale(img, (tw, th))

            self.screen.blit(scaled, ((window_w - tw) // 2, window_h // 20))
        else:
            t = self.f_xl.render("PAC-MAN", True, (255, 220, 0))
            self.screen.blit(
                t, ((window_w - t.get_width()) // 2, window_h // 8)
            )

        opts = ["PLAY", "HIGHSCORES", "FULLSCREEN", "INSTRUCTIONS", "EXIT"]
        for i, opt in enumerate(opts):
            is_sel = (i == sel)
            col = (255, 220, 0) if is_sel else (200, 200, 200)

            t_surf = self.f_menu.render(opt, True, col)
            cx = window_w // 2
            cy = window_h // 2 + i * 75
            t_rect = t_surf.get_rect(center=(cx, cy))

            if is_sel:
                g_rect = t_rect.inflate(40, 20)
                pygame.draw.rect(
                    self.screen, (40, 40, 40), g_rect, border_radius=12
                )
                pygame.draw.rect(
                    self.screen, (255, 220, 0), g_rect, 2, border_radius=12
                )

                t_ticks = pygame.time.get_ticks()
                offset = int(math.sin(t_ticks * 0.01) * 8)
                c_surf = self.f_menu.render(">", True, (255, 220, 0))
                self.screen.blit(
                    c_surf, (t_rect.left - 50 + offset, t_rect.top)
                )

            self.screen.blit(t_surf, t_rect)

        hint = self.f_hint.render("USE ARROWS & ENTER", True, (100, 100, 100))
        self.screen.blit(
            hint, ((window_w - hint.get_width()) // 2, window_h - 50)
        )

    def draw_highscores(
        self, win_w: int, win_h: int, scores: List[Any]
    ) -> None:
        if self.assets.menu_bg:
            self.screen.blit(self.assets.menu_bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        ov = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        self.screen.blit(ov, (0, 0))

        titre = self.f_xl.render("HIGHSCORES", True, (255, 220, 0))
        self.screen.blit(titre, ((win_w - titre.get_width()) // 2, 30))

        c1 = win_w // 2 - 280
        c2 = win_w // 2 - 180
        c3 = win_w // 2 + 280

        hr = self.f_md.render("#", True, (150, 150, 150))
        hn = self.f_md.render("NAME", True, (150, 150, 150))
        hs = self.f_md.render("SCORE", True, (150, 150, 150))
        self.screen.blit(hr, (c1, 110))
        self.screen.blit(hn, (c2, 110))
        self.screen.blit(hs, (c3 - hs.get_width(), 110))

        pygame.draw.line(
            self.screen, (80, 80, 80), (c1, 138), (c3 + 10, 138), 1
        )

        y = 150
        for i, s in enumerate(scores[:10]):
            if i == 0:
                col = (255, 215, 0)
            elif i == 1:
                col = (192, 192, 192)
            elif i == 2:
                col = (205, 127, 50)
            else:
                col = (255, 255, 255)

            r_s = self.f_lg.render(f"{i+1}.", True, col)
            n_s = self.f_lg.render(s.name[:10], True, col)
            sc_s = self.f_lg.render(str(s.score)[:8], True, col)

            self.screen.blit(r_s, (c1, y))
            self.screen.blit(n_s, (c2, y))
            self.screen.blit(sc_s, (c3 - sc_s.get_width(), y))
            y += 52

        hint_txt = "PRESS ESC TO RETURN"
        hint_surf = self.f_sm.render(hint_txt, True, (150, 150, 150))
        self.screen.blit(
            hint_surf,
            ((win_w - hint_surf.get_width()) // 2, win_h - 60)
        )

    def draw_pause(
        self, win_w: int, win_h: int, sel: int, confirm: bool
    ) -> None:
        ov = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))

        msg = "Exit game?" if confirm else "PAUSED"
        opts = (
            ["Yes, exit", "No, go back"] if confirm
            else ["Resume", "Exit to menu"]
        )

        t_col = (255, 80, 80) if confirm else (255, 220, 0)
        t_surf = self.f_xl.render(msg, True, t_col)
        self.screen.blit(
            t_surf, ((win_w - t_surf.get_width()) // 2, win_h // 3)
        )

        for i, opt in enumerate(opts):
            col = (255, 220, 0) if i == sel else (255, 255, 255)
            pref = "> " if i == sel else "  "
            txt = self.f_lg.render(f"{pref}{opt}", True, col)
            x = (win_w - txt.get_width()) // 2
            y = win_h // 2 + i * 60
            self.screen.blit(txt, (x, y))

    def draw_instructions(self, window_w: int, window_h: int) -> None:
        if self.assets.menu_bg:
            self.screen.blit(self.assets.menu_bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        ov = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))

        titre = self.f_xl.render("HOW TO PLAY", True, (255, 220, 0))
        self.screen.blit(titre, ((window_w - titre.get_width()) // 2, 30))

        y = window_h // 3

        controls = [
            ("MOVE", ["UP", "DOWN", "LEFT", "RIGHT"]),
            ("PAUSE", ["P", "ESC"]),
            ("CHEATS", ["TAB"])
        ]

        for label, keys in controls:
            # Affichage du label
            lbl_surf = self.f_md.render(label, True, (255, 220, 0))
            self.screen.blit(lbl_surf, (window_w // 4, y))
            curr_x = window_w // 2 - 20
            for key in keys:
                # Rendu du texte de la touche
                k_surf = self.f_sm.render(key, True, (255, 255, 255))
                k_rect = k_surf.get_rect(topleft=(curr_x, y))

                # Contour du bouton
                btn_rect = k_rect.inflate(24, 18)
                pygame.draw.rect(
                    self.screen, (60, 60, 60), btn_rect, border_radius=5
                )
                pygame.draw.rect(
                    self.screen, (255, 255, 255), btn_rect, 1, border_radius=5
                )

                # Texte au centre du bouton
                self.screen.blit(
                    k_surf,
                    (btn_rect.centerx - k_surf.get_width() // 2,
                     btn_rect.centery - k_surf.get_height() // 2)
                )
                curr_x += btn_rect.width + 15
            y += 80

        # But du jeu
        y += 20
        goal_txt = "GOAL: Eat all pac-gums and avoid ghosts!"
        goal_surf = self.f_md.render(goal_txt, True, (200, 200, 255))
        self.screen.blit(
            goal_surf, ((window_w - goal_surf.get_width()) // 2, y)
        )

        # esc en bas
        hint = self.f_sm.render("PRESS ESC TO RETURN", True, (150, 150, 150))
        self.screen.blit(
            hint, ((window_w - hint.get_width()) // 2, window_h - 60)
        )

    def draw_enter_name(
        self, window_w: int, window_h: int, name: str, score: int
    ) -> None:
        self.screen.fill((0, 0, 0))

        t1 = self.f_xl.render("GAME OVER", True, (255, 50, 50))
        self.screen.blit(
            t1, ((window_w - t1.get_width()) // 2, window_h // 5)
        )

        t2 = self.f_lg.render(f"Final score : {score}", True, (255, 220, 0))
        y2 = window_h // 5 + 100
        self.screen.blit(t2, ((window_w - t2.get_width()) // 2, y2))

        t3 = self.f_lg.render("Enter your name :", True, (255, 255, 255))
        y3 = window_h // 2 - 40
        self.screen.blit(t3, ((window_w - t3.get_width()) // 2, y3))

        t4 = self.f_lg.render(name + "_", True, (255, 220, 0))
        y4 = window_h // 2 + 20
        self.screen.blit(t4, ((window_w - t4.get_width()) // 2, y4))

        msg = "Press [RETURN] to validate | max 10 characters"
        t5 = self.f_sm.render(msg, True, (100, 100, 100))
        y5 = window_h - 60
        self.screen.blit(t5, ((window_w - t5.get_width()) // 2, y5))

    def draw_cheats_overlay(self, cheats: Dict[str, bool]) -> None:
        ov = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))

        def status(val: bool) -> str:
            return "ON" if val else "OFF"

        lines = [
            "CHEATS", "",
            f"I -> Invincible : {status(cheats['invincible'])}",
            f"F -> Freeze ghosts : {status(cheats['freeze'])}",
            f"S -> Speed : {status(cheats['speed'])}",
            "N -> Next level", "V -> +1 Life", "", "TAB -> Fermer"
        ]
        for i, line in enumerate(lines):
            font = self.f_xl if i == 0 else self.f_sm
            if "ON" in line:
                col = (0, 255, 0)
            elif "OFF" in line:
                col = (255, 80, 80)
            else:
                col = (255, 255, 255)

            text = font.render(line, True, col)
            x = (self.screen.get_width() - text.get_width()) // 2
            y = 150 + i * 40
            self.screen.blit(text, (x, y))
