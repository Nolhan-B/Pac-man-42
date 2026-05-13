from typing import TYPE_CHECKING
import random
from constants import Direction, State, OPPOSITES

if TYPE_CHECKING:
    from game_engine import Engine


class Ghost():
    """Represents a ghost enemy with specific AI states and movement."""

    def __init__(self, color: str, pos_y: int, pos_x: int,
                 engine: "Engine", spawn: tuple[int, int]):
        """Initialize the ghost with its color, position, and spawn point."""
        self.color = color
        self._spawn = spawn
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.prev_x = self.pos_x
        self.prev_y = self.pos_y
        self._state = State.CHASE
        self.direction: Direction | None = None
        self.speed: float = 1.0
        self.engine: "Engine" = engine
        self.move_timer: float = 0.0
        self.frightened_timer: int = 0
        self.pos_history: list[tuple[int, int]] = []

    def set_state(self, new_state: State) -> None:
        """Update the ghost's behavioral state and timer if frightened."""
        if new_state == State.FRIGHTENED and self._state == State.DEAD:
            return
        if new_state == State.FRIGHTENED:
            self.frightened_timer = 360
        self._state = new_state

    def get_position(self) -> tuple[int, int]:
        """Return the current grid coordinates of the ghost."""
        return (self.pos_x, self.pos_y)

    def force_u_turn(self) -> None:
        """Force the ghost to smoothly reverse direction when frightened."""
        # On inverse la direction actuelle de manière fluide
        if self.direction in OPPOSITES:
            if self.direction == Direction.NORTH:
                self.pos_y += 1
            elif self.direction == Direction.SOUTH:
                self.pos_y -= 1
            elif self.direction == Direction.EAST:
                self.pos_x -= 1
            elif self.direction == Direction.WEST:
                self.pos_x += 1

            # On inverse le timer pour éviter le saut visuel
            self.move_timer = 30.0 - self.move_timer

            # On applique la nouvelle direction
            self.direction = OPPOSITES[self.direction]

        self.set_state(State.FRIGHTENED)

    def move(self, layout: list[list[int]]) -> None:
        """Calculate and execute the next move based on current state."""
        possible = []
        possible = self._get_possible_direction(layout)

        self.pos_history.append((self.pos_x, self.pos_y))
        if len(self.pos_history) > 18:
            self.pos_history.pop(0)

        if self._state == State.CHASE:
            move = self._chase_pac_man(possible)

        elif self._state == State.FRIGHTENED:
            move = self._run_from_pac_man(possible)

        elif self._state == State.DEAD:
            move = self._respawn(possible)

        else:
            return

        # Met a jour la direction et la position
        self.prev_x = self.pos_x
        self.prev_y = self.pos_y
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
        if (
            self._state == State.DEAD
            and (self.pos_x, self.pos_y) == self._spawn
        ):
            self.set_state(State.CHASE)

    @property
    def current_speed(self) -> float:
        """Return the effective speed modifier based on current state."""
        if self._state == State.FRIGHTENED:
            return self.speed * 0.5
        if self._state == State.DEAD:
            return self.speed * 2.0
        return self.speed

    def _get_possible_direction(self,
                                layout: list[list[int]]) -> list[Direction]:
        """Find all valid movement directions from the current cell."""
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

        if self.direction is None:
            return possible
        forbidden = OPPOSITES.get(self.direction)

        if forbidden in possible and len(possible) > 1:
            possible.remove(forbidden)

        return possible

    def _chase_pac_man(self, possible: list[Direction]) -> Direction:
        """Determine the next step to hunt down Pac-Man."""
        if random.random() < 0.35:
            return random.choice(possible)
        target: tuple[int, int] = self.engine.player.get_position()
        move = self._get_direction(target, possible)
        return move

    def _run_from_pac_man(self, possible: list[Direction]) -> Direction:
        """Determine the next step to escape from Pac-Man."""
        target: tuple[int, int] = self.engine.player.get_position()
        best_distance = -1.0  # On cherche le maximum donc on part de bas
        best_direction: Direction = possible[0]

        offsets = {
            Direction.NORTH: (0, -1),
            Direction.SOUTH: (0, 1),
            Direction.EAST: (1, 0),
            Direction.WEST: (-1, 0)
        }

        for direction in possible:
            dx, dy = offsets[direction]
            tx, ty = self.pos_x + dx, self.pos_y + dy
            #  Distance euclidienne
            dist = (target[0] - tx)**2 + (target[1] - ty)**2

            if dist > best_distance:
                best_distance = dist
                best_direction = direction

        return best_direction

    def _respawn(self, possible: list[Direction]) -> Direction:
        """Determine the path back to the ghost's spawn point."""
        target: tuple[int, int] = self._spawn
        if random.random() < 0.35:
            return random.choice(possible)
        move = self._get_direction(target, possible)
        return move

    def _get_direction(self, target: tuple[int, int],
                       possible: list[Direction]) -> Direction:
        """Evaluate the best direction to reach a given target coordinate."""
        best_distance = float('inf')
        best_direction = possible[0]  # Valeur par défaut

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
            # Malus pour les cases deja visitee
            if (tx, ty) in self.pos_history:
                dist += 1000
            # Comparaison
            if dist < best_distance:
                best_distance = dist
                best_direction = direction

        return best_direction

    def _state_timer(self) -> None:
        """Handle countdowns for temporary states like FRIGHTENED."""
        if self._state == State.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.set_state(State.CHASE)

    def ghost_update(self) -> None:
        """Update ghost movement timers and execute steps if needed."""
        self.move_timer += self.current_speed
        time_to_move = 30.0
        self._state_timer()
        if self.move_timer >= time_to_move:
            assert self.engine.current_level is not None
            layout = self.engine.current_level.layout
            self.move(layout)
            self.move_timer = 0.0
