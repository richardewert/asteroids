from re import A
from tokenize import String
from turtle import width
import random
import pygame
import math
pygame.init()

screen = pygame.display.set_mode([1920/2, 1080/2], pygame.RESIZABLE)
assets = {  "window_icon": pygame.image.load("Projekt/Assets/window_icon.png").convert_alpha(),
            "player_image": pygame.image.load("Projekt/Assets/player_image.png").convert_alpha(),
            "asteroid_image": pygame.image.load("Projekt/Assets/asteroid_image.png").convert_alpha(),
            "bullet_image": pygame.image.load("Projekt/Assets/bullet_image.png").convert_alpha()}
gamestate = {"player": None, "camera": None, "all_entities": pygame.sprite.Group(), "clock": pygame.time.Clock(), "asteroides": pygame.sprite.Group(), "bullets": pygame.sprite.Group()}

ADDASTEROID = pygame.USEREVENT + 1
pygame.time.set_timer(ADDASTEROID, 250)

pygame.display.set_caption('Asteriodes by Rofdo')
pygame.display.set_icon(assets["window_icon"])

class Camera():
    def __init__(self, position = pygame.Vector2(0, 0)) -> None:
        self.position = position

    def update(self):
        d = gamestate["player"].position.__sub__(self.position)
        self.position.x += d.x/10
        self.position.y += d.y/10

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
        self.velocity = pygame.Vector2(0, 0)
        self.slow = 0
        self.weapon_cooldown = 0

    def update(self, pressed_keys):
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= 1
        self.slow = (math.pow(self.position.distance_to((0, 0))*0.0005, 5))
        speed = -0.5
        if self.slow > 1:
            speed = speed/self.slow

        if pressed_keys[pygame.K_UP]:
            dir = pygame.Vector2(0, speed)
            dir = dir.rotate(-self.rotation)
            self.velocity.x += dir.x
            self.velocity.y += dir.y
        if pressed_keys[pygame.K_DOWN]:
            dir = pygame.Vector2(0, speed)
            dir = dir.rotate(-self.rotation)
            self.velocity.x -= dir.x
            self.velocity.y -= dir.y
        if pressed_keys[pygame.K_LEFT]:
            self.rotation += 10
        if pressed_keys[pygame.K_RIGHT]:
            self.rotation -= 10
        if pressed_keys[pygame.K_SPACE] and self.weapon_cooldown == 0:
            Bullet(pygame.Vector2(self.position.x, self.position.y), int(self.rotation))
            self.weapon_cooldown = 10

        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

        self.velocity = pygame.Vector2((self.velocity.x*0.99), (self.velocity.y*0.99))
        if (self.slow * 1) > 1:
            self.velocity = pygame.Vector2(self.velocity.x / (self.slow * 1), self.velocity.y / (self.slow * 1))

class Asteroid(Entity):
    def __init__(self, size=pygame.Vector2(50, 50), position=pygame.Vector2(0, 0), rotation=0) -> None:
        s = random.randint(50, 100)
        super().__init__(assets["asteroid_image"], size=pygame.Vector2(s, s), position=position, rotation=random.randint(-180, 180))
        gamestate["asteroides"].add(self)

    def update(self):
        dir = pygame.Vector2(0, -1)
        dir = dir.rotate(-self.rotation)
        self.position.x += dir.x
        self.position.y += dir.y

        if self.position.distance_to(gamestate["camera"].position) > 2000:
            self.kill()

class Bullet(Entity):
    def __init__(self, position=pygame.Vector2(0, 0), rotation=0) -> None:
        super().__init__(assets["bullet_image"], pygame.Vector2(10, 20), position, rotation)
        gamestate["bullets"].add(self)

    def update(self):
        dir = pygame.Vector2(0, -50)
        dir = dir.rotate(-self.rotation)
        self.position.x += dir.x
        self.position.y += dir.y

        if self.position.distance_to(gamestate["camera"].position) > 2000:
            self.kill()

gamestate["player"] = Player()

def render():
    screen.fill((0, 0, 0))
    c: Camera = gamestate["camera"]
    for e in gamestate["all_entities"]:
        s: pygame.surface = e.get_image()
        r: pygame.rect = s.get_rect()
        xs, ys = screen.get_size()
        screen.blit(s, r.move((xs-s.get_width())/2, (ys-s.get_height())/2).move(e.position.x, e.position.y).move(-c.position.x, -c.position.y))

    surface = pygame.Surface(screen.get_size())
    surface.fill((255, 0, 0))
    if gamestate["player"].slow > 0.1:
        surface.set_alpha(10*gamestate["player"].slow)
        screen.blit(surface, (0, 0))
    else:
        pass

    pygame.display.flip()

def game_update() -> bool:
    run = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == ADDASTEROID:
            s = screen.get_size()
            r = random.randint(0, 3)
            if r == 0:
                Asteroid(position=pygame.Vector2(s[0]/1.5, random.randint(round(-s[1]/2), round(s[1]/2))).__add__(gamestate["camera"].position))
            elif r == 1:
                Asteroid(position=pygame.Vector2(-s[0]/1.5, random.randint(round(-s[1]/2), round(s[1]/2))).__add__(gamestate["camera"].position))
            elif r == 2:
                Asteroid(position=pygame.Vector2(random.randint(round(-s[0]/2), round(s[0]/2)), s[1]/1.5).__add__(gamestate["camera"].position))
            else:
                Asteroid(position=pygame.Vector2(random.randint(round(-s[0]/2), round(s[0]/2)), -s[1]/1.5).__add__(gamestate["camera"].position))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    gamestate["asteroides"].update()
    gamestate["player"].update(pygame.key.get_pressed())
    gamestate["bullets"].update()
    gamestate["camera"].update()

    render()
    return run

running = True
while running:
    running = game_update()
    gamestate["clock"].tick(60)

pygame.quit()
