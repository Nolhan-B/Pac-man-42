import pygame
import sys
# import random
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("coucou")

# controler les fps
clock = pygame.time.Clock()

x = 0
y = 0

while True:

    # 1. EVENTS : on lit ce qui s'est passe depuis la derniere frame
    for event in pygame.event.get():

        screen.fill((0, 0, 0))  # RGB : (0, 0, 0) = noir

        p = pygame.draw.rect(screen, (255, 0, 0), (x, y, 100, 100))    # Ici on dessinerait les trucs du jeu...

        # L'utilisateur a ferme la fenetre avec la croix
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # L'utilisateur a appuye sur une touche
        if event.type == pygame.KEYDOWN:
            match (event.key):
                case pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # case pygame.K_SPACE:
                #     c1, c2, c3 = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                #     screen.fill((c1, c2, c3))
                case pygame.K_UP:
                    y -= 10
                case pygame.K_DOWN:
                    y += 10
                case pygame.K_LEFT:
                    x -= 10
                case pygame.K_RIGHT:
                    x += 10

    # 2. DESSIN : on remplit l'ecran d'une couleur (ici noir)
    # Si on fait pas ca, les frames precedentes restent visibles
    # screen.fill((0,0,0))  # RGB : (0, 0, 0) = noir

    # 3. FLIP : on envoie ce qu'on a dessine a l'ecran
    # Sans ca, l'ecran reste vide
    pygame.display.flip()

    # 4. FPS : on limite a 60 frames par seconde
    clock.tick(60)
