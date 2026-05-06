import logging
from typing import Dict, List, Optional, Tuple

import pygame

logger = logging.getLogger(__name__)


class AssetManager:

    def __init__(self) -> None:
        self.pacman_frames: List[pygame.Surface] = []
        self.pacman_frames_west: List[pygame.Surface] = []
        self.ghost_sprites: Dict[str, pygame.Surface] = {}
        self.walls: Dict[str, Optional[pygame.Surface]] = {}
        self.banners: Dict[str, pygame.Surface] = {}
        self.menu_bg: Optional[pygame.Surface] = None

    def load_all(self, screen_size: Tuple[int, int]) -> None:
        self._load_pacman()
        self._load_ghosts()
        self._load_walls()
        self._load_ui(screen_size)

    def _load_pacman(self) -> None:
        try:
            for i in range(8):
                path = f"assets/pacman_{i}.png"
                frame = pygame.image.load(path).convert_alpha()
                self.pacman_frames.append(frame)

                path_w = f"assets/pacman_west_{i}.png"
                frame_w = pygame.image.load(path_w).convert_alpha()
                self.pacman_frames_west.append(frame_w)
        except Exception as e:
            logger.warning("Missing Pac-Man sprites: %s", e)

    def _load_ghosts(self) -> None:
        colors = ["red", "blue", "yellow", "pink", "frightened", "dead"]
        for color in colors:
            try:
                path = f"assets/ghost_{color}.png"
                img = pygame.image.load(path).convert_alpha()
                self.ghost_sprites[color] = img
            except Exception as e:
                logger.warning("Missing %s ghost sprite: %s", color, e)
                surf = pygame.Surface((30, 30))
                surf.fill((200, 0, 0))
                self.ghost_sprites[color] = surf

    def _load_ui(self, screen_size: Tuple[int, int]) -> None:
        try:
            bg_img = pygame.image.load("assets/menu_bg.png").convert()
            self.menu_bg = pygame.transform.smoothscale(
                bg_img, screen_size
            )
        except Exception as e:
            logger.warning("Missing menu background: %s", e)

        banners = {
            "main": "assets/banner.png",
            "ready": "assets/ready.png",
            "go": "assets/go.png",
            "game_over": "assets/game_over_banner.png",
        }
        for key, path in banners.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self.banners[key] = img
            except Exception as e:
                logger.warning("Missing banner '%s': %s", key, e)
