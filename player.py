class Player:
	def __init__(self, config: ConfigLoader) -> None:
		self.lives = config.lives
		self._pos_x: int = None
		self._pos_y: int = None
		self.score: int = 0

	def _init_player_pos(self, maze_size_x: int, maze_size_y: int) -> None:
		self._pos_x = maze_size_x // 2
		self._pos_y = maze_size_y // 2
	
	def move_up(self) -> None:
		self._pos_y += 1

	def move_down(self) -> None:
		self._pos_y -= 1

	def move_right(self) -> None:
		self._pos_x += 1

	def move_left(self) -> None:
		self._pos_x -= 1

	def set_position(self, x: int, y: int) -> None:
		self._pos_x = x
		self._pos_y = y
	
	def get_position(self) -> tuple[int, int]:
		return (self._pos_x, self._pos_y)

	def get_pos_x(self) -> int:
		return self._pos_x

	def get_pos_y(self) -> int:
		return self._pos_y

	def lose_life(self) -> None:
		if self.lives == 0:
			logger.warning("Player can't lose life, already at 0 !")
		else:
			self.lives -= 1

	def add_score(self, amount: int) -> None:
		self.score += amount