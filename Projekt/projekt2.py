from re import A
from tokenize import String
from turtle import width
import pygame
pygame.init()

screen = pygame.display.set_mode([1920/2, 1080/2], pygame.RESIZABLE)
assets = {  "window_icon": pygame.image.load("Projekt/Assets/window_icon.png").convert_alpha(),
            "player_image": pygame.image.load("Projekt/Assets/player_image.png").convert_alpha(),
            "asteroid_image": pygame.image.load("Projekt/Assets/asteroid_image.png").convert_alpha()}
gamestate = {"player": None, "camera": None, "all_entities": pygame.sprite.Group(), "clock": pygame.time.Clock()}

pygame.display.set_caption('Asteriodes by Rofdo')
pygame.display.set_icon(assets["window_icon"])

class Camera():
    def __init__(self, position = pygame.Vector2(0, 0)) -> None:
        self.position = position

gamestate["camera"] = Camera()

class Entity(pygame.sprite.Sprite):
    def __init__(self, image: pygame.surface, size = pygame.Vector2(50, 50), position = pygame.Vector2(0, 0), rotation = 0) -> None:
        super().__init__()
        gamestate["all_entities"].add(self)
        self.rotation = rotation
        self.position = position
        self.size = size
        self.surf = image
        self.surf.set_colorkey((0, 0, 0), pygame.RLEACCEL)

    def get_image(self) -> pygame.surface:
        image = pygame.transform.scale(self.surf, (self.size.x, self.size.y))
        image = pygame.transform.rotate(image, self.rotation)
        return image

    def update():
        pass

class Player(Entity):
    def __init__(self):
        super().__init__(assets["player_image"], position=pygame.Vector2(0, 0))

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_UP]:
            dir = pygame.Vector2(0, -1)
            dir = dir.rotate(-self.rotation)
            self.position.x += dir.x
            self.position.y += dir.y
        if pressed_keys[pygame.K_DOWN]:
            pass
        if pressed_keys[pygame.K_LEFT]:
            self.rotation += 1
        if pressed_keys[pygame.K_RIGHT]:
            self.rotation -= 1

class Asteroid(Entity):
    def __init__(self, size=pygame.Vector2(50, 50), position=pygame.Vector2(0, 0), rotation=0) -> None:
        super().__init__(assets["asteroid_image"], size, position, rotation)

gamestate["player"] = Player()

def render():
    screen.fill((0, 0, 0))
    c: Camera = gamestate["camera"]
    for e in gamestate["all_entities"]:
        s: pygame.surface = e.get_image()
        r: pygame.rect = s.get_rect()
        xs, ys = screen.get_size()
        screen.blit(s, r.move((xs-s.get_width())/2, (ys-s.get_height())/2).move(e.position.x, e.position.y).move(-c.position.x, -c.position.y))

    pygame.display.flip()

t = (Asteroid(position=pygame.Vector2(100, 100)), Asteroid())
def game_update() -> bool:
    run = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    gamestate["player"].update(pygame.key.get_pressed())

    render()
    return run

running = True
while running:
    running = game_update()
    gamestate["clock"].tick(60)

pygame.quit()
