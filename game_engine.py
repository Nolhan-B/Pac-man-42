import math
from parser import ConfigLoader
from generate_level import Level
from ghost import Ghost
from constants import State, Direction
from player import Player


class Engine():
    """Core game engine managing logic, actors, and level progression."""

    def __init__(self, level_id: int, config: ConfigLoader, player: Player):
        """Initialize the game engine with config, level, and player."""
        self.level_id: int = level_id
        self.config: ConfigLoader = config
        self.player: Player = player
        self.lives: int = config.lives
        self.ghosts: list[Ghost] = []
        self.cheat_invincible: bool = False
        self.cheat_freeze: bool = False
        self.cheat_speed: bool = False
        self.running: bool = True
        self.is_paused: bool = False
        self.current_level: Level | None = None
        self.invincibility_timer: int = 0
        self.dying = False
        self.death_animation_timer: int = 60
        self.c_s: int = 30  # mis a jour depuis le main apres init
        self.life_just_lost: bool = False
        self.level_just_changed: bool = False
        self.level_time_limit: float = 0.0
        self.time_left: float = 0.0
        self.game_completed: bool = False

    def start_level_timer(self) -> None:
        """Initialize and start the countdown timer for the current level."""
        # assert self.current_level is not None
        # time_per_tile = 1.6
        # area = self.current_level.width * self.current_level.height
        self.level_time_limit = self.config.level_max_time
        self.time_left = self.level_time_limit

    def load_level(self, level_id: int) -> None:
        """Load a specific level by its ID and place actors."""
        self.current_level = Level(level_id, self.config)
        assert self.current_level is not None
        size_x = self.current_level.width
        size_y = self.current_level.height
        mid_x, mid_y = self._init_player_pos(size_x, size_y)
        self.player.set_position(mid_x, mid_y)
        self._spawn_ghosts()
        self.start_level_timer()

    def _init_player_pos(self, size_x: int, size_y: int) -> tuple[int, int]:
        """Find the closest free tile to the geometric center for spawning."""
        if self.current_level is None:
            return (size_x // 2, size_y // 2)

        mid_x = size_x // 2
        mid_y = size_y // 2
        layout = self.current_level.layout
        best_pos = (mid_x, mid_y)
        min_dist = float('inf')

        for y in range(self.current_level.height):
            for x in range(self.current_level.width):
                # cases qui ne sont pas des mur plein(val != 15)
                if (layout[y][x] & 15) != 15:
                    dist = float(abs(x - mid_x) + abs(y - mid_y))
                    if dist < min_dist:
                        min_dist = dist
                        best_pos = (x, y)
        return best_pos

    def next_level(self) -> None:
        """Advance to the next level or trigger game completion."""
        if self.level_id + 1 < len(self.config.levels):
            self.level_id += 1
            print(f"Now going for level {self.level_id + 1}...")
            self.load_level(self.level_id)
            self.level_just_changed = True
        else:
            print("Congrats ! You finished the game !")
            self.game_completed = True

    def _spawn_ghosts(self) -> None:
        """Spawn the four ghosts in their respective starting corners."""
        assert self.current_level is not None
        w = self.current_level.width
        h = self.current_level.height
        self.ghosts.clear()
        self.ghosts.append(Ghost("red", 0, 0, self, (0, 0)))
        self.ghosts.append(Ghost("blue", 0, w - 1, self, (w - 1, 0)))
        self.ghosts.append(Ghost("pink", h - 1, 0, self, (0, h - 1)))
        self.ghosts.append(Ghost("yellow", h - 1, w - 1, self, (w - 1, h - 1)))

    def _get_visual_pos_player(self) -> tuple[float, float]:
        """Calculate the visual pixel position of the player."""
        px = self.player.get_pos_x()
        py = self.player.get_pos_y()
        if px is None:
            return 0.0, 0.0

        offset_x: float = 0.0
        offset_y: float = 0.0
        direction = self.player.current_direction
        progress = self.player.move_timer / self.player.speed

        if direction == Direction.NORTH:
            offset_y = -progress * self.c_s
        elif direction == Direction.SOUTH:
            offset_y = progress * self.c_s
        elif direction == Direction.WEST:
            offset_x = -progress * self.c_s
        elif direction == Direction.EAST:
            offset_x = progress * self.c_s

        return (px * self.c_s + offset_x +
                self.c_s // 2, py * self.c_s + offset_y + self.c_s // 2)

    def _get_visual_pos_ghost(self, ghost: "Ghost") -> tuple[float, float]:
        """Calculate the visual pixel position of a ghost."""
        # calcule la position visuelle du ghost en pixels (sans offset maze)
        gx = ghost.pos_x
        gy = ghost.pos_y
        offset_x: float = 0.0
        offset_y: float = 0.0

        if ghost.direction is not None:
            progress = min(1.0, ghost.move_timer / 30.0)
            dist_restante = self.c_s * (1.0 - progress)
            if ghost.direction == Direction.NORTH:
                offset_y = dist_restante
            elif ghost.direction == Direction.SOUTH:
                offset_y = -dist_restante
            elif ghost.direction == Direction.WEST:
                offset_x = dist_restante
            elif ghost.direction == Direction.EAST:
                offset_x = -dist_restante

        return (gx * self.c_s + offset_x +
                self.c_s // 2, gy * self.c_s + offset_y + self.c_s // 2)

    def take_pac_gum(self) -> None:
        """Check and process pac-gum consumption at the player's position."""
        px = self.player.get_pos_x()
        py = self.player.get_pos_y()

        offset_x: float = 0.0
        offset_y: float = 0.0

        if self.player.current_direction is not None:
            progress = self.player.move_timer / self.player.speed
            if self.player.current_direction == Direction.NORTH:
                offset_y = -progress
            elif self.player.current_direction == Direction.SOUTH:
                offset_y = progress
            elif self.player.current_direction == Direction.WEST:
                offset_x = -progress
            elif self.player.current_direction == Direction.EAST:
                offset_x = progress

        #  pos mathématique reel
        exact_x = px + offset_x
        exact_y = py + offset_y
        assert self.current_level is not None
        type_gum: str = self.current_level.check_and_eat_gum(exact_y, exact_x)
        self._process_gum(type_gum)

    def _process_gum(self, type_gum: str) -> None:
        """Update score and game state based on the type of gum eaten."""
        assert self.current_level is not None
        if type_gum == "SUPER":
            self.player.add_score(self.config.points_per_super_pacgum)
            self.current_level.total_gum -= 1
            self._check_win()
            for ghost in self.ghosts:
                ghost.force_u_turn()
        elif type_gum == "NORMAL":
            self.player.add_score(self.config.points_per_pacgum)
            self.current_level.total_gum -= 1
            self._check_win()
        elif type_gum == "NONE":
            return

    def _check_win(self) -> None:
        """Check if all pac-gums are eaten to trigger level or game win."""
        assert self.current_level is not None
        if self.current_level.total_gum == 0:
            print(f"Level {self.level_id + 1} ended!")
            if self.level_id >= len(self.config.levels) - 1:
                print("Final Victory !")
                self.game_completed = True
            else:
                print(f"Level {self.level_id + 1} done !")
                self.level_completed = True

    def _check_loose(self) -> None:
        """Check if the player has lost all lives and end the game."""
        if self.player.lives <= 0:
            print("Game Over...")
            self.running = False

    def _check_collisions(self) -> None:
        """Check for collisions between the player and any ghosts."""
        if self.invincibility_timer > 0:
            return

        px_vis, py_vis = self._get_visual_pos_player()
        px = self.player.get_pos_x()
        py = self.player.get_pos_y()

        for ghost in self.ghosts:
            gx_vis, gy_vis = self._get_visual_pos_ghost(ghost)
            dist = math.sqrt(
                (gx_vis - px_vis) ** 2 + (gy_vis - py_vis) ** 2
            )
            # collision si moins de 60% de la taille d'une case
            same_cell = (
                    (ghost.pos_x == px and ghost.pos_y == py) or
                    (ghost.prev_x == px and ghost.prev_y == py)
            )
            if dist < self.c_s * 0.65 and same_cell:
                self._handle_collision(ghost)

    def _handle_collision(self, ghost: "Ghost") -> None:
        """Handle the outcome of a collision based on ghost state."""
        if self.cheat_invincible is False:
            if ghost._state == State.CHASE:
                if self.invincibility_timer <= 0 and not self.dying:
                    self.dying = True
                    self.death_animation_timer = 60
                    self.player.lose_life()
                    self._check_loose()

        if ghost._state == State.FRIGHTENED:
            self.player.add_score(self.config.points_per_ghost)
            ghost.set_state(State.DEAD)

    def run(self) -> None:
        """Main logic update loop called every frame."""
        if not self.running or self.is_paused:
            return
        assert self.current_level is not None

        if self.time_left > 0:
            self.time_left -= 1/60
        elif not self.dying and not self.cheat_invincible:
            self.time_left = 0
            self.dying = True
            self.death_animation_timer = 60
            self.player.lose_life()
            self._check_loose()

        if self.dying:
            self.death_animation_timer -= 1
            if self.death_animation_timer <= 0:
                # animation fini on respawn
                size_x = self.current_level.width
                size_y = self.current_level.height
                self.player.current_direction = None
                self.player.next_direction = None
                mid_x, mid_y = self._init_player_pos(size_x, size_y)
                self.player.set_position(mid_x, mid_y)
                self._spawn_ghosts()
                self.invincibility_timer = 90
                self.dying = False
                self.start_level_timer()
            return

        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
        layout = self.current_level.layout
        self.player.update_player(layout)

        if self.cheat_speed is True:
            self.player.update_speed(10.0)
        else:
            self.player.set_default_speed()

        if self.cheat_freeze is False:
            for ghost in self.ghosts:
                ghost.ghost_update()

        self.take_pac_gum()
        self._check_collisions()
