import math
from parser import ConfigLoader
from generate_level import Level
from ghost import Ghost
from constants import State, Direction
from player import Player


class Engine():
    def __init__(self, level_id: int, config: ConfigLoader, player: Player):
        self.level_id: int = level_id
        self.config = config
        self.player: Player = player
        self.lives = config.lives
        self.ghosts: list[Ghost] = []
        self.cheat_invincible: bool = False
        self.cheat_freeze: bool = False
        self.cheat_speed: bool = False
        self.running: bool = True
        self.is_paused: bool = False
        self.current_level: Level = None
        self.invincibility_timer = 0
        self.dying = False
        self.death_animation_timer = 60
        self.c_s: int = 30  # mis a jour depuis le main apres init

    def load_level(self, level_id: int) -> None:
        self.current_level = Level(level_id, self.config)
        mid_x = self.current_level.width // 2
        mid_y = self.current_level.height // 2
        self.player.set_position(mid_x, mid_y)
        self._spawn_ghosts()

    def next_level(self) -> None:
        self.level_id += 1
        if self.level_id < len(self.config.levels):
            self.load_level(self.level_id)
        else:
            print("Congrats ! You finished the game !")
            self.running = False

    def _spawn_ghosts(self) -> None:
        w = self.current_level.width
        h = self.current_level.height
        self.ghosts.clear()
        self.ghosts.append(Ghost("red", 1, 1, self, (1, 1)))
        self.ghosts.append(Ghost("blue", 1, w - 2, self, (w - 2, 1)))
        self.ghosts.append(Ghost("pink", h - 2, 1, self, (1, h - 2)))
        self.ghosts.append(Ghost("yellow", h - 2, w - 2, self, (w - 2, h - 2)))

    def _get_visual_pos_player(self) -> tuple[float, float]:
        # calcule la position visuelle du player en pixels (sans offset maze)
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
        y: int = self.player.get_pos_y()
        x: int = self.player.get_pos_x()
        type_gum: str = self.current_level.check_and_eat_gum(y, x)
        self._process_gum(type_gum)

    def _process_gum(self, type_gum: str) -> None:
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
        if self.current_level.total_gum == 0:
            print("Niveau Termine !")
            self.next_level()

    def _check_loose(self) -> None:
        if self.player.lives <= 0:
            print("Game Over...")
            self.running = False

    def _check_collisions(self) -> None:
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
        if not self.running or self.is_paused:
            return

        if self.dying:
            self.death_animation_timer -= 1
            if self.death_animation_timer <= 0:
                # animation fini on respawn
                mid_x = self.current_level.width // 2
                mid_y = self.current_level.height // 2
                self.player.current_direction = None
                self.player.next_direction = None
                self.player.set_position(mid_x, mid_y)
                self._spawn_ghosts()
                self.invincibility_timer = 120
                self.dying = False
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
