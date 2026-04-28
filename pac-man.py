import logging
logging.basicConfig(level=logging.WARNING)
import sys
from parser import ConfigLoader

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config_file.json>")
        raise SystemExit(1)
    
    config = ConfigLoader(sys.argv[1])
    config.load()

	#lancer le fichier

if __name__ == "__main__":
    main()