import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


DEFAULTS: dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "levels": [
        {"width": 21, "height": 21},
    ],
}


class ConfigLoader:
    """Charge et valide le fichier de config JSON du jeu.

    Gere les commentaires '#', les valeurs manquantes ou invalides,
    et les cles inconnues, sans jamais planter.

    Example:
        loader = ConfigLoader("config.json")
        loader.load()
        lives = loader.config["lives"]
    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.config: dict[str, Any] = {}

    def load(self) -> None:
        """Point d'entree principal, appelle les etapes dans l'ordre."""
        raw_content = self._read_file()
        clean_content = self._strip_comments(raw_content)
        raw_config = self._parse_json(clean_content)
        self.config = self._validate(raw_config)

    # --- Etape 1 : lecture du fichier ---

    def _read_file(self) -> str:
        # Lit le fichier et retourne son contenu brut.
        # Si le fichier existe pas ou est illisible, on exit proprement.
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Erreur : fichier introuvable : '{self.filepath}'")
            raise SystemExit(1)
        except OSError as e:
            print(f"Erreur : impossible de lire '{self.filepath}' : {e}")
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

    # parsning json

    def _parse_json(self, content: str) -> dict[str, Any]:
        # parse le JSON sans commenatires, si c'est pas du JSON valide ou
        # pas un objet (genre une liste), on exit avec un message clair.
        try:
            raw = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Erreur : JSON invalide dans '{self.filepath}' : {e}")
            raise SystemExit(1)

        if not isinstance(raw, dict):
            print(f"Erreur : '{self.filepath}' doit etre un objet JSON.")
            raise SystemExit(1)

        return raw

    # ensuite validation cle par cle

    def _validate(self, raw: dict[str, Any]) -> dict[str, Any]:
        # on valide chaque cle connue
        # Les cles inconnues sont ignorees automatiquement ducoup
        config: dict[str, Any] = {}

        config["highscore_filename"] = self._clamp(
            raw.get("highscore_filename", DEFAULTS["highscore_filename"]),
            str, None, None,
            "highscore_filename", DEFAULTS["highscore_filename"]
        )
        config["lives"] = self._clamp(
            raw.get("lives", DEFAULTS["lives"]),
            int, 1, 10, "lives", DEFAULTS["lives"]
        )
        config["pacgum"] = self._clamp(
            raw.get("pacgum", DEFAULTS["pacgum"]),
            int, 1, 1000, "pacgum", DEFAULTS["pacgum"]
        )
        config["points_per_pacgum"] = self._clamp(
            raw.get("points_per_pacgum", DEFAULTS["points_per_pacgum"]),
            int, 0, 10000, "points_per_pacgum", DEFAULTS["points_per_pacgum"]
        )
        config["points_per_super_pacgum"] = self._clamp(
            raw.get(
                "points_per_super_pacgum",
                DEFAULTS["points_per_super_pacgum"]
            ),
            int, 0, 10000,
            "points_per_super_pacgum", DEFAULTS["points_per_super_pacgum"]
        )
        config["points_per_ghost"] = self._clamp(
            raw.get("points_per_ghost", DEFAULTS["points_per_ghost"]),
            int, 0, 10000, "points_per_ghost", DEFAULTS["points_per_ghost"]
        )
        config["seed"] = self._clamp(
            raw.get("seed", DEFAULTS["seed"]),
            int, 0, 2**32 - 1, "seed", DEFAULTS["seed"]
        )
        config["level_max_time"] = self._clamp(
            raw.get("level_max_time", DEFAULTS["level_max_time"]),
            int, 10, 600, "level_max_time", DEFAULTS["level_max_time"]
        )
        config["levels"] = self._parse_levels(raw.get("levels"))

        return config

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
        # Check que la valeur soit du bon type et dans les bornes.
        # Si c'est invalide, on log un warning et on retourne le defaut.
        if not isinstance(value, expected_type):
            logger.warning(
                "Config '%s' : attendu %s, recu %s. Defaut: %s",
                key, expected_type.__name__, type(value).__name__, default
            )
            return default

        if min_val is not None and value < min_val:
            logger.warning(
                "Config '%s' : valeur %s trop petite, clampee a %s.",
                key, value, min_val
            )
            return min_val

        if max_val is not None and value > max_val:
            logger.warning(
                "Config '%s' : valeur %s trop grande, clampee a %s.",
                key, value, max_val
            )
            return max_val

        return value

    def _parse_level(self, raw_level: Any, index: int) -> dict[str, Any]:
        # Valide un niveau individuel (width + height).
        # Si c'est pas un dict, on retourne le niveau par defaut.
        default_level = DEFAULTS["levels"][0]

        if not isinstance(raw_level, dict):
            logger.warning(
                "Config : niveau %d invalide, defaut utilise.", index
            )
            return dict(default_level)

        width = self._clamp(
            raw_level.get("width", default_level["width"]),
            int, 5, 200, f"levels[{index}].width", default_level["width"]
        )
        height = self._clamp(
            raw_level.get("height", default_level["height"]),
            int, 5, 200, f"levels[{index}].height", default_level["height"]
        )

        # pour eviter les erreurs faut que les dimensions du labyrinthe
        # soit impair, donc on ajuste si besoin.
        if width % 2 == 0:
            width += 1
            logger.warning(
                "Config : levels[%d].width doit etre impair, ajuste a %d.",
                index, width
            )
        if height % 2 == 0:
            height += 1
            logger.warning(
                "Config : levels[%d].height doit etre impair, ajuste a %d.",
                index, height
            )

        return {"width": width, "height": height}

    #Jai fais avec des dict pour linstant mais on va vite le transformer pour avoir une class
    # un truc du genre LevelModel ou LevelConfig
    def _parse_levels(self, raw: Any) -> list[dict[str, Any]]:
        # Parse la liste des levels, le sujet en demande 10,
        # donc si c'est trop court on complete avec le niveau par defaut.
        min_levels = 10
        default_level = DEFAULTS["levels"][0]

        if not isinstance(raw, list) or len(raw) == 0:
            logger.warning(
                "Config : 'levels' absent ou invalide, "
                "%d niveaux par defaut generes.", min_levels
            )
            return [dict(default_level) for _ in range(min_levels)]

        levels = [self._parse_level(lvl, i) for i, lvl in enumerate(raw)]

        while len(levels) < min_levels:
            levels.append(dict(default_level))
            logger.warning(
                "Config : pas assez de niveaux, niveau par defaut ajoute "
                "(total : %d).", len(levels)
            )

        return levels