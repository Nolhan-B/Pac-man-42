from abc import ABC, abstractmethod
from typing import Any, List, Optional

import pygame

from assets import AssetManager


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
        color = (255, 184, 174)
        for y, row in enumerate(layout):
            for x, cell in enumerate(row):
                ox = x * c_s + mx + c_s // 2
                oy = y * c_s + my + c_s // 2
                if cell & 16:
                    pygame.draw.circle(self.screen, color, (ox, oy), 3)
                if cell & 32:
                    pygame.draw.circle(self.screen, color, (ox, oy), 8)


class ActorRenderer(BaseRenderer):

    def __init__(self, screen: pygame.Surface, assets: AssetManager) -> None:
        super().__init__(screen, assets)
        self.tick: int = 0

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
