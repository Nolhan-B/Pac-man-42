from dataclasses import dataclass, asdict
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class PlayerScore:
    """Represents a player's high score entry with validation."""
    name: str
    score: int

    def __post_init__(self) -> None:
        """Validate name length, alphanumeric characters, and score value."""
        if not all(c.isalnum() or c == ' ' for c in self.name):
            raise ValueError("PlayerScore's name can't contain"
                             " non-alnum characters :"
                             f" name '{self.name}' is not valid, "
                             "score was not saved.")
        if len(self.name) > 10:
            logger.warning(f"PlayerScore name {self.name} is too long !"
                           f"Name in use is now {self.name[:10]}")
            self.name = self.name[:10]

        if not isinstance(self.score, int) or self.score < 0:
            raise ValueError(f"Score must be a positive integer!"
                             f" (got :{self.score})")


class HighscoreManager:
    """Manages loading, adding, and saving the top 10 high scores."""

    def __init__(self, filepath: str) -> None:
        """Initialize the manager and load existing scores from disk."""
        self.filepath = filepath
        self.scores: list[PlayerScore] = []
        self._load()

    # ici on cherche a charger le fichier des highscores
    def _load(self) -> None:
        """Read scores from the JSON file, validating and sorting them."""
        try:
            with open(self.filepath, 'r', encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, list):
                    for e in data:
                        try:
                            # On essaie d'ajouter le score
                            self.scores.append(PlayerScore(e["name"],
                                                           e["score"]))
                        except (KeyError, ValueError, TypeError) as err:
                            logger.warning(
                                f"Score entry {e} is not valid and "
                                "will be ignored. "
                                f"Reason: {err}"
                            )
                self.scores = sorted(self.scores, key=lambda s: s.score,
                                     reverse=True)[:10]
        except FileNotFoundError:
            logger.warning(f"Filepath {self.filepath} not found")
            self._save()
        except (json.JSONDecodeError, OSError):
            logger.warning(f"{self.filepath} is a malformed json")
            logger.warning("Suppressing file content for safety...")
            try:
                open(self.filepath, 'w').close()
            except (PermissionError, OSError) as exc:
                logger.warning(f"Can not empty {self.filepath} : {exc}")
            finally:
                self.scores = []

    def add_score(self, score: PlayerScore) -> None:
        """Add a new score, sort the list, keep the top 10, and save."""
        self.scores.append(score)
        self.scores = sorted(self.scores, key=lambda e: e.score,
                             reverse=True)[:10]
        self._save()

    def _save(self) -> None:
        """Write the current list of top scores back to the JSON file."""
        try:
            with open(self.filepath, 'w', encoding="utf-8") as f:
                json.dump([asdict(s) for s in self.scores], f, indent=4)
        except (PermissionError, OSError) as e:
            logger.warning(f"Can not save players' scores : {e}")
