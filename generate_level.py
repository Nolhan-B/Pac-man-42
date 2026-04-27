from mazegenerator.mazegenerator import MazeGenerator
from parser import ConfigLoader


class Level:
    def __init__(self, level_id: int, config: ConfigLoader):
        self.level_id = level_id
        self.generator: MazeGenerator = self._init_generator(level_id, config)
        self.layout: list[list[int]] = self.generator.maze
        self.max_time = config.level_max_time
        self.points_per_pacgum: int = config.points_per_pacgum
        self.points_per_super_pacgum: int = config.points_per_super_pacgum
        self.points_per_ghost: int = config.points_per_ghost
        self.height: int = len(self.layout)
        self.width: int = len(self.layout[0]) if self.height > 0 else 0

    # Init method
    def _init_generator(self, level_id: int,
                        config: ConfigLoader) -> MazeGenerator:

        level_data = config.levels[level_id]
        size: tuple[int, int] = (level_data["width"], level_data["height"])
        return (MazeGenerator(size=size, seed=config.seed))
