import logging
import json

logger = logging.getLogger(__name__)

class HighscoreManager:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.scores = []
        self._load()

	# ici on cherche a charger le fichier des highscores
	# 
	def _load(self) -> None:
		try:
			with open(self.filepath, 'r', encoding="utf-8") as f:
				data = json.load(f)
		        self.scores = data if isinstance(data, list) else []
		except FileNotFoundError:
			logger.warning(f"Filepath {self.filepath} not found")
			_save()
		except (json.JSONDecodeError, OSError):
			logger.warning(f"{self.filepath} is a malformed json")
			logger.warning(f"Suppressing file content for safety...")
			try:
				open(self.filepath, 'w').close()
			except (PermissionError, OSError):
				logger.warning(f"Impossible de vider {self.filepath}")
			finally:
				self.scores = []

				