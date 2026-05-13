from constants import Direction, OPPOSITES
from parser import ConfigLoader
import logging
from typing import List
logger = logging.getLogger(__name__)


class Player:
    """Represents the player character (Pac-Man) and its logic."""

    def __init__(self, config: ConfigLoader) -> None:
        """Initialize the player with config values."""
        self.lives = config.lives
        self._pos_x: int = 0
        self._pos_y: int = 0
        self.score: int = 0
        self.current_direction: Direction | None = None
        self.next_direction: Direction | None = None
        self.move_timer: float = 0.0
        self.speed: float = 20.0
        self.spawn: None | tuple[int, int] = None

    def update_speed(self, value: float) -> None:
        """Safely update the player's movement speed modifier."""
        if value <= 0:
            logger.warning("Can not update player's speed, "
                           "Value must be > 0 !")
        else:
            self.speed = value

    def set_default_speed(self) -> None:
        """Reset the player's speed to its default value."""
        self.speed = 20.0

    def move_up(self) -> None:
        """Move the player one tile North."""
        self.current_direction = Direction.NORTH
        self._pos_y -= 1

    def move_down(self) -> None:
        """Move the player one tile South."""
        self.current_direction = Direction.SOUTH
        self._pos_y += 1

    def move_right(self) -> None:
        """Move the player one tile East."""
        self.current_direction = Direction.EAST
        self._pos_x += 1

    def move_left(self) -> None:
        """Move the player one tile West."""
        self.current_direction = Direction.WEST
        self._pos_x -= 1

    def set_position(self, x: int, y: int) -> None:
        """Force the player's coordinates to a specific tile."""
        self._pos_x = x
        self._pos_y = y

    def get_position(self) -> tuple[int, int]:
        """Return the current (x, y) grid coordinates."""
        return (self._pos_x, self._pos_y)

    def get_pos_x(self) -> int:
        """Return the current x grid coordinate."""
        return self._pos_x

    def get_pos_y(self) -> int:
        """Return the current y grid coordinate."""
        return self._pos_y

    def lose_life(self) -> None:
        """Decrement the player's life count safely."""
        if self.lives == 0:
            logger.warning("Player can't lose life, already at 0 !")
        else:
            # logger.warning("Player justst lost a life!")
            self.lives -= 1

    def set_next_direction(self, direction: Direction) -> None:
        """Buffer the next desired movement direction."""
        self.next_direction = direction

    def add_score(self, amount: int) -> None:
        """Add the given amount to the player's total score."""
        self.score += amount

    def _execute_move(self) -> None:
        """Apply the current direction to update grid coordinates."""
        if self.current_direction == Direction.NORTH:
            self.move_up()
        elif self.current_direction == Direction.SOUTH:
            self.move_down()
        elif self.current_direction == Direction.WEST:
            self.move_left()
        elif self.current_direction == Direction.EAST:
            self.move_right()

    def _can_move(self, direction: Direction,
                  layout: List[List[int]]) -> bool:
        """Check if movement in the given direction is possible."""
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
        """Update movement timers and handle direction changes."""
        if self.current_direction and (
            self.next_direction == OPPOSITES.get(self.current_direction)
        ):
            if self.move_timer > 0 and self._can_move(
                self.current_direction, layout
            ):
                self._execute_move()
                self.move_timer = self.speed - self.move_timer
            else:
                self.move_timer = 0.0

            self.current_direction = self.next_direction
            self.next_direction = None
            return

        if self.move_timer == 0.0:
            if self.next_direction and self._can_move(
                self.next_direction, layout
            ):
                self.current_direction = self.next_direction
                self.next_direction = None

            # Si on fait face à un mur et qu'on ne peut pas avancer
            if self.current_direction and not self._can_move(
                self.current_direction, layout
            ):
                return

        self.move_timer += 1.0

        if self.move_timer >= self.speed:
            if self.current_direction and self._can_move(
                self.current_direction, layout
            ):
                self._execute_move()

            if self.next_direction and self._can_move(
                self.next_direction, layout
            ):
                self.current_direction = self.next_direction
                self.next_direction = None

            self.move_timer = 0.0
