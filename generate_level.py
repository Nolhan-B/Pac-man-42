from mazegenerator.mazegenerator import MazeGenerator
from parser import ConfigLoader
import random


class Level:
    PACGUM = 16
    SUPER_PACGUM = 32

    def __init__(self, level_id: int, config: ConfigLoader):
        self.level_id = level_id
        self.total_gum: int = 0
        self.generator: MazeGenerator = self._init_generator(level_id, config)
        self.layout: list[list[int]] = self.generator.maze
        self.max_time = config.level_max_time
        self.points_per_pacgum: int = config.points_per_pacgum
        self.points_per_super_pacgum: int = config.points_per_super_pacgum
        self.points_per_ghost: int = config.points_per_ghost
        self.height: int = len(self.layout)
        self.width: int = len(self.layout[0]) if self.height > 0 else 0
        self._init_put_gum()

    def _init_generator(self, level_id: int,
                        config: ConfigLoader) -> MazeGenerator:
        level_data = config.levels[level_id]
        size: tuple[int, int] = (level_data["width"], level_data["height"])
        seed = config.seed if level_id == 0 else random.randint(0, 99999999999)
        return MazeGenerator(size=size, seed=seed)

    def _init_put_gum(self) -> None:
        # 4 coin
        c1 = (0, 0)
        c2 = (self.width - 1, 0)
        c3 = (0, self.height - 1)
        c4 = (self.width - 1, self.height - 1)

        corners = [c1, c2, c3, c4]
        for y in range(self.height):
            for x in range(self.width):
                val = self.layout[y][x]

                # On ne met pas de gomme dans les blocs pleins (15)
                if (val & 15) == 15:
                    continue

                if (x, y) in corners:
                    # On force le bit 32
                    self.layout[y][x] |= 32
                    self.total_gum += 1
                else:
                    # On force le bit 16
                    self.layout[y][x] |= 16
                    self.total_gum += 1

    def check_and_eat_gum(self, player_posy: int, player_posx: int) -> str:
        val = self.layout[player_posy][player_posx]

        # Test de la Super-gum (bit 32)
        if val & 32:
            self.layout[player_posy][player_posx] &= ~self.SUPER_PACGUM
            return "SUPER"

        # Test de la Pac-gum normale (bit 16)
        if val & 16:
            self.layout[player_posy][player_posx] &= ~self.PACGUM
            return "NORMAL"
        # Rien trouvé
        return "NONE"
