import sys
import pygame
from typing import Dict

from constants import Direction, GameState
from game_engine import Engine
from player import Player
from parser import ConfigLoader
from HighscoreManager import HighscoreManager, PlayerScore
from renderer import Renderer


def _reset_game(config: ConfigLoader) -> tuple[Player, Engine]:
    """Reinitialize the player and engine to start a new game session."""
    player = Player(config)
    engine = Engine(0, config, player)
    engine.load_level(0)
    return player, engine


def main() -> None:
    """Initialize Pygame, manage game states, and run the main event loop."""
    config_file = "config.json"
    if len(sys.argv) == 2:
        config_file = sys.argv[1]
    elif len(sys.argv) > 2:
        print("Usage: python3 pac-man.py <config_file.json>")
        raise SystemExit(1)

    config = ConfigLoader(config_file)
    config.load()

    C_S = 42
    max_w = max(lvl["width"] for lvl in config.levels)
    max_h = max(lvl["height"] for lvl in config.levels)
    WINDOW_W = max_w * C_S + 150
    WINDOW_H = max_h * C_S + 150 + 75

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
    pygame.display.set_caption("Pac-Man - By nbarbosa & nbilyj")

    renderer = Renderer(screen)
    renderer.c_s = C_S

    highscore_manager = HighscoreManager(config.highscore_filename)
    player, engine = _reset_game(config)
    engine.c_s = C_S

    clock = pygame.time.Clock()
    game_state = GameState.MENU

    menu_selection, pause_selection = 0, 0
    confirm_selection = 1
    countdown, frame_timer = 1, 0
    player_name = ""
    show_cheats = False
    cheats: Dict[str, bool] = {
        "invincible": False,
        "freeze": False,
        "speed": False
    }

    is_fullscreen = False  # Track l'état de l'écran

    while True:
        win_w, win_h = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                renderer.assets.load_all((event.w, event.h))
                renderer.maze_p.maze_surface = None

            if event.type == pygame.KEYDOWN:
                if game_state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        menu_selection = (menu_selection - 1) % 5
                    elif event.key == pygame.K_DOWN:
                        menu_selection = (menu_selection + 1) % 5
                    elif event.key == pygame.K_RETURN:
                        if menu_selection == 0:  # PLAY
                            player, engine = _reset_game(config)
                            engine.c_s = C_S
                            countdown, frame_timer = 1, 0
                            game_state = GameState.COUNTDOWN
                            renderer.maze_p.maze_surface = None
                            player_name = ""
                        elif menu_selection == 1:  # HIGHSCORES
                            game_state = GameState.HIGHSCORES
                        elif menu_selection == 2:  # FULLSCREEN
                            is_fullscreen = not is_fullscreen
                            if is_fullscreen:
                                screen = pygame.display.set_mode(
                                    (0, 0), pygame.FULLSCREEN
                                )
                            else:
                                screen = pygame.display.set_mode(
                                    (WINDOW_W, WINDOW_H), pygame.RESIZABLE
                                )
                            renderer.screen = screen
                            renderer.assets.load_all(screen.get_size())
                            renderer.maze_p.maze_surface = None
                        elif menu_selection == 3:  # INSTRUCTIONS
                            game_state = GameState.INSTRUCTIONS
                        elif menu_selection == 4:  # EXIT
                            pygame.quit()
                            sys.exit()

                elif game_state == GameState.INSTRUCTIONS:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        game_state = GameState.MENU

                elif game_state == GameState.PLAYING:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        engine.is_paused = True
                        game_state = GameState.PAUSE
                        pause_selection = 0
                    elif event.key == pygame.K_TAB:
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

                elif game_state == GameState.PAUSE:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        engine.is_paused = False
                        game_state = GameState.PLAYING
                    elif event.key == pygame.K_UP:
                        pause_selection = (pause_selection - 1) % 2
                    elif event.key == pygame.K_DOWN:
                        pause_selection = (pause_selection + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if pause_selection == 0:
                            engine.is_paused = False
                            game_state = GameState.PLAYING
                        elif pause_selection == 1:
                            confirm_selection = 1
                            game_state = GameState.PAUSE_CONFIRM

                elif game_state == GameState.PAUSE_CONFIRM:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameState.PAUSE
                    elif event.key in (pygame.K_LEFT, pygame.K_UP):
                        confirm_selection = (confirm_selection - 1) % 2
                    elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                        confirm_selection = (confirm_selection + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if confirm_selection == 0:
                            engine.is_paused = False
                            game_state = GameState.MENU
                        else:
                            game_state = GameState.PAUSE

                elif game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        game_state = GameState.ENTER_NAME

                elif game_state == GameState.GAME_COMPLETED:
                    # quitter l'écran de victoire finale
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        game_state = GameState.ENTER_NAME

                elif game_state == GameState.ENTER_NAME:
                    if (
                        event.key == pygame.K_RETURN and
                        len(player_name.strip()) >= 3
                    ):
                        try:
                            ps = PlayerScore(player_name.strip(), player.score)
                            highscore_manager.add_score(ps)
                            game_state = GameState.HIGHSCORES
                        except ValueError as e:
                            print(e)
                        finally:
                            game_state = GameState.MENU

                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif len(player_name) < 10:
                        if event.key == pygame.K_SPACE:
                            player_name += " "
                        elif pygame.K_a <= event.key <= pygame.K_z:
                            player_name += event.unicode

                elif game_state == GameState.HIGHSCORES:
                    exit_keys = (
                        pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN
                    )
                    if event.key in exit_keys:
                        game_state = GameState.MENU
                        player_name = ""

        if game_state == GameState.MENU:
            cheats["invincible"] = False
            cheats["speed"] = False
            cheats["freeze"] = False
            show_cheats = False
            renderer.draw_menu(win_w, win_h, menu_selection)

        elif game_state == GameState.ENTER_NAME:
            renderer.draw_enter_name(win_w, win_h, player_name, player.score)

        elif game_state == GameState.INSTRUCTIONS:
            renderer.draw_instructions(win_w, win_h)

        elif game_state == GameState.COUNTDOWN:
            frame_timer += 2
            if frame_timer >= 60:
                frame_timer = 0
                countdown -= 1
            if countdown < 0:
                game_state = GameState.PLAYING
            renderer.draw_game(
                engine, game_state, countdown,
                frame_timer, show_cheats, cheats
            )

        elif game_state == GameState.PLAYING:
            engine.cheat_invincible = cheats["invincible"]
            engine.cheat_speed = cheats["speed"]
            engine.cheat_freeze = cheats["freeze"]
            engine.run()

            # conditions de fin/victoire/mort
            if not engine.running:
                game_state = GameState.GAME_OVER

            elif getattr(engine, 'game_completed', False):
                engine.game_completed = False
                game_state = GameState.GAME_COMPLETED

            elif getattr(engine, 'level_completed', False):
                engine.level_completed = False
                countdown, frame_timer = 2, 0  # 2 secondes d'affichage
                game_state = GameState.LEVEL_COMPLETED

            elif getattr(engine, 'life_just_lost', False):
                engine.life_just_lost = False
                countdown, frame_timer = 1, 0
                game_state = GameState.COUNTDOWN

            elif getattr(engine, 'level_just_changed', False):
                engine.level_just_changed = False
                countdown, frame_timer = 1, 0
                game_state = GameState.COUNTDOWN
                renderer.maze_p.maze_surface = None
                player.current_direction = None
                player.next_direction = None

            renderer.draw_game(
                engine, game_state, countdown,
                frame_timer, show_cheats, cheats
            )

        elif game_state == GameState.LEVEL_COMPLETED:
            frame_timer += 2
            if frame_timer >= 60:
                frame_timer = 0
                countdown -= 1

            if countdown < 0:
                engine.next_level()
                engine.level_just_changed = False
                countdown, frame_timer = 1, 0
                game_state = GameState.COUNTDOWN
                renderer.maze_p.maze_surface = None
                player.current_direction = None
                player.next_direction = None

            renderer.draw_game(
                engine, game_state, countdown,
                frame_timer, show_cheats, cheats
            )

        elif game_state == GameState.GAME_COMPLETED:
            renderer.draw_game(
                engine, game_state, 0, 0, show_cheats, cheats
            )

        elif game_state == GameState.PAUSE:
            renderer.draw_pause(win_w, win_h, pause_selection, False)

        elif game_state == GameState.PAUSE_CONFIRM:
            renderer.draw_pause(win_w, win_h, confirm_selection, True)

        elif game_state == GameState.GAME_OVER:
            renderer.draw_game(
                engine, game_state, countdown,
                frame_timer, show_cheats, cheats
            )

        elif game_state == GameState.HIGHSCORES:
            renderer.draw_highscores(win_w, win_h, highscore_manager.scores)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C Detected !\\nGood bye!")
