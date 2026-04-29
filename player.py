from constants import Direction
from parser import ConfigLoader
import logging
logger = logging.getLogger(__name__)


class Player:
    def __init__(self, config: ConfigLoader) -> None:
        self.lives = config.lives
        self._pos_x: int = None
        self._pos_y: int = None
        self.score: int = 0
        self.current_direction: Direction = None
        self.next_direction: Direction = None
        self.move_timer: float = 0.0

    def _init_player_pos(self, maze_size_x: int, maze_size_y: int) -> None:
        self._pos_x = maze_size_x // 2
        self._pos_y = maze_size_y // 2

    def move_up(self) -> None:
        self.current_direction = Direction.NORTH
        self._pos_y -= 1

    def move_down(self) -> None:
        self.current_direction = Direction.SOUTH
        self._pos_y += 1

    def move_right(self) -> None:
        self.current_direction = Direction.EAST
        self._pos_x += 1

    def move_left(self) -> None:
        self.current_direction = Direction.WEST
        self._pos_x -= 1

    def set_position(self, x: int, y: int) -> None:
        self._pos_x = x
        self._pos_y = y

    def get_position(self) -> tuple[int, int]:
        return (self._pos_x, self._pos_y)

    def get_pos_x(self) -> int:
        return self._pos_x

    def get_pos_y(self) -> int:
        return self._pos_y

    def lose_life(self) -> None:
        if self.lives == 0:
            logger.warning("Player can't lose life, already at 0 !")
        else:
            self.lives -= 1

    def set_next_direction(self, direction: Direction) -> None:
        self.next_direction = direction

    def add_score(self, amount: int) -> None:
        self.score += amount

    def _execute_move(self) -> None:
        if self.current_direction == Direction.NORTH:
            self.move_up()
        elif self.current_direction == Direction.SOUTH:
            self.move_down()
        elif self.current_direction == Direction.WEST:
            self.move_left()
        elif self.current_direction == Direction.EAST:
            self.move_right()

    def _can_move(self, direction, layout) -> bool:

        pos_x, pos_y = self._pos_x, self._pos_y
        val = layout[pos_y][pos_x]

        # Check Nord (Bit 1)
        if direction == Direction.NORTH and (val & 1) == 0:
            return True

        # Check Est (Bit 2)
        elif direction == Direction.EAST and (val & 2) == 0:
            return True

        # Check Sud (Bit 4)
        elif direction == Direction.SOUTH and (val & 4) == 0:
            return True

        # Check Ouest (Bit 8)
        elif direction == Direction.WEST and (val & 8) == 0:
            return True

        return False

    def update_player(self, layout: list[list[int]]) -> None:
        self.move_timer += 1.0
        time_to_move = 30.0
        if self.move_timer >= time_to_move:
            #  On essaye de tourner vers la direction demandée (next_dir)
            if self._can_move(self.next_direction, layout):
                self.current_direction = self.next_direction
            #  On vérifie si on peut avancer dans la direction actuelle
            if self._can_move(self.current_direction, layout):
                self._execute_move()
                self.move_timer = 0.0
            else:
                # On bute contre un mur, on attend une nouvelle direction
                self.move_timer = 0.0
