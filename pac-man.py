import logging
logging.basicConfig(level=logging.WARNING)

from parser import ConfigLoader

loader = ConfigLoader("config.json")
loader.load()
print(loader.filepath)
print(loader.highscore_filename)
print(loader.lives)
print(loader.pacgum)
print(loader.points_per_super_pacgum)
print(loader.points_per_pacgum)
print(loader.points_per_ghost)
print(loader.seed)
print(loader.level_max_time)
print(loader.levels)