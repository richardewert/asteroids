from asyncio import shield
from re import A
from select import select
from tokenize import String
from turtle import width
import random
import pygame
import math
pygame.init()

screen = pygame.display.set_mode([1920/2, 1080/2], pygame.RESIZABLE)
assets = {  "window_icon": pygame.image.load("Projekt/Assets/window_icon.png").convert(),
            "player_image": pygame.image.load("Projekt/Assets/player_image.png").convert(),
            "asteroid_image": pygame.image.load("Projekt/Assets/asteroid_image.png").convert(),
            "bullet_image": pygame.image.load("Projekt/Assets/bullet_image.png").convert()}
gamestate = {"player": None, "camera": None, "all_entities": pygame.sprite.Group(), "clock": pygame.time.Clock(), "asteroides": pygame.sprite.Group(), "bullets": pygame.sprite.Group(), "running": False, "ui": pygame.sprite.Group()}

ADDASTEROID = pygame.USEREVENT + 1
pygame.time.set_timer(ADDASTEROID, 100)

pygame.display.set_caption('Asteriodes by Rofdo')
pygame.display.set_icon(assets["window_icon"])

class bar(pygame.sprite.Sprite):
    def __init__(self, position = pygame.Vector2(50, 80), size = pygame.Vector2(100, 10), color = (0, 255, 0)) -> None:
        super().__init__()
        gamestate["ui"].add(self)
        self.position = position
        self.size = size
        self.value = 100
        self.color = color

    def render(self):
        s = screen.get_size()
        smaller_size = pygame.Vector2(self.size[0] - 5, self.size[1] - 5)
        pygame.draw.rect(screen, (255, 255, 255), (s[0] * self.position[0]/100 - self.size[0]/2, s[1] * self.position[1]/100 - self.size[1]/2, self.size[0], self.size[1]))
        pygame.draw.rect(screen, self.color, (s[0] * self.position[0]/100 - smaller_size[0]/2, s[1] * self.position[1]/100 - smaller_size[1]/2, smaller_size[0] * self.value/100, smaller_size[1]))

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
        self.shield = 100
        self.health = 100
        self.shield_bar = bar(pygame.Vector2(50, 90), pygame.Vector2(300, 30), (30,144,255))
        self.health_bar = bar(pygame.Vector2(50, 95), pygame.Vector2(300, 30), (0,255,0))

    def update(self, pressed_keys):
        if self.health <= 0:
            gamestate["running"] = False

        if self.shield < 100:
            self.shield += 0.1

        self.shield_bar.value = self.shield
        self.health_bar.value = self.health

        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= 1
        self.slow = (math.pow(self.position.distance_to((0, 0))*0.0005, 5))
        speed = -0.5
        if self.slow > 1:
            speed = speed/self.slow

        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            dir = pygame.Vector2(0, speed)
            dir = dir.rotate(-self.rotation)
            self.velocity.x += dir.x
            self.velocity.y += dir.y
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            dir = pygame.Vector2(0, speed)
            dir = dir.rotate(-self.rotation)
            self.velocity.x -= dir.x
            self.velocity.y -= dir.y
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            self.rotation += 10
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            self.rotation -= 10
        if pressed_keys[pygame.K_SPACE] and self.weapon_cooldown == 0:
            Bullet(pygame.Vector2(self.position.x, self.position.y), int(self.rotation))
            self.weapon_cooldown = 10

        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

        self.velocity = pygame.Vector2((self.velocity.x*0.99), (self.velocity.y*0.99))
        if (self.slow * 1) > 1:
            self.velocity = pygame.Vector2(self.velocity.x / (self.slow * 1), self.velocity.y / (self.slow * 1))

    def hit(self, damage: int):
        self.shield -= damage
        if self.shield < 0:
            self.health += self.shield
            self.shield = 0


class Asteroid(Entity):
    def __init__(self, size=pygame.Vector2(50, 50), position=pygame.Vector2(0, 0), rotation=0) -> None:
        super().__init__(assets["asteroid_image"], size=size, position=position, rotation=rotation)
        gamestate["asteroides"].add(self)

    def split(self):
            Asteroid(pygame.Vector2(self.size[0]/2, self.size[1]/2), pygame.Vector2(self.position[0], self.position[1]), int(self.rotation + 90))
            Asteroid(pygame.Vector2(self.size[0]/2, self.size[1]/2), pygame.Vector2(self.position[0], self.position[1]), int(self.rotation - 90))
            self.kill()

    def update(self):
        dir = pygame.Vector2(0, -1)
        dir = dir.rotate(-self.rotation)
        self.position.x += dir.x
        self.position.y += dir.y

        for b in gamestate["bullets"]:
            if self.position.distance_to(b.position) < self.size[0]*0.9:
                b.hit()
                self.split()

        if gamestate["player"].position.distance_to(self.position) < self.size[0] * 0.9 + 10:
            gamestate["player"].hit(self.size.y/10)
            self.split()

        if self.position.distance_to(gamestate["camera"].position) > 2000 or self.size[0] < 30:
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

    def hit(self):
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

    for ui in gamestate["ui"]:
        ui.render()

    surface = pygame.Surface(screen.get_size())
    surface.fill((255, 0, 0))
    if gamestate["player"].slow > 0.1:
        surface.set_alpha(10*gamestate["player"].slow)
        screen.blit(surface, (0, 0))
    else:
        pass

    pygame.display.flip()

def game_update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gamestate["running"] = False
        elif event.type == ADDASTEROID:
            rs = random.randint(50, 100)
            s = screen.get_size()
            r = random.randint(0, 3)
            if r == 0:
                Asteroid(position=pygame.Vector2(s[0]/1.5, random.randint(round(-s[1]/2), round(s[1]/2))).__add__(gamestate["camera"].position), size=pygame.Vector2(rs, rs), rotation=random.randint(0, 360))
            elif r == 1:
                Asteroid(position=pygame.Vector2(-s[0]/1.5, random.randint(round(-s[1]/2), round(s[1]/2))).__add__(gamestate["camera"].position), size=pygame.Vector2(rs, rs), rotation=random.randint(0, 360))
            elif r == 2:
                Asteroid(position=pygame.Vector2(random.randint(round(-s[0]/2), round(s[0]/2)), s[1]/1.5).__add__(gamestate["camera"].position), size=pygame.Vector2(rs, rs), rotation=random.randint(0, 360))
            else:
                Asteroid(position=pygame.Vector2(random.randint(round(-s[0]/2), round(s[0]/2)), -s[1]/1.5).__add__(gamestate["camera"].position), size=pygame.Vector2(rs, rs), rotation=random.randint(0, 360))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gamestate["running"] = False

    gamestate["asteroides"].update()
    gamestate["player"].update(pygame.key.get_pressed())
    gamestate["bullets"].update()
    gamestate["camera"].update()

    render()

gamestate["running"] = True
while gamestate["running"]:
    game_update()
    gamestate["clock"].tick(60)

pygame.quit()
