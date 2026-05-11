from typing import Any, Dict, Optional, Tuple
import pygame
from asset_manager import AssetManager
from constants import GameState
from base_renderer import ActorRenderer, MazeRenderer, UIRenderer
from HighscoreManager import PlayerScore


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.assets = AssetManager()
        self.assets.load_all(self.screen.get_size())

        self.maze_p = MazeRenderer(self.screen, self.assets)
        self.actor_p = ActorRenderer(self.screen, self.assets)
        self.ui_p = UIRenderer(self.screen, self.assets)

        self.header: int = 150
        self.footer: int = 75
        self.c_s: int = 0

    def _get_layout_params(self, engine: Any) -> Tuple[int, int, int]:
        win_w = self.screen.get_width()
        win_h = self.screen.get_height()
        avail_h = win_h - self.header - self.footer
        self.c_s = min(
            win_w // engine.current_level.width,
            avail_h // engine.current_level.height
        )
        mx = (win_w - (engine.current_level.width * self.c_s)) // 2
        my = self.header + (avail_h -
                            (engine.current_level.height * self.c_s)) // 2
        return mx, my, self.c_s

    def draw_game(self, engine: Any, game_state: GameState, countdown: int,
                  timer: int, show_cheats: bool,
                  cheats: Optional[Dict[str, bool]] = None) -> None:

        if self.assets.game_bg:
            self.screen.blit(self.assets.game_bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
        mx, my, c_s = self._get_layout_params(engine)

        engine.c_s = c_s

        self.maze_p.draw(engine.current_level.layout, mx, my, c_s)
        self.actor_p.draw(engine, mx, my, c_s)
        self.ui_p.draw_hud(engine, self.screen.get_width(), self.footer)

        if game_state == GameState.COUNTDOWN:
            banner = "ready" if countdown > 0 else "go"
            self.ui_p.draw_banner(banner, self.screen.get_width(), timer)
        if game_state == GameState.GAME_OVER:
            self.ui_p.draw_banner("game_over", self.screen.get_width(), 0)
        if game_state.name == "LEVEL_COMPLETED":
            self.ui_p.draw_banner("victory", self.screen.get_width(), timer)
        if game_state.name == "GAME_COMPLETED":
            self.ui_p.draw_banner("final_victory", self.screen.get_width(),
                                  timer)
        if show_cheats and cheats is not None:
            self.ui_p.draw_cheats_overlay(cheats)

        pygame.display.flip()

    def draw_menu(self, win_w: int, win_h: int, selection: int) -> None:
        self.ui_p.draw_menu(win_w, win_h, selection)
        pygame.display.flip()

    def draw_pause(self, win_w: int, win_h: int, selection: int,
                   confirm: bool) -> None:
        self.ui_p.draw_pause(win_w, win_h, selection, confirm)
        pygame.display.flip()

    def draw_highscores(self, win_w: int, win_h: int,
                        scores: list[PlayerScore]) -> None:
        self.ui_p.draw_highscores(win_w, win_h, scores)
        pygame.display.flip()

    def draw_instructions(self, win_w: int, win_h: int) -> None:
        self.ui_p.draw_instructions(win_w, win_h)
        pygame.display.flip()

    def draw_enter_name(self, win_w: int, win_h: int, name: str,
                        score: int) -> None:
        self.ui_p.draw_enter_name(win_w, win_h, name, score)
        pygame.display.flip()
