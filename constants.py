"""Constants and enumerations used throughout the Pac-Man game."""

from enum import Enum, auto


class State(Enum):
    """Defines the behavioral states for the ghosts."""
    CHASE = auto()
    FRIGHTENED = auto()
    DEAD = auto()


class GameState(Enum):
    """Defines the global states for the main game loop."""
    COUNTDOWN = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    MENU = auto()
    INSTRUCTIONS = auto()
    PAUSE = auto()
    PAUSE_CONFIRM = auto()
    ENTER_NAME = auto()
    HIGHSCORES = auto()
    LEVEL_COMPLETED = auto()
    GAME_COMPLETED = auto()


class Direction(Enum):
    """Defines the four cardinal directions for movement."""
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()


# Maps each direction to its opposite for easy reversal
OPPOSITES = {
    Direction.NORTH: Direction.SOUTH,
    Direction.SOUTH: Direction.NORTH,
    Direction.EAST: Direction.WEST,
    Direction.WEST: Direction.EAST
}
