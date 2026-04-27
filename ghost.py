from enum import Enum, auto
from game_engine import Engine
from random import random


class State(Enum):
    CHASE = auto()
    FRIGHTENED = auto()
    DEAD = auto()


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



class Ghost():
    def __init__(self, color: str, pos_y: int, pos_x: int, engine: Engine, spawn: tuple):
        self.color = color
        self.spawn = spawn
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.state = State.CHASE
        self.direction = None
        self.speed = 1.0
        self.engine = engine

    def set_state(self, new_state: State):
        self.state = new_state

    def move(self, layout: list[list[int]], target_pos: tuple[int, int]):
        possible []
        possible = self._get_possible_direction(layout)

        if self.state == CHASE:
            move = _chase_pac_man(layout)

        if self.state == FRIGHTENED:
            move = random.choice(possible)

        if self.state == DEAD:
            move = _respawn_(layout, )


    def _get_possible_direction(self, layout):
        pos_x, pos_y = self.pos_x, self.pos_y
        val = layout[pos_y][pos_x]
        possible = []

        # Check Nord (Bit 1)
        if (val & 1) == 0:
            possible.append(Direction.NORTH)

        # Check Est (Bit 2)
        if (val & 2) == 0:
            possible.append(Direction.EAST)

        # Check Sud (Bit 4)
        if (val & 4) == 0:
            possible.append(Direction.SOUTH)

        # Check Ouest (Bit 8)
        if (val & 8) == 0:
            possible.append(Direction.WEST)
  
        forbidden = Direction.OPPOSITES.get(self.direction)
        if forbidden in possible and len(possible) > 1 and self.state != FRIGHTENED:
            possible.remove(forbidden)

        return possible

    def _chase_pac_man(self, layout):
        target: tuple = (player.pos_x, player.pos_y)
        move = 
        return move


    def _respawn_(self, layout)
        target: tuple = self.spawn
        move = 
        return move