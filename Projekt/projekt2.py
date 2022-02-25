from tokenize import String
from turtle import width
import pygame
pygame.init()

screen = pygame.display.set_mode([1920/2, 1080/2], pygame.RESIZABLE)
assets = {  "window_icon": pygame.image.load("Assets/window_icon.png").convert_alpha(),
            "player_image": pygame.image.load("Assets/player_image.png").convert_alpha()}
gamestate = {"player": None, "camera": None}

pygame.display.set_caption('Asteriodes by Rofdo')
pygame.display.set_icon(assets["window_icon"])

class Camera():
    def __init__(self, position = pygame.Vector2(0, 0)) -> None:
        self.position = position
gamestate["camera"] = Camera()

class Entity(pygame.sprite.Sprite):
    def __init__(self, image: pygame.surface, size = pygame.Vector2(50, 50), position = pygame.Vector2(0, 0), rotation = 0) -> None:
        self.rotation = rotation
        self.position = position
        self.size = size
        self.surf = image
        self.surf.set_colorkey((0, 0, 0), pygame.RLEACCEL)
    
    def get_image(self) -> pygame.surface:
        image = pygame.transform.scale(self.surf, (self.size.x, self.size.y))
        image = pygame.transform.rotate(image, self.rotation)
        return image

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

gamestate["player"] = Player()

def render():
    c: Camera = gamestate["camera"]
    p: Player = gamestate["player"]
    s: pygame.surface = p.get_image()
    r: pygame.rect = s.get_rect()
    screen.fill((0, 0, 0))
    xs, ys = screen.get_size()
    screen.blit(s, r.move((xs-s.get_width())/2, (ys-s.get_height())/2).move(p.position.x, p.position.y).move(-c.position.x, -c.position.y))

    pygame.display.flip()

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

pygame.quit()
