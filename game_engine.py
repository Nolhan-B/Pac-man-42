from parser import ConfigLoader
from generate_level import Level
from ghost import Ghost


class Engine():
    def __init__(self, level_id: int, config: ConfigLoader, player: Player):
        self.level: int = level_id
        self.config = config
        self.player: "Player" = player
        self.lives = config.lives
        self.ghosts: list[Ghost] = []
        self.cheat_mode_active: bool = False
        self.running: bool = True
        self.is_paused: bool = False
        self.current_level: Level = None

    def load_level(self, level_id: int):
        # On charge les nouvelles données de map
        self.current_level = Level(level_id, self.config)

        # On calcule le milieu de la nouvelle map
        mid_x = self.current_level.width // 2
        mid_y = self.current_level.height // 2
        # On téléporte le joueur existant au milieu
        self.player.set_position(mid_x, mid_y)
        # Idem pour les fantômes
        self._spawn_ghosts()

    def _spawn_ghosts(self):

        w = self.current_level.width
        h = self.current_level.height

        self.ghosts.clear()
        # Coin Haut-Gauche
        self.ghosts.append(Ghost("rouge", 0, 0))
        # Coin Haut-Droit
        self.ghosts.append(Ghost("bleu", w - 1, 0))
        # Coin Bas-Gauche
        self.ghosts.append(Ghost("vert", 0, h - 1))
        # Coin Bas-Droit
        self.ghosts.append(Ghost("violet", w - 1, h - 1))

    def _check_pac_gum(self):

