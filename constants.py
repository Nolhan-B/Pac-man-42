from enum import Enum, auto


class State(Enum):
    CHASE = auto()
    FRIGHTENED = auto()
    DEAD = auto()


class GameState(Enum):
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
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()


OPPOSITES = {
    Direction.NORTH: Direction.SOUTH,
    Direction.SOUTH: Direction.NORTH,
    Direction.EAST: Direction.WEST,
    Direction.WEST: Direction.EAST
    }
