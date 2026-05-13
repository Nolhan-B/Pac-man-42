import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


DEFAULTS: dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 240,
    "levels": [
        {"width": 13, "height": 13},
    ],
}


class ConfigLoader:
    """Charge et valide le fichier de config JSON du jeu.

    Gere les commentaires '#', les valeurs manquantes ou invalides,
    et les cles inconnues, sans jamais planter.

    Example:
        loader = ConfigLoader("config.json")
        loader.load()
        lives = loader.lives
    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        # les attributs sont initialises avec les defauts,
        # puis ecrases par load() si le fichier est valide
        self.highscore_filename: str = DEFAULTS["highscore_filename"]
        self.lives: int = DEFAULTS["lives"]
        self.points_per_pacgum: int = DEFAULTS["points_per_pacgum"]
        self.points_per_super_pacgum: int = DEFAULTS["points_per_super_pacgum"]
        self.points_per_ghost: int = DEFAULTS["points_per_ghost"]
        self.seed: int = DEFAULTS["seed"]
        self.level_max_time: int = DEFAULTS["level_max_time"]
        self.levels: list[dict[str, Any]] = list(DEFAULTS["levels"])

    def load(self) -> None:
        """Point d'entree principal, appelle les etapes dans l'ordre."""
        raw_content = self._read_file()
        clean_content = self._strip_comments(raw_content)
        raw_config = self._parse_json(clean_content)
        self._validate(raw_config)

    # --- Etape 1 : lecture du fichier ---

    def _read_file(self) -> str:
        # Lit le fichier et retourne son contenu brut.
        # Si le fichier existe pas ou est illisible, on exit proprement.
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error : file '{self.filepath}' not found")
            raise SystemExit(1)
        except OSError as e:
            print(f"Error: Can not read '{self.filepath}' : {e}")
            raise SystemExit(1)

    # del des commentaires dans les json

    def _strip_comments(self, raw: str) -> str:
        # le JSON supporte pas les commentaires donc on les vire avant
        # on passe ligne par ligne et si ca commence par # on skip.
        lines = []
        for line in raw.splitlines():
            if not line.strip().startswith("#"):
                lines.append(line)
        return "\n".join(lines)

    # parsing json

    def _parse_json(self, content: str) -> dict[str, Any]:
        try:
            raw = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(
                "Config : '%s' is not valid JSON : %s. "
                "All defaults will be used.",
                self.filepath, e
            )
            return {}

        if not isinstance(raw, dict):
            logger.warning(
                "Config : '%s' must be a JSON object. "
                "All defaults will be used.",
                self.filepath
            )
            return {}

        return raw

    # validation cle par cle

    def _validate(self, raw: dict[str, Any]) -> None:
        # on valide chaque cle connue et on assigne direct sur self
        # les cles inconnues sont ignorees automatiquement
        self.highscore_filename = self._clamp(
            self._get(
                raw,
                "highscore_filename",
                DEFAULTS["highscore_filename"]
            ),
            str, None, None,
            "highscore_filename", DEFAULTS["highscore_filename"]
        )
        raw_lives = self._get(raw, "lives", DEFAULTS["lives"])
        if isinstance(raw_lives, int) and raw_lives < 0:
            logger.warning(
                "Config 'lives' : negative value %d is invalid, "
                "using default: %d", raw_lives, DEFAULTS["lives"]
            )
            raw_lives = DEFAULTS["lives"]
        self.lives = self._clamp(
            raw_lives, int, 1, 10, "lives", DEFAULTS["lives"]
        )
        self.points_per_pacgum = self._clamp(
            self._get(raw, "points_per_pacgum", DEFAULTS["points_per_pacgum"]),
            int, 0, 10000, "points_per_pacgum", DEFAULTS["points_per_pacgum"]
        )
        self.points_per_super_pacgum = self._clamp(
            self._get(
                raw,
                "points_per_super_pacgum",
                DEFAULTS["points_per_super_pacgum"]
            ),
            int, 0, 10000,
            "points_per_super_pacgum", DEFAULTS["points_per_super_pacgum"]
        )
        self.points_per_ghost = self._clamp(
            self._get(raw, "points_per_ghost", DEFAULTS["points_per_ghost"]),
            int, 0, 10000, "points_per_ghost", DEFAULTS["points_per_ghost"]
        )
        self.seed = self._clamp(
            self._get(raw, "seed", DEFAULTS["seed"]),
            int, 0, 2**32 - 1, "seed", DEFAULTS["seed"]
        )
        self.level_max_time = self._clamp(
            self._get(raw, "level_max_time", DEFAULTS["level_max_time"]),
            int, 10, 600, "level_max_time", DEFAULTS["level_max_time"]
        )
        self.levels = self._parse_levels(raw.get("levels"))

    # les helpers

    def _clamp(
        self,
        value: Any,
        expected_type: type,
        min_val: Any,
        max_val: Any,
        key: str,
        default: Any
    ) -> Any:
        # check que la valeur soit du bon type et dans les bornes.
        # si c'est invalide, on log un warning et on retourne le defaut.
        if not isinstance(value, expected_type):
            logger.warning(
                "Config '%s' : expected %s, got %s. Default: %s",
                key, expected_type.__name__, type(value).__name__, default
            )
            return default

        if min_val is not None and value < min_val:
            logger.warning(
                "Config '%s' : value %s is too small, clamped at %s.",
                key, value, min_val
            )
            return min_val

        if max_val is not None and value > max_val:
            logger.warning(
                "Config '%s' : value %s too high, clamped at %s.",
                key, value, max_val
            )
            return max_val

        return value

    def _parse_level(self, raw_level: Any, index: int) -> dict[str, Any]:
        # valide un niveau individuel (width + height).
        # si c'est pas un dict, on retourne le niveau par defaut.
        default_level = DEFAULTS["levels"][0]

        if not isinstance(raw_level, dict):
            logger.warning(
                "Config : level %d is not valid, default level used.", index
            )
            return dict(default_level)

        width = self._clamp(
            raw_level.get("width", default_level["width"]),
            int, 5, 19, f"levels[{index}].width", default_level["width"]
        )
        height = self._clamp(
            raw_level.get("height", default_level["height"]),
            int, 5, 19, f"levels[{index}].height", default_level["height"]
        )

        return {"width": width, "height": height}

    # a refactorer plus tard avec une vraie classe LevelConfig
    def _parse_levels(self, raw: Any) -> list[dict[str, Any]]:
        # parse la liste des levels, le sujet en demande 10,
        # donc si c'est trop court on complete avec
        #  le niveau par defaut.
        min_levels = 10
        default_level = DEFAULTS["levels"][0]

        if not isinstance(raw, list) or len(raw) == 0:
            logger.warning(
                "Config : 'levels' missign or invalid, "
                "%d defaut levels generated.", min_levels
            )
            return [dict(default_level) for _ in range(min_levels)]

        levels = [self._parse_level(lvl, i) for i, lvl in enumerate(raw)]

        while len(levels) < min_levels:
            levels.append(dict(default_level))
            logger.warning(
                "Config : levels count is < 10, new levels added "
                "(total : %d).", len(levels)
            )

        return levels

    def _get(self, raw: dict[str, Any], key: str, default: Any) -> Any:
        if key not in raw:
            logger.warning(
                "Config : key '%s' not found, using default: %s", key, default
            )
            return default
        return raw[key]
