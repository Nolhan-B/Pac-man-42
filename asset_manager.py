import logging
from typing import Dict, List, Optional, Tuple

import pygame

logger = logging.getLogger(__name__)


class AssetManager:
    """Manages the loading and caching of all game graphical assets."""

    def __init__(self) -> None:
        """Initialize the AssetManager with empty containers."""
        self.pacman: List[pygame.Surface] = []
        self.pacman_west: List[pygame.Surface] = []
        self.ghosts: Dict[str, pygame.Surface] = {}
        self.banners: Dict[str, pygame.Surface] = {}
        self.menu_bg: Optional[pygame.Surface] = None
        self.game_bg: Optional[pygame.Surface] = None

    def load_all(self, screen_size: Tuple[int, int]) -> None:
        """Load all game resources into memory.

        Args:
            screen_size (Tuple[int, int]): current dimensions of the screen.
        """
        self._load_pacman()
        self._load_ghosts()
        self._load_ui(screen_size)
        self._load_back_maze(screen_size)  # On passe la taille ici

    def _load_back_maze(self, screen_size: Tuple[int, int]) -> None:
        """Load and scale the background image of the maze.

        Args:
            screen_size (Tuple[int, int]): dimensions to scale the background.
        """
        try:
            bg = pygame.image.load("assets/background.png").convert()
            scaled_bg = pygame.transform.scale(bg, screen_size)
            scaled_bg.set_alpha(100)

            self.game_bg = pygame.Surface(screen_size).convert()
            self.game_bg.fill((0, 0, 0))
            self.game_bg.blit(scaled_bg, (0, 0))
        except (pygame.error, FileNotFoundError):
            self.game_bg = pygame.Surface(screen_size).convert()
            self.game_bg.fill((0, 0, 0))

    def _load_pacman(self) -> None:
        """Load the animation sprites for Pac-Man."""
        try:
            for i in range(8):
                p = f"assets/pacman_{i}.png"
                self.pacman.append(pygame.image.load(p).convert_alpha())

                pw = f"assets/pacman_west_{i}.png"
                self.pacman_west.append(
                    pygame.image.load(pw).convert_alpha()
                )
        except FileNotFoundError as e:
            logger.warning("Missing Pac-Man sprites: %s", e)

    def _load_ghosts(self) -> None:
        """Load the sprites for all ghosts and their specific states."""
        colors = ["red", "blue", "yellow", "pink", "frightened", "dead"]
        for c in colors:
            try:
                p = f"assets/ghost_{c}.png"
                self.ghosts[c] = pygame.image.load(p).convert_alpha()
            except FileNotFoundError as e:
                logger.warning("Missing ghost sprite '%s': %s", c, e)

    def _load_ui(self, size: Tuple[int, int]) -> None:
        """Load user interface elements such as menus and banners.
        Args:
            size (Tuple[int, int]):The dimensions to scale the menu background.
        """
        try:
            bg = pygame.image.load("assets/menu_bg.png").convert()
            self.menu_bg = pygame.transform.smoothscale(bg, size)
        except FileNotFoundError as e:
            logger.warning("Missing menu background: %s", e)

        paths = {
            "main": "assets/banner.png",
            "game_over": "assets/game_over_banner.png",
            "ready": "assets/ready.png",
            "go": "assets/go.png",
            "victory": "assets/level_up.png",
            "final_victory": "assets/victory.png"
        }
        for key, path in paths.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                self.banners[key] = img
            except FileNotFoundError as e:
                logger.warning("Missing banner '%s': %s", key, e)
