from parser import ConfigLoader
from generate_level import Level
from ghost import Ghost, State
from player import Player


class Engine():
    def __init__(self, level_id: int, config: ConfigLoader, player: Player):
        self.level_id: int = level_id
        self.config = config
        self.player: Player = player
        self.lives = config.lives
        self.ghosts: list[Ghost] = []
        self.cheat_mode_active: bool = False
        self.running: bool = True
        self.is_paused: bool = False
        self.current_level: Level = None
        self.invincibility_timer = 0

    def load_level(self, level_id: int) -> None:
        # On charge les nouvelles données de map
        self.current_level = Level(level_id, self.config)

        # On calcule le milieu de la nouvelle map
        mid_x = self.current_level.width // 2
        mid_y = self.current_level.height // 2
        # On téléporte le joueur existant au milieu
        self.player.set_position(mid_x, mid_y)
        # Idem pour les fantômes
        self._spawn_ghosts()

    def next_level(self) -> None:
        self.level_id += 1
        if self.level_id < len(self.config.levels):
            self.load_level(self.level_id)
        else:
            print("Congrats ! You finished te game !")
            self.running = False

    def _spawn_ghosts(self) -> None:
        w = self.current_level.width
        h = self.current_level.height

        self.ghosts.clear()
        # On spawn a(x, y) et enregistre le spawn (x, y) pour le mode DEAD
        # Haut-Gauche
        self.ghosts.append(Ghost("red", 1, 1, self, (1, 1)))
        # Haut-Droit
        self.ghosts.append(Ghost("blue", w - 2, 1, self, (w - 2, 1)))
        # Bas-Gauche
        self.ghosts.append(Ghost("green", 1, h - 2, self, (1, h - 2)))
        # Bas-Droit
        self.ghosts.append(Ghost("purple", w - 2, h - 2, self, (w - 2, h - 2)))

    def take_pac_gum(self) -> None:
        y: int = self.player.get_pos_y()
        x: int = self.player.get_pos_x()
        type_gum: str = self.current_level.check_and_eat_gum(y, x)
        self._process_gum(type_gum)

    def _process_gum(self, type_gum: str) -> None:
        if type_gum == "SUPER":
            self.player.add_score(self.config.points_per_super_pacgum)
            self.current_level.total_gum -= 1
            self._check_win()
            for ghost in self.ghosts:
                ghost.force_u_turn()
                
        elif type_gum == "NORMAL":
            self.player.add_score(self.config.points_per_pacgum)
            self.current_level.total_gum -= 1
            self._check_win()
        elif type_gum == "NONE":
            return

    def _check_win(self) -> None:
        # Condition de Victoire
        if self.current_level.total_gum == 0:
            print("Niveau Terminé !")
            self.next_level()

    def _check_loose(self) -> None:
        # Condition de Défaite
        if self.player.lives <= 0:
            print("Game Over...")
            self.running = False  # Pour arrêter la boucle de jeu

    def _check_collisions(self) -> None:

        if self.invincibility_timer > 0:
            return
        px: int = self.player.get_pos_x()
        py: int = self.player.get_pos_y()

        for ghost in self.ghosts:
            gx: int = ghost.pos_x
            gy: int = ghost.pos_y

            dist_carree = (gx - px)**2 + (gy - py)**2

            if dist_carree < 0.5:  # 0.7 au carré ça fait environ 0.5
                self._handle_collision(ghost)

    def _handle_collision(self, ghost: "Ghost") -> None:
        if ghost.state == State.CHASE:
            if self.invincibility_timer <= 0:
                self.invincibility_timer = 180
                self.player.lose_life()
                self._check_loose()

        elif ghost.state == State.FRIGHTENED:
            self.player.add_score(self.config.points_per_ghost)
            ghost.set_state(State.DEAD)


