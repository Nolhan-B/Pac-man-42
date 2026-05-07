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