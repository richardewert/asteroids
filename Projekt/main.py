import random
import math
from time import time
from turtle import position, update
from numpy import size
import pygame
pygame.init()

screen = pygame.display.set_mode([1920/2, 1080/2], pygame.RESIZABLE)
assets =    {   "window_icon": pygame.image.load("Projekt/Assets/window_icon.png").convert(),
                "player_image": pygame.image.load("Projekt/Assets/player_image.png").convert(),
                "asteroid_image": pygame.image.load("Projekt/Assets/asteroid_image.png").convert(),
                "bullet_image": pygame.image.load("Projekt/Assets/bullet_image.png").convert(),
                "shot_sound": pygame.mixer.Sound ("Projekt/Assets/laser.mp3"),
                "asteroid_hit_sound": pygame.mixer.Sound ("Projekt/Assets/asteroid_hit_sound.wav"),
                "rocket_image": pygame.image.load("Projekt/Assets/rocket_image.png").convert(),
                "particle_image": pygame.image.load("Projekt/Assets/particle_image.png").convert(),
                "pointer_image": pygame.image.load("Projekt/Assets/pointer_image.png").convert(),
                "explosion_image": pygame.image.load("Projekt/Assets/explosion_image.png").convert()}

gamestate = {   "player": None,
                "camera": None,
                "all_entities": pygame.sprite.Group(),
                "clock": pygame.time.Clock(),
                "asteroides": pygame.sprite.Group(),
                "bullets": pygame.sprite.Group(),
                "running": False, "ui": pygame.sprite.Group(),
                "menu": True, "menu_ui": pygame.sprite.Group(),
                "enemies": pygame.sprite.Group(),
                "particle_systems": pygame.sprite.Group(),
                "particles": pygame.sprite.Group(),
                "granades": pygame.sprite.Group(),
                "explosions": pygame.sprite.Group(),
                "level_text": None,
                "fps_text": None,
                "buttons": pygame.sprite.Group()}

ADDASTEROID = pygame.USEREVENT + 1
pygame.time.set_timer(ADDASTEROID, 100)

pygame.display.set_caption('Asteriodes by Rofdo')
pygame.display.set_icon(assets["window_icon"])

class ui_bar(pygame.sprite.Sprite):
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

class Text(pygame.sprite.Sprite):
    def __init__(self, text, position = pygame.Vector2(50, 80), size = 24, color = (255, 255, 255)) -> None:
        super().__init__()
        self.text = text
        self.position = position
        self.size = size
        self.color = color

    def render(self):
        font = pygame.font.SysFont(None, self.size)
        img = font.render(self.text, True, self.color)
        text_position_x = screen.get_size()[0] * self.position[0]/100 - img.get_size()[0]/2
        text_position_y = screen.get_size()[1] * self.position[1]/100 - img.get_size()[1]/2
        screen.blit(img, (text_position_x, text_position_y))

class Button(Text):
    def __init__(self, text, position=pygame.Vector2(50, 80), size=24, color=(255, 255, 255)) -> None:
        super().__init__(text, position, size, color)
        gamestate["buttons"].add(self)
        self.inflate = 0

    def get_rect(self)->pygame.Rect:
        true_size = self.size + self.inflate
        estimated_size_x = self.size*len(self.text)*0.5 + self.inflate
        return pygame.Rect(screen.get_size()[0] * self.position[0]/100 - estimated_size_x/2, screen.get_size()[1] * self.position[1]/100 - true_size/2, estimated_size_x, true_size)

    def render(self):
        pygame.draw.rect(screen, self.color, self.get_rect(), 2)
        return super().render()

    def effect(self):
        pass

    def update(self):
        self.inflate = 0
        if self.get_rect().collidepoint(pygame.mouse.get_pos()):
            self.inflate = 5
            if pygame.mouse.get_pressed()[0]:
                self.effect()

class ResumeButton(Button):
    def __init__(self, text, position=pygame.Vector2(50, 80), size=24, color=(255, 255, 255)) -> None:
        super().__init__(text, position, size, color)

    def effect(self):
        gamestate["menu"] = False

class RestartButton(Button):
    def __init__(self, text, position=pygame.Vector2(50, 80), size=24, color=(255, 255, 255)) -> None:
        super().__init__(text, position, size, color)

    def effect(self):
        gamestate["player"].die()
        gamestate["menu"] = False

class Camera():
    def __init__(self, position = pygame.Vector2(0, 0)) -> None:
        self.position = position
        self.rel_position = position

    def update(self):
        d = gamestate["player"].position.__sub__(self.rel_position)
        self.rel_position.x += d.x/10
        self.rel_position.y += d.y/10
        self.position = gamestate["player"].position + (gamestate["player"].position - self.rel_position)/1.5

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.position.x - screen.get_size()[0]/2, self.position.y - screen.get_size()[1]/2, screen.get_size()[0], screen.get_size()[1])

gamestate["camera"] = Camera()

class ParticleSystem(pygame.sprite.Sprite):
    def __init__(self, position = pygame.Vector2(0, 0), directionection = 0) -> None:
        super().__init__()
        gamestate["particle_systems"].add(self)
        self.position = position
        self.directionection = directionection
        self.particles = []
        self.on = True

    def update(self):
        if self.on:
            size = random.randint(15, 50)
            self.particles.append(Particle(position=self.position.xy, rotation=self.directionection + random.randint(-10, 10), speed=random.randint(5, 10), size=pygame.Vector2(size, size), lifetime=random.randint(30, 60)))

class Entity(pygame.sprite.Sprite):
    def __init__(self, image: pygame.surface, size = pygame.Vector2(50, 50), position = pygame.Vector2(0, 0), rotation = 0) -> None:
        super().__init__()
        gamestate["all_entities"].add(self)
        self.rotation = rotation
        self.position = position
        self.size = size
        self.surf = image
        self.surf.set_colorkey((0, 0, 0), pygame.RLEACCEL)
        self.opacity = 0

    def get_image(self) -> pygame.surface:
        image = pygame.transform.scale(self.surf, (self.size.x, self.size.y))
        image = pygame.transform.rotate(image, self.rotation)
        image.set_alpha(255*(100-self.opacity)*0.01)
        return image

    def update(self):
        pass

class Granade(Entity):
    def __init__(self, size=pygame.Vector2(50, 50), position=pygame.Vector2(0, 0), rotation=0, lifetime=120, velocity=pygame.Vector2) -> None:
        super().__init__(assets["particle_image"], size, position, rotation)
        gamestate["granades"].add(self)

        self.max_lifetime = lifetime
        self.lifetime = 0
        self.standart_size = size
        self.velocity = velocity

    def update(self):
        self.position += self.velocity.xy
        self.velocity = self.velocity*0.99
        self.lifetime += 1
        self.size = self.standart_size.xy * (math.sin((self.lifetime/3)*(self.lifetime/self.max_lifetime))/2 + 1.5)
        if self.lifetime >= self.max_lifetime:
            for entity in gamestate["asteroides"]:
                if entity.position.distance_to(self.position) < 300:
                    entity.kill()
            for entity in gamestate["enemies"]:
                if entity.position.distance_to(self.position) < 300:
                    entity.kill()
            if gamestate["player"].position.distance_to(self.position) < 300:
                gamestate["player"].hit(80)
            Explosion(position=self.position.xy)
            self.kill()

class Explosion(Entity):
    def __init__(self, size=pygame.Vector2(700, 700), position=pygame.Vector2(0, 0), rotation=0, time=10) -> None:
        super().__init__(assets["explosion_image"], size, position, rotation)
        gamestate["explosions"].add(self)

        self.max_size = size
        self.size = pygame.Vector2(0, 0)

        self.max_time = time
        self.time = 0

    def update(self):
        self.size = self.max_size.xy * self.time / self.max_time
        self.time += 1
        if self.time >= self.max_time:
            self.kill()

class Particle(Entity):
    def __init__(self, size=pygame.Vector2(50, 50), position=pygame.Vector2(0, 0), rotation=0, speed=10, lifetime=60) -> None:
        super().__init__(assets["particle_image"], size, position, rotation)
        gamestate["particles"].add(self)
        self.maxlifetime = lifetime
        self.lifetime = 0
        self.velocity = pygame.Vector2()
        direction = pygame.Vector2(0, speed)
        direction = direction.rotate(-self.rotation)
        self.velocity += direction.xy

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
        direction = pygame.Vector2(0, 200)
        direction = direction.rotate(-self.rotation + 180)
        self.position = pl_position.xy + direction.xy
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
        self.granade_cooldown = 0
        self.shield = 100
        self.health = 100
        self.shield_ui_bar = ui_bar(pygame.Vector2(50, 90), pygame.Vector2(300, 30), (30,144,255))
        self.health_ui_bar = ui_bar(pygame.Vector2(50, 95), pygame.Vector2(300, 30), (0,255,0))
        self.score = 0
        self.booster = ParticleSystem(self.position.xy, self.rotation)
        self.pointer = Pointer(size=pygame.Vector2(20, 50))

    def die(self):
        self.booster.kill()
        self.pointer.kill()
        reset()
        self.kill()

    def update(self, pressed_keys):
        self.booster.directionection = self.rotation
        direction = pygame.Vector2(0, 20)
        direction = direction.rotate(-self.rotation)
        self.booster.position = self.position.xy + direction.xy
        self.score += 1
        if self.score % 1000 == 0:
            pass
        if self.health <= 0:
            self.die()

        if self.shield < 100:
            self.shield += 0.1

        self.shield_ui_bar.value = self.shield
        self.health_ui_bar.value = self.health

        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= 1

        if self.granade_cooldown > 0:
            self.granade_cooldown -= 1

        self.slow = (math.pow(self.position.distance_to((0, 0))*0.00025, 5))
        speed = -0.5
        if self.slow > 1:
            speed = speed/self.slow

        self.booster.on = False
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            direction = pygame.Vector2(0, speed)
            direction = direction.rotate(-self.rotation)
            self.velocity += direction.xy
            self.booster.on = True
            #direction = pygame.Vector2(0, speed)
            #self.velocity += direction.xy
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            direction = pygame.Vector2(0, speed)
            direction = direction.rotate(-self.rotation)
            self.velocity -= direction.xy
            #direction = pygame.Vector2(0, -speed)
            #self.velocity += direction.xy
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            self.rotation += 10
            #direction = pygame.Vector2(speed, 0)
            #self.velocity += direction.xy
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            self.rotation -= 10
            #direction = pygame.Vector2(-speed, 0)
            #self.velocity += direction.xy
        if (pressed_keys[pygame.K_SPACE] or pygame.mouse.get_pressed(3)[0]) and self.weapon_cooldown == 0:
            goal = gamestate["camera"].position.xy
            goal.x += pygame.mouse.get_pos()[0] - screen.get_size()[0]/2
            goal.y += pygame.mouse.get_pos()[1] - screen.get_size()[1]/2
            Bullet(self.position.xy, math.atan2(goal.x - self.position.x, goal.y - self.position.y) * 57.296 + 180)
            self.weapon_cooldown = 10
        if pressed_keys[pygame.K_e] and self.granade_cooldown == 0:
            goal = gamestate["camera"].position.xy
            goal.x += pygame.mouse.get_pos()[0] - screen.get_size()[0]/2 - self.position.x
            goal.y += pygame.mouse.get_pos()[1] - screen.get_size()[1]/2 - self.position.y
            Granade(position=self.position.xy, velocity=(goal.xy/50) + self.velocity)
            self.granade_cooldown = 100

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
        direction = pygame.Vector2(0, -1)
        direction = direction.rotate(-self.rotation)
        self.position += direction.xy

        for bullet in gamestate["bullets"]:
            if self.position.distance_to(bullet.position) < self.size[0]*0.9:
                bullet.hit()
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
        direction = pygame.Vector2(gamestate["player"].position.xy.__sub__(self.position)).normalize()
        if self.position.distance_to(gamestate["player"].position) > 5000:
            self.kill()

        self.velocity += direction.xy
        self.position += self.velocity.xy
        self.velocity = self.velocity*0.98

        self.rotation = math.atan2(self.velocity.x, self.velocity.y)*180/3.141 + 180

        for enemy in gamestate["enemies"]:
            if self.position.distance_to(enemy.position) < self.size[0]*0.9 and not enemy == self:
                self.velocity += (enemy.position.xy - self.position.xy)*-1

        for bullet in gamestate["bullets"]:
            if self.position.distance_to(bullet.position) < self.size[0]*0.9:
                bullet.hit()
                self.kill()

        for enemy in gamestate["enemies"]:
            if self.position.distance_to(enemy.position) < self.size[0]*0.9 and not enemy == self:
                direction = enemy.position.xy - self.position.xy
                self.velocity -= direction.xy/2

        for asteroid in gamestate["asteroides"]:
            if self.position.distance_to(asteroid.position) < self.size[0]*0.9:
                asteroid.split()
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
        direction = pygame.Vector2(0, -50)
        direction = direction.rotate(-self.rotation)
        self.position += direction.xy

        if self.position.distance_to(gamestate["camera"].position) > 2000:
            self.kill()

        for granade in gamestate["granades"]:
            if self.position.distance_to(granade.position) < granade.size[0]*0.9:
                granade.lifetime = granade.max_lifetime
                self.kill()

    def hit(self):
        self.kill()

gamestate["player"] = Player()

def render():
    gamestate["fps_text"].text = "FPS: " + str(round(gamestate["clock"].get_fps()))
    gamestate["score_text"].text = "Score: " + str(gamestate["player"].score)
    gamestate["level_text"].text = "Level: " + str(math.ceil(gamestate["player"].score/1000))
    screen.fill((0, 0, 0))
    camera: Camera = gamestate["camera"]
    for entity in gamestate["all_entities"]:
        if entity.get_image().get_rect().move(entity.position.x, entity.position.y).colliderect(gamestate["camera"].get_rect()):
            screen.blit(entity.get_image(),
                        entity.get_image().get_rect().move(
                            (screen.get_size()[0]-entity.get_image().get_width())/2,
                            (screen.get_size()[1]-entity.get_image().get_height())/2)
                        .move(entity.position.x, entity.position.y)
                        .move(-camera.position.x, -camera.position.y))

    for menu_ui_element in gamestate["ui"]:
        menu_ui_element.render()

    surface = pygame.Surface(screen.get_size())
    surface.fill((255, 0, 0))
    if gamestate["player"].slow > 0.1:
        surface.set_alpha(20*gamestate["player"].slow)
        screen.blit(surface, (0, 0))
    else:
        pass

    surface = pygame.Surface(screen.get_size())
    surface.fill((100, 150, 0))
    if gamestate["player"].score % 1000 < 25 and gamestate["player"].score % 1000 > 0 and not gamestate["player"].score < 1000:
        surface.set_alpha(math.sin((gamestate["player"].score % 1000)/5)*100)
        screen.blit(surface, (0, 0))
    else:
        pass

    if gamestate["menu"]:
        for menu_ui_element in gamestate["menu_ui"]:
            menu_ui_element.render()

    pygame.display.flip()

def get_spawning_pos() -> pygame.Vector2():
    screen_size_x = screen.get_size()[0]
    screen_size_y = screen.get_size()[1]
    spawn_direction = random.randint(0, 3)
    if spawn_direction == 0:
        return pygame.Vector2(screen_size_x/1.5, random.randint(round(-screen_size_y/2), round(screen_size_y/2)))
    if spawn_direction == 1:
        return pygame.Vector2(-screen_size_x/1.5, random.randint(round(-screen_size_y/2), round(screen_size_y/2)))
    if spawn_direction == 2:
        return pygame.Vector2(random.randint(round(-screen_size_x/2), round(screen_size_x/2)), screen_size_y/1.5)
    return pygame.Vector2(random.randint(round(-screen_size_x/2), round(screen_size_x/2)), -screen_size_y/1.5)

def add_asteroid():
    asteroid_size = random.randint(50, 100)
    Asteroid(position=get_spawning_pos().__add__(gamestate["camera"].position), size=pygame.Vector2(asteroid_size, asteroid_size), rotation=random.randint(0, 360))

def game_update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gamestate["running"] = False
        elif event.type == ADDASTEROID:
            if bool(random.getrandbits(1)):
                if len(gamestate["asteroides"]) < 10:
                    add_asteroid()
            else:
                max = math.ceil(gamestate["player"].score/1000)
                max = min(max, 10)
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
    gamestate["granades"].update()
    gamestate["explosions"].update()

    render()

def menu_update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gamestate["running"] = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gamestate["menu"] = False

    gamestate["buttons"].update()
    render()

def reset():
    gamestate["player"] = Player()

pygame.mixer.set_num_channels(10)
gamestate["menu_ui"].add(ResumeButton("RESUME", (50, 40), 100))
gamestate["menu_ui"].add(RestartButton("START NEW GAME", (50, 20), 100))
gamestate["score_text"] = Text("Score: 0", (50, 5), 50)
gamestate["level_text"] = Text("Level: 1", (5, 5), 50)
gamestate["fps_text"] = Text("FPS: 0", (95, 5), 50)
gamestate["ui"].add(gamestate["score_text"])
gamestate["ui"].add(gamestate["level_text"])
gamestate["ui"].add(gamestate["fps_text"])
gamestate["running"] = True

while gamestate["running"]:
    if not gamestate["menu"]:
        game_update()
    else:
        menu_update()
    gamestate["clock"].tick(60)
pygame.quit()
