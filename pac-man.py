import logging
logging.basicConfig(level=logging.WARNING)

from parser import ConfigLoader

loader = ConfigLoader("config.json")
loader.load()
print(loader.config)