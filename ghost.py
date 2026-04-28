from enum import Enum, auto
from game_engine import Engine
import random


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
    def __init__(self, color: str, pos_y: int, pos_x: int,
                 engine: Engine, spawn: tuple):
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
        possible = []
        possible = self._get_possible_direction(layout)

        if self.state == State.CHASE:
            move = self._chase_pac_man(possible)

        elif self.state == State.FRIGHTENED:
            move = random.choice(possible)

        elif self.state == State.DEAD:
            move = self._respawn(possible)

        # Met a jour la direction et la position
        self.direction = move
        if move == Direction.NORTH:
            self.pos_y -= 1
        elif move == Direction.SOUTH:
            self.pos_y += 1
        elif move == Direction.EAST:
            self.pos_x += 1
        elif move == Direction.WEST:
            self.pos_x -= 1
        # Si on atteinyt le spawn on repasse en chase
        if self.state == State.DEAD and (self.pos_x, self.pos_y) == self.spawn:
            self.set_state(State.CHASE)

    @property
    def current_speed(self):
        if self.state == State.FRIGHTENED:
            return self.speed * 0.5
        if self.state == State.DEAD:
            return self.speed * 2.0
        return self.speed

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
        if forbidden in possible and len(possible) > 1 and (self.state !=
                                                            State.FRIGHTENED):
            possible.remove(forbidden)

        return possible

    def _chase_pac_man(self, possible):
        target: tuple = (self.engine.player.pos_x, self.engine.player.pos_y)
        move = self._get_direction(target, possible)
        return move

    def _respawn(self, possible):
        target: tuple = self.spawn
        move = self._get_direction(target, possible)
        return move

    def _get_direction(self, target, possible):
        best_distance = float('inf')  # Plus propre que 1000000
        best_direction = self.direction  # Valeur par défaut

        # On définit le mouvement pour chaque direction
        # (delta_x, delta_y)
        offsets = {
            Direction.NORTH: (0, -1),
            Direction.SOUTH: (0, 1),
            Direction.EAST: (1, 0),
            Direction.WEST: (-1, 0)
        }

        for direction in possible:
            # On récupère le décalage correspondant
            dx, dy = offsets[direction]

            tx = self.pos_x + dx
            ty = self.pos_y + dy

            # Calcul de la distance euclidienne au carré
            # target[0] est x, target[1] est y
            dist = (target[0] - tx)**2 + (target[1] - ty)**2

            # Comparaison
            if dist < best_distance:
                best_distance = dist
                best_direction = direction

        return best_direction
