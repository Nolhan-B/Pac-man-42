from parser import ConfigLoader

class Engine():
	def __init__(self, level_id : int, config : ConfigLoader, player: Player,):
		self.level: int = level_id
		self.config = config
		self.player : Player = player
		self.lives = config.lives
		self.ghost: Ghost = ghost
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
        # On téléporte le joueur existant au milieu, sans toucher à ses vies/score
        self.player.set_position(mid_x, mid_y
        # Idem pour les fantômes
        self._spawn_ghosts()