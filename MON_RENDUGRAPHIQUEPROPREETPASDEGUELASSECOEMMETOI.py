import pygame
from constants import Direction
import sys
from player import Player
from game_engine import Engine
from parser import ConfigLoader
from generate_level import Level


class Renderer:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.header = 150
        self.footer = 75
        self.side_margin = 150
        self.c_s = 0
        # On essaie de charger la vraie image
        try:
            self.pacman_sprite = pygame.image.load("assets/pacman.png").convert_alpha()
        # Si elle n'existe pas, on crée un carré jaune de secours pour éviter le crash
        except FileNotFoundError:
            self.pacman_sprite = pygame.Surface((30, 30))
            self.pacman_sprite.fill((255, 255, 0))

    def draw_all(self, engine):
        # Remplir de noir
        self.screen.fill((0, 0, 0))

        # Dessin du maze
        self._draw_maze(engine.current_level.layout)

        # # Dessine les item (pacgum)(va etre implementee dans draw maze)
        # self._draw_items(engine.current_level)

        # Dessine les fantomes
        for ghost in engine.ghosts:
            self.draw_ghost(ghost)

        self.draw_pac_man(engine.player, engine.current_level.layout)

        # Affichage du resultat et rafraichissement du rendu
        pygame.display.flip()

    def draw_pac_man(self, player, layout):
        px, py = player.get_position()
        if px is None:
            return

        offset_x, offset_y = 0, 0
        
        # On glisse en avant UNIQUEMENT si le moteur autorise le mouvement
        if player.current_direction is not None and player._can_move(player.current_direction, layout):
            progress = player.move_timer / 30.0
            
            if player.current_direction == Direction.NORTH: offset_y = -progress * self.c_s
            elif player.current_direction == Direction.SOUTH: offset_y = progress * self.c_s
            elif player.current_direction == Direction.WEST: offset_x = -progress * self.c_s
            elif player.current_direction == Direction.EAST: offset_x = progress * self.c_s

        sprite_resized = pygame.transform.smoothscale(
            self.pacman_sprite, (self.c_s, self.c_s))

        rotations = {
            Direction.EAST: 0, Direction.NORTH: 90, 
            Direction.WEST: 180, Direction.SOUTH: 270
        }

        angle = rotations.get(player.current_direction, 0)
        sprite_final = pygame.transform.rotate(sprite_resized, angle)

        #  On applique l'offset calculé
        pixel_x = px * self.c_s + (self.side_margin // 2) + offset_x
        pixel_y = py * self.c_s + self.header + offset_y
        
        self.screen.blit(sprite_final, (pixel_x, pixel_y))

    def _draw_maze(self, layout):
        # On parcourt chaque case du labyrinthe
        for y, row in enumerate(layout):
            for x, cell in enumerate(row):
                # Calcul de la position de base en pixels
                ox = x * self.c_s + (self.side_margin // 2)
                oy = y * self.c_s + self.header

                # dessin des murs
                self._draw_walls(ox, oy, cell)
                # dessin des pacgum
                self._draw_items(ox, oy, cell)

    def _draw_walls(self, ox, oy, cell):
        color = (33, 33, 255)
        thickness = 2

        # North
        if cell & 1:
            pygame.draw.line(self.screen, color,
                             (ox, oy),
                             (ox + self.c_s, oy), thickness)
        # East
        if cell & 2:
            pygame.draw.line(self.screen, color,
                             (ox + self.c_s, oy),
                             (ox + self.c_s, oy + self.c_s), thickness)
        # South
        if cell & 4:
            pygame.draw.line(self.screen, color,
                             (ox, oy + self.c_s),
                             (ox + self.c_s, oy + self.c_s), thickness)
        # West
        if cell & 8:
            pygame.draw.line(self.screen, color, (ox, oy),
                             (ox, oy + self.c_s), thickness)

        # Bloc plein (murs extérieurs)
        if cell == 15:
            pygame.draw.rect(self.screen, color, (ox, oy, self.c_s, self.c_s))

    def _draw_items(self, ox, oy, cell):
        center = (ox + self.c_s // 2, oy + self.c_s // 2)
        gum_color = (255, 184, 174)

        if cell & 16:  # NORMAL_GUM
            pygame.draw.circle(self.screen, gum_color, center, 3)

        if cell & 32:  # SUPER_GUM
            pygame.draw.circle(self.screen, gum_color, center, 8)

    def draw_ghost(self, ghost):
        # On récupère la position
        gx, gy = ghost.get_position()

        pixel_x = gx * self.c_s + (self.side_margin // 2) + (self.c_s // 2)
        pixel_y = gy * self.c_s + self.header + (self.c_s // 2)
        pygame.draw.circle(self.screen, ghost.color, (int(pixel_x), int(pixel_y)), self.c_s // 2.5)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config_file.json>")
        raise SystemExit(1)

    # Chargement de la config
    config = ConfigLoader(sys.argv[1])
    config.load()

    player = Player(config)
    engine = Engine(0, config, player)
    engine.load_level(0)

    # Definition de la taille des cases selon la taille du niveau
    C_S = 30
    WINDOW_W = (engine.current_level.width * C_S) + 150
    WINDOW_H = (engine.current_level.height * C_S) + 150 + 75

    # Creation de la fenetre
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))

    renderer = Renderer(screen, config)
    renderer.c_s = C_S

    clock = pygame.time.Clock()

    # Lancement du moteur du jeu puis du moteur graphique
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Implementation des controles
            if event.type == pygame.KEYDOWN:
                from constants import Direction
                if event.key == pygame.K_UP:
                    player.set_next_direction(Direction.NORTH)
                elif event.key == pygame.K_DOWN:
                    player.set_next_direction(Direction.SOUTH)
                elif event.key == pygame.K_LEFT:
                    player.set_next_direction(Direction.WEST)
                elif event.key == pygame.K_RIGHT:
                    player.set_next_direction(Direction.EAST)

        # Lancement du moteur de jeu
        engine.run()
        # Mise a jour du rendu
        renderer.draw_all(engine)

        clock.tick(60)

if __name__ == "__main__":
    main()