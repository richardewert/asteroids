from cmath import phase
import random
from re import S
from turtle import reset
import pygame
import math
pygame.init()

screen = pygame.display.set_mode([1920/2, 1080/2], pygame.RESIZABLE)
assets = {  "window_icon": pygame.image.load("Projekt/Assets/window_icon.png").convert(),
            "player_image": pygame.image.load("Projekt/Assets/player_image.png").convert(),
            "asteroid_image": pygame.image.load("Projekt/Assets/asteroid_image.png").convert(),
            "bullet_image": pygame.image.load("Projekt/Assets/bullet_image.png").convert(),
            "shot_sound": pygame.mixer.Sound ("Projekt/Assets/laser.mp3"),
            "asteroid_hit_sound": pygame.mixer.Sound ("Projekt/Assets/asteroid_hit_sound.wav"),
            "rocket_image": pygame.image.load("Projekt/Assets/rocket_image.png").convert(),
            "particle_image": pygame.image.load("Projekt/Assets/particle_image.png").convert(),
            "pointer_image": pygame.image.load("Projekt/Assets/pointer_image.png").convert()}
gamestate = {"player": None, "camera": None, "all_entities": pygame.sprite.Group(), "clock": pygame.time.Clock(), "asteroides": pygame.sprite.Group(), "bullets": pygame.sprite.Group(), "running": False, "ui": pygame.sprite.Group(), "menu": True, "menu_ui": pygame.sprite.Group(), "enemies": pygame.sprite.Group(), "particle_systems": pygame.sprite.Group(), "particles": pygame.sprite.Group()}

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

class text(pygame.sprite.Sprite):
    def __init__(self, text, position = pygame.Vector2(50, 80), size = 24, color = (255, 255, 255)) -> None:
        super().__init__()
        self.text = text
        self.position = position
        self.size = size
        self.color = color

    def render(self):
        font = pygame.font.SysFont(None, self.size)
        s = screen.get_size()
        img = font.render(self.text, True, self.color)
        ss = img.get_size()
        screen.blit(img, (s[0] * self.position[0]/100 - ss[0]/2, s[1] * self.position[1]/100 - ss[1]/2))

class Camera():
    def __init__(self, position = pygame.Vector2(0, 0)) -> None:
        self.position = position

    def update(self):
        d = gamestate["player"].position.__sub__(self.position)
        self.position.x += d.x/10
        self.position.y += d.y/10

gamestate["camera"] = Camera()

class ParticleSystem(pygame.sprite.Sprite):
    def __init__(self, position = pygame.Vector2(0, 0), direction = 0) -> None:
        super().__init__()
        gamestate["particle_systems"].add(self)
        self.position = position
        self.direction = direction
        self.particles = []
        self.on = True

    def update(self):
        if self.on:
            s = random.randint(15, 50)
            self.particles.append(Particle(position=self.position.xy, rotation=self.direction + random.randint(-10, 10), speed=random.randint(5, 10), size=pygame.Vector2(s, s), lifetime=random.randint(30, 60)))

class Entity(pygame.sprite.Sprite):
    def __init__(self, image: pygame.surface, size = pygame.Vector2(50, 50), position = pygame.Vector2(0, 0), rotation = 0) -> None:
        super().__init__()
        gamestate["all_entities"].add(self)
        self.rotation = rotation
        self.position = position
        self.size = size
        self.surf = image
        self.surf.set_colorkey((0, 0, 0), pygame.RLEACCEL)
        self.opacity = 0;

    def get_image(self) -> pygame.surface:
        image = pygame.transform.scale(self.surf, (self.size.x, self.size.y))
        image = pygame.transform.rotate(image, self.rotation)
        image.set_alpha(255*(100-self.opacity)*0.01);
        return image

    def update(self):
        pass

class Particle(Entity):
    def __init__(self, size=pygame.Vector2(50, 50), position=pygame.Vector2(0, 0), rotation=0, speed=10, lifetime=60) -> None:
        super().__init__(assets["particle_image"], size, position, rotation)
        gamestate["particles"].add(self)
        self.maxlifetime = lifetime
        self.lifetime = 0
        self.velocity = pygame.Vector2()
        dir = pygame.Vector2(0, speed)
        dir = dir.rotate(-self.rotation)
        self.velocity += dir.xy

    def update(self):
        self.opacity = self.lifetime/self.maxlifetime*100
        self.position += self.velocity.xy
        self.velocity = self.velocity*0.99

        self.lifetime += 1
        if self.lifetime >= self.maxlifetime:
            self.kill()

class Pointer(Entity):
    def __init__(self, size=pygame.Vector2(50, 50), position=pygame.Vector2(0, 0), rotation=0) -> None:
        super().__init__(assets["pointer_image"], size, position, rotation)
        self.base_size = size
        self.phase = 0

    def update(self, pl_position: pygame.Vector2(), slow):
        if not slow == 0:
            self.opacity = 100 - 100*slow
        self.rotation = math.atan2(pl_position.x, pl_position.y)*180/math.pi
        dir = pygame.Vector2(0, 200)
        dir = dir.rotate(-self.rotation + 180)
        self.position = pl_position.xy + dir.xy
        self.rotation += 90
        self.phase += 1
        scale = math.sin(self.phase/10)/2 + 2
        self.size = self.base_size.xy * scale


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
        self.score = 0
        self.booster = ParticleSystem(self.position.xy, self.rotation)
        self.pointer = Pointer(size=pygame.Vector2(20, 50))

    def update(self, pressed_keys):
        self.booster.direction = self.rotation
        dir = pygame.Vector2(0, 20)
        dir = dir.rotate(-self.rotation)
        self.booster.position = self.position.xy + dir.xy
        self.score += 1
        if self.health <= 0:
            reset()

        if self.shield < 100:
            self.shield += 0.1

        self.shield_bar.value = self.shield
        self.health_bar.value = self.health

        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= 1

        self.slow = (math.pow(self.position.distance_to((0, 0))*0.00025, 5))
        speed = -0.5
        if self.slow > 1:
            speed = speed/self.slow

        self.booster.on = False
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            dir = pygame.Vector2(0, speed)
            dir = dir.rotate(-self.rotation)
            self.velocity += dir.xy
            self.booster.on = True
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            dir = pygame.Vector2(0, speed)
            dir = dir.rotate(-self.rotation)
            self.velocity -= dir.xy
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            self.rotation += 10
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            self.rotation -= 10
        if (pressed_keys[pygame.K_SPACE] or pygame.mouse.get_pressed(3)[0] == True) and self.weapon_cooldown == 0:
            s = screen.get_size()
            goal = gamestate["camera"].position.xy
            goal.x += pygame.mouse.get_pos()[0] - s[0]/2
            goal.y += pygame.mouse.get_pos()[1] - s[1]/2
            Bullet(self.position.xy, math.atan2(goal.x - self.position.x, goal.y - self.position.y) * 57.296 + 180)
            self.weapon_cooldown = 10

        self.position += self.velocity.xy
        self.velocity = self.velocity*0.99
        if (self.slow * 1) > 1:
            self.velocity = pygame.Vector2(self.velocity.x / (self.slow * 1), self.velocity.y / (self.slow * 1))

        self.pointer.update(self.position.xy, self.slow)

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
            assets["asteroid_hit_sound"].set_volume(100/self.position.distance_to(gamestate["camera"].position))
            pygame.mixer.Channel(1).play(assets["asteroid_hit_sound"])
            Asteroid(self.size / 2, self.position.xy, int(self.rotation + 45))
            Asteroid(self.size / 2, self.position.xy, int(self.rotation - 45))
            self.kill()

    def update(self):
        dir = pygame.Vector2(0, -1)
        dir = dir.rotate(-self.rotation)
        self.position += dir.xy

        for b in gamestate["bullets"]:
            if self.position.distance_to(b.position) < self.size[0]*0.9:
                b.hit()
                self.split()

        if gamestate["player"].position.distance_to(self.position) < self.size[0] * 0.9 + 10:
            gamestate["player"].hit(self.size.y/5)
            self.split()

        if self.position.distance_to(gamestate["camera"].position) > 2000 or self.size[0] < 30:
            self.kill()

class Enemy(Entity):
    def __init__(self, size=pygame.Vector2(50, 50), position=pygame.Vector2(0, 0), rotation=0) -> None:
        super().__init__(assets["rocket_image"], size, position, rotation)
        gamestate["enemies"].add(self)
        self.velocity = pygame.Vector2(0, 0)

    def update(self):
        dir = pygame.Vector2(gamestate["player"].position.xy.__sub__(self.position)).normalize()
        if self.position.distance_to(gamestate["player"].position) > 5000:
            self.kill()

        self.velocity += dir.xy
        self.position += self.velocity.xy
        self.velocity = self.velocity*0.98

        self.rotation = math.atan2(self.velocity.x, self.velocity.y)*180/3.141 + 180

        for e in gamestate["enemies"]:
            if self.position.distance_to(e.position) < self.size[0]*0.9 and not e == self:
                self.velocity += (e.position.xy - self.position.xy)*-1

        for b in gamestate["bullets"]:
            if self.position.distance_to(b.position) < self.size[0]*0.9:
                b.hit()
                self.kill()

        for e in gamestate["enemies"]:
            if self.position.distance_to(e.position) < self.size[0]*0.9 and not e == self:
                dir = e.position.xy - self.position.xy
                self.velocity -= dir.xy/2

        for a in gamestate["asteroides"]:
            if self.position.distance_to(a.position) < self.size[0]*0.9:
                a.split()
                self.kill()

        if gamestate["player"].position.distance_to(self.position) < self.size[0] * 0.9 + 10:
            gamestate["player"].hit(self.size.y/5)
            self.kill()

class Bullet(Entity):
    def __init__(self, position=pygame.Vector2(0, 0), rotation=0) -> None:
        super().__init__(assets["bullet_image"], pygame.Vector2(10, 20), position, rotation)
        gamestate["bullets"].add(self)
        assets["shot_sound"].set_volume(random.randint(30, 50)/100)
        pygame.mixer.Channel(0).play(assets["shot_sound"])

    def update(self):
        dir = pygame.Vector2(0, -50)
        dir = dir.rotate(-self.rotation)
        self.position += dir.xy

        if self.position.distance_to(gamestate["camera"].position) > 2000:
            self.kill()

    def hit(self):
        self.kill()

gamestate["player"] = Player()
def render():
    gamestate["score_text"].text = "Score: " + str(gamestate["player"].score)
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
        surface.set_alpha(20*gamestate["player"].slow)
        screen.blit(surface, (0, 0))
    else:
        pass

    if gamestate["menu"]:
        for ui in gamestate["menu_ui"]:
            ui.render()

    pygame.display.flip()

def get_spawning_pos() -> pygame.Vector2():
    s = screen.get_size()
    r = random.randint(0, 3)
    if r == 0:
        return pygame.Vector2(s[0]/1.5, random.randint(round(-s[1]/2), round(s[1]/2)))
    elif r == 1:
        return pygame.Vector2(-s[0]/1.5, random.randint(round(-s[1]/2), round(s[1]/2)))
    elif r == 2:
        return pygame.Vector2(random.randint(round(-s[0]/2), round(s[0]/2)), s[1]/1.5)
    else:
        return pygame.Vector2(random.randint(round(-s[0]/2), round(s[0]/2)), -s[1]/1.5)

def add_asteroid():
    rs = random.randint(50, 100)
    Asteroid(position=get_spawning_pos().__add__(gamestate["camera"].position), size=pygame.Vector2(rs, rs), rotation=random.randint(0, 360))

def game_update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gamestate["running"] = False
        elif event.type == ADDASTEROID:
            if bool(random.getrandbits(1)):
                add_asteroid()
            else:
                max = math.ceil(gamestate["player"].score/1000)
                if max > 10:
                    max = 10
                if len(gamestate["enemies"]) < max:
                    Enemy(position=get_spawning_pos().__add__(gamestate["camera"].position))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gamestate["menu"] = True

    gamestate["asteroides"].update()
    gamestate["enemies"].update()
    gamestate["player"].update(pygame.key.get_pressed())
    gamestate["bullets"].update()
    gamestate["camera"].update()
    gamestate["particle_systems"].update()
    gamestate["particles"].update()

    render()

def menu_update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gamestate["running"] = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gamestate["menu"] = False

    render()

def reset():
    {"player": None, "camera": None, "all_entities": pygame.sprite.Group(), "clock": pygame.time.Clock(), "asteroides": pygame.sprite.Group(), "bullets": pygame.sprite.Group(), "running": False, "ui": pygame.sprite.Group(), "menu": True, "menu_ui": pygame.sprite.Group(), "enemies": pygame.sprite.Group(), "player": None}
    gamestate["camera"] = Camera()
    gamestate["player"] = Player()
    gamestate["menu_ui"].add(text("PRESS SPACE TO UNPAUSE", (50, 40), 50))
    gamestate["running"] = True

pygame.mixer.set_num_channels(10)
gamestate["menu_ui"].add(text("PRESS SPACE TO UNPAUSE", (50, 40), 50))
gamestate["score_text"] = text("Score: 0", (50, 5), 50)
gamestate["ui"].add(gamestate["score_text"])
gamestate["running"] = True

def reset():
    gamestate["player"].kill()
    gamestate["player"] = Player()

while gamestate["running"]:
    if not gamestate["menu"]:
        game_update()
    else:
        menu_update()
    gamestate["clock"].tick(60)

pygame.quit()
