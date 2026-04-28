from mazegenerator.mazegenerator import MazeGenerator
from parser import ConfigLoader


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

    # Init method
    def _init_generator(self, level_id: int,
                        config: ConfigLoader) -> MazeGenerator:

        level_data = config.levels[level_id]
        size: tuple[int, int] = (level_data["width"], level_data["height"])
        return (MazeGenerator(size=size, seed=config.seed))

    def _init_put_gum(self) -> None:
        corners = [
            (1, 1),                                      # Haut-Gauche
            (self.width - 2, 1),                         # Haut-Droite
            (1, self.height - 2),                        # Bas-Gauche
            (self.width - 2, self.height - 2)            # Bas-Droite
        ]

        for y in range(self.height):
            for x in range(self.width):
                val = self.layout[y][x]
                # Si (val & 15) == 15, c'est un bloc plein
                # cases où on peut marcher :
                if (val & 15) != 15:

                    if (x, y) in corners:
                        # coin:Super Pac-gum
                        self.layout[y][x] |= self.SUPER_PACGUM
                        self.total_gum += 1
                    else:
                        # couloir normal: Pac-gum
                        self.layout[y][x] |= self.PACGUM
                        self.total_gum += 1

    def check_and_eat_gum(self, player_posy, player_posx) -> str:
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
