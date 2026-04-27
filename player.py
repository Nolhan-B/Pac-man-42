class Player:
	def __init__(config: ConfigLoader) -> None:
		self.lives = config.lives
		self.__pos_x: int = None
		self.__pos_y: int = None

	def _init_player_pos(self, maze_size_x: int, maze_size_y: int) -> None:
		self.__pos_x = maze_size_x // maze_size_y
	
	def move_up(self) -> None:


	def set_position(self)
