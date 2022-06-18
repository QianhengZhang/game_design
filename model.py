from turtle import update
import pygame
import time

HERO_ASSET = 'assets/imgs/Sprites/HeroKnight/'
Warlock_ASSET = 'assets/imgs/Sprites/Warlock/'
Skeleton_ASSET = 'assets/imgs/Sprites/Skeleton/'

class Hero(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.maxHp = 100
        self.hp = 100
        self.attack = 20
        self.coolDown = 0.7
        self.damageCoolDown = 2.5
        self.status = 'idle'
        self.direction = 1
        self.velocity = 12
        self.index = 0
        self.last = time.time()
        self.lasthurt = time.time()
        self.images = {
            'idle': [pygame.image.load(HERO_ASSET + f'idle/HeroKnight_Idle_{i+1}.png') for i in range(0, 7)],
            'run': [pygame.image.load(HERO_ASSET + f'run/HeroKnight_Run_{i+1}.png') for i in range(0, 9)],
            'jump': [pygame.image.load(HERO_ASSET + f'Jump/HeroKnight_Jump_{i+1}.png') for i in range(0, 5)],
            'fall': [pygame.image.load(HERO_ASSET + f'fall/HeroKnight_fall_{i+1}.png') for i in range(0, 3)],
            'attack' : [pygame.image.load(HERO_ASSET + f'Attack1/HeroKnight_Attack1_{i+1}.png') for i in range(0, 5)],
            'attack2' : [pygame.image.load(HERO_ASSET + f'Attack2/HeroKnight_Attack2_{i+1}.png') for i in range(0, 5)],
            'attack3' : [pygame.image.load(HERO_ASSET + f'Attack3/HeroKnight_Attack3_{i+1}.png') for i in range(0, 7)],
            'hurt': [pygame.image.load(HERO_ASSET + f'Hurt/HeroKnight_Hurt_{i+1}.png') for i in range(0, 11)],
            'block' : [pygame.image.load(HERO_ASSET + f'BlockIdle/HeroKnight_Block Idle_{i+1}.png') for i in range(0, 7)],
            'block_success' : [pygame.image.load(HERO_ASSET + f'Block/HeroKnight_Block_{i+1}.png') for i in range(0, 4)],
            'death' : [pygame.image.load(HERO_ASSET + f'Death/HeroKnight_Death_{i+1}.png') for i in range(0, 9)]

        }

        image_surf = pygame.image.load(HERO_ASSET + 'idle/HeroKnight_Idle_0.png').convert()
        self.image = pygame.Surface((100,55))
        self.image.blit(image_surf, (0,0))
        self.image.set_colorkey((0,0,0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, controls):

        if self.hp <= 0:
            self.status = 'death'
            if self.index == len(self.images[self.status]) - 1:
                self.kill()
                pygame.mixer.music.load('assets/sounds/mixkit-player-losing-or-failing-2042.wav')
                pygame.mixer.music.play()
        new = time.time()
        if self.status == 'block_sucess' and self.index == len(self.images[self.status]) - 1:
            self.status = 'block'
        if self.index == len(self.images[self.status]) - 1 or self.status in ['idle', 'run', 'block'] and self.status != 'death':
            if controls['attack'] and (new-self.last > self.coolDown):
                pygame.mixer.music.load('assets/sounds/mixkit-sword-blade-attack-in-medieval-battle-2762.wav')
                pygame.mixer.music.play()
                if controls['block']:
                    self.status = 'attack2'
                elif self.status == 'run':
                    self.status = 'attack3'
                else:
                    self.status = 'attack'
                self.index = 0
                self.last = time.time()
            elif controls['up'] or controls['down'] or controls['left'] or controls['right']:
                self.status = 'run'
                self.movement_wrapper(controls['up'], controls['down'], controls['left'], controls['right'])
            elif controls['block']:
                if self.status != 'block_success' or (self.status == 'block_success' and self.index == len(self.images[self.status]) - 1 ):
                    self.status = 'block'
            else:
                self.status = 'idle'
        self.index = (self.index + 1) % len(self.images[self.status])
        self.image = self.images[self.status][self.index]
        self.mask = pygame.mask.from_surface(self.image)
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def movement_wrapper(self, up, down, left, right):
        x = 0
        y = 0
        if up and self.rect.y > 374:
            y = -1
        elif down and self.rect.y < 670:
            y = 1
        if left and self.rect.x > 0:
            x = -1
            self.direction = -1
        elif right and self.rect.x < 1000:
            x = 1
            self.direction = 1
        self.rect.x += x * self.velocity
        self.rect.y += y * self.velocity

    def update_collisiton(self, battle):
        status = ['attack', 'attack1', 'attack2']
        new = time.time()
        if len(battle) > 0:
            if self.status in status:
                for monster in battle:
                    if (new- monster.last_hurt > monster.hurt_cd):
                        monster.last_hurt = time.time()
                        monster.hp -= self.attack
                        if monster.direction == 1:
                            monster.state = 'hurt_left'
                        else:
                            monster.state = 'hurt_right'
                        monster.index = 0
            else:
                for monster in battle:
                    if monster.state in ['attack_left', 'attack_right']:
                        if self.status in ['block', 'block_success', 'attack2'] and self.direction == monster.direction:
                            self.rect.x -= monster.direction * 10
                            monster.rect.x += monster.direction * 20
                            self.hp -= monster.attack * 0.1
                            self.status = 'block_success'
                            self.index = 0
                        else:
                            new = time.time()
                            if new - self.lasthurt > self.damageCoolDown:
                                self.hp -= monster.attack
                                if self.hp > 0:
                                    pygame.mixer.music.load('assets/sounds/mixkit-human-fighter-pain-scream-2768.wav')
                                    pygame.mixer.music.play()
                                self.lasthurt = time.time()
                                self.index = 0
                                self.update_hurt(monster)

    def update_hurt(self, monster):
        print('hurt')
        self.status = 'hurt'
        self.rect.x -= monster.direction * 15
        self.image = self.images[self.status][self.index]
        self.index = (self.index + 1) % len(self.images[self.status])
        print(self.index)
        if self.index == len(self.images[self.status]) - 1:
            self.status = ['idle']
            print('end')
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)


    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Tester(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)

        self.maxHp = 200
        self.hp = 80
        self.attack = 20

        image_surf = pygame.image.load('tester.png').convert()
        self.image = pygame.Surface((44,55))
        image_surf = pygame.transform.flip(image_surf, True, False)
        self.image.blit(image_surf, (0,0))
        self.image.set_colorkey((0,0,0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        if (self.hp <= 0):
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Skeleton_blue(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.hp = 50
        self.state = 'born'
        self.index = 0
        self.image = pygame.Surface((64,64))
        self.image_surf = pygame.image.load(Skeleton_ASSET + f'SkeletonMage_Blue.png').convert()
        self.image.blit(self.image_surf,(0,0),(180,0,64,64))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect(topleft=pos)
        self.lock = 1
        self.direction = 1
        self.image_rects = {
            'idle_left' : [pygame.Rect(0,64,64,64), pygame.Rect(64,64,64,64), pygame.Rect(128,64,64,64),
                           pygame.Rect(192,64,64,64)],
            'idle_right': [pygame.Rect(0, 192, 64, 64), pygame.Rect(64, 192, 64, 64), pygame.Rect(128, 192, 64, 64),
                          pygame.Rect(192, 192, 64, 64)],
            'run_left' : [pygame.Rect(0,320,64,64),pygame.Rect(64,320,64,64),pygame.Rect(128,320,64,64),
                        pygame.Rect(192,320,64,64),pygame.Rect(256,320,64,64),pygame.Rect(320,320,64,64)],
            'run_right': [pygame.Rect(0, 448, 64, 64), pygame.Rect(64, 448, 64, 64), pygame.Rect(128, 448, 64, 64),
                         pygame.Rect(192, 448, 64, 64), pygame.Rect(256, 448, 64, 64), pygame.Rect(320, 448, 64, 64)],
            'attack_left' : [pygame.Rect(0,576,64,64),pygame.Rect(64,576,64,64),pygame.Rect(128,576,64,64),
                        pygame.Rect(192,576,64,64),pygame.Rect(256,576,64,64),pygame.Rect(320,576,64,64),
                        pygame.Rect(384,576,64,64),pygame.Rect(448,576,64,64)],
            'attack_right': [pygame.Rect(0, 704, 64, 64), pygame.Rect(64, 704, 64, 64), pygame.Rect(128, 704, 64, 64),
                             pygame.Rect(192, 704, 64, 64), pygame.Rect(256, 704, 64, 64),
                             pygame.Rect(320, 704, 64, 64),
                             pygame.Rect(384, 704, 64, 64), pygame.Rect(448, 704, 64, 64)],
            'born' : [pygame.Rect(0,1088,64,64),pygame.Rect(64,1088,64,64),pygame.Rect(128,1088,64,64),
                        pygame.Rect(192,1088,64,64),pygame.Rect(256,1088,64,64),pygame.Rect(320,1088,64,64),
                        pygame.Rect(384,1088,64,64),pygame.Rect(448,1088,64,64),pygame.Rect(512,1088,64,64)],
            'hurt_left' : [pygame.Rect(0,1280,64,64),pygame.Rect(64,1280,64,64),pygame.Rect(128,1280,64,64),
                        pygame.Rect(192,1280,64,64),pygame.Rect(256,1280,64,64),pygame.Rect(320,1280,64,64)],
            'hurt_right': [pygame.Rect(0, 1344, 64, 64), pygame.Rect(64, 1344, 64, 64), pygame.Rect(128, 1344, 64, 64),
                           pygame.Rect(192, 1344, 64, 64), pygame.Rect(256, 1344, 64, 64),
                           pygame.Rect(320, 1344, 64, 64)],
            'death_left' : [pygame.Rect(0,1472,64,64),pygame.Rect(64,1472,64,64),pygame.Rect(128,1472,64,64),
                        pygame.Rect(192,1472,64,64),pygame.Rect(256,1472,64,64),pygame.Rect(320,1472,64,64),
                        pygame.Rect(384,1472,64,64)],
            'death_right': [pygame.Rect(0, 1600, 64, 64), pygame.Rect(64, 1600, 64, 64), pygame.Rect(128, 1600, 64, 64),
                      pygame.Rect(192, 1600, 64, 64), pygame.Rect(256, 1600, 64, 64), pygame.Rect(320, 1600, 64, 64),
                      pygame.Rect(384, 1600, 64, 64)]
        }

    def update(self,hero_center_pos):
        if self.state == 'born' and self.index == 8:
            self.state = 'idle_left'
            self.lock = 0
            self.index = 0
        if self.hp < 0:
            if self.direction == 1:
                self.state = 'death_left'
            else:
                self.state = 'death_right'
            self.lock = 1
        if (self.state == 'death_left' or self.state == 'death_right') and self.index == 6:
            self.kill()
        if self.lock == 0:
            x = self.rect.centerx
            y = self.rect.centery
            distance = ((hero_center_pos[0]-x)**2 + (hero_center_pos[1]-y)**2)**0.5
            if distance < 150 and distance > 20:
                if self.direction == 1:
                    self.state = 'run_left'
                if self.direction == -1:
                    self.state = 'run_right'
                if hero_center_pos[0] < x:
                    self.direction = 1
                    self.rect.move_ip(-1,0)
                if hero_center_pos[0] > x:
                    self.direction = -1
                    self.rect.move_ip(1,0)
                if hero_center_pos[1] < y:
                    self.rect.move_ip(0,-1)
                if hero_center_pos[1] > y:
                    self.rect.move_ip(0,1)
            if distance <= 20:
                if self.direction == 1:
                    self.state = 'attack_left'
                if self.direction == -1:
                    self.state = 'attack_right'
            if distance >= 150:
                if self.direction == 1:
                    self.state = 'idle_left'
                if self.direction == -1:
                    self.state = 'idle_right'
        self.index = (self.index + 1)%len(self.image_rects[self.state])
        self.image.blit(self.image_surf,(0,0),self.image_rects[self.state][self.index])
    def draw(self, surface):

        surface.blit(self.image, self.rect)


class Skeleton_red(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.hp = 50
        self.attack = 15
        self.state = 'born'
        self.index = 0
        self.hurt_cd = 0.3
        self.last_hurt = time.time()
        self.cd = 1.2
        self.last = time.time()
        self.image = pygame.Surface((64,64))
        self.image_surf = pygame.image.load(Skeleton_ASSET + f'SkeletonMage_Red.png').convert()
        self.image.blit(self.image_surf,(0,0),(180,0,64,64))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect(topleft=pos)
        self.lock = 1
        self.direction = 1
        self.image_rects = {
            'idle_left' : [pygame.Rect(0,64,64,64), pygame.Rect(64,64,64,64), pygame.Rect(128,64,64,64),
                           pygame.Rect(192,64,64,64)],
            'idle_right': [pygame.Rect(0, 192, 64, 64), pygame.Rect(64, 192, 64, 64), pygame.Rect(128, 192, 64, 64),
                          pygame.Rect(192, 192, 64, 64)],
            'run_left' : [pygame.Rect(0,320,64,64),pygame.Rect(64,320,64,64),pygame.Rect(128,320,64,64),
                        pygame.Rect(192,320,64,64),pygame.Rect(256,320,64,64),pygame.Rect(320,320,64,64)],
            'run_right': [pygame.Rect(0, 448, 64, 64), pygame.Rect(64, 448, 64, 64), pygame.Rect(128, 448, 64, 64),
                         pygame.Rect(192, 448, 64, 64), pygame.Rect(256, 448, 64, 64), pygame.Rect(320, 448, 64, 64)],
            'attack_left': [pygame.Rect(0, 832, 64, 64), pygame.Rect(64, 832, 64, 64), pygame.Rect(128, 832, 64, 64),
                       pygame.Rect(192, 832, 64, 64), pygame.Rect(256, 832, 64, 64), pygame.Rect(320, 832, 64, 64),
                       pygame.Rect(384, 832, 64, 64), pygame.Rect(448, 832, 64, 64)],
            'attack_right': [pygame.Rect(0, 960, 64, 64), pygame.Rect(64, 960, 64, 64), pygame.Rect(128, 960, 64, 64),
                       pygame.Rect(192, 960, 64, 64), pygame.Rect(256, 960, 64, 64), pygame.Rect(320, 960, 64, 64),
                       pygame.Rect(384, 960, 64, 64), pygame.Rect(448, 960, 64, 64)],
            'born' : [pygame.Rect(0,1088,64,64),pygame.Rect(64,1088,64,64),pygame.Rect(128,1088,64,64),
                        pygame.Rect(192,1088,64,64),pygame.Rect(256,1088,64,64),pygame.Rect(320,1088,64,64),
                        pygame.Rect(384,1088,64,64),pygame.Rect(448,1088,64,64),pygame.Rect(512,1088,64,64)],
            'hurt_left' : [pygame.Rect(0,1280,64,64),pygame.Rect(64,1280,64,64),pygame.Rect(128,1280,64,64),
                        pygame.Rect(192,1280,64,64),pygame.Rect(256,1280,64,64),pygame.Rect(320,1280,64,64)],
            'hurt_right': [pygame.Rect(0, 1344, 64, 64), pygame.Rect(64, 1344, 64, 64), pygame.Rect(128, 1344, 64, 64),
                           pygame.Rect(192, 1344, 64, 64), pygame.Rect(256, 1344, 64, 64),
                           pygame.Rect(320, 1344, 64, 64)],
            'death_left' : [pygame.Rect(0,1472,64,64),pygame.Rect(64,1472,64,64),pygame.Rect(128,1472,64,64),
                        pygame.Rect(192,1472,64,64),pygame.Rect(256,1472,64,64),pygame.Rect(320,1472,64,64),
                        pygame.Rect(384,1472,64,64)],
            'death_right': [pygame.Rect(0, 1600, 64, 64), pygame.Rect(64, 1600, 64, 64), pygame.Rect(128, 1600, 64, 64),
                      pygame.Rect(192, 1600, 64, 64), pygame.Rect(256, 1600, 64, 64), pygame.Rect(320, 1600, 64, 64),
                      pygame.Rect(384, 1600, 64, 64)]
        }

    def update(self,hero_center_pos, game):
        if self.state in ['hurt_left', 'hurt_right'] and self.index != len(self.image_rects[self.state]) - 1:
            if self.direction == 1:
                self.state = 'hurt_left'
            else:
                self.state = 'hurt_right'
        else:
            if self.state == 'born' and self.index == 8:
                pygame.mixer.music.load('assets/sounds/WK36XX5-summon-skeleton-companion.wav')
                pygame.mixer.music.play()
                self.state = 'idle_left'
                self.lock = 0
                self.index = 0
            if self.hp < 0:
                if self.direction == 1:
                    self.state = 'death_left'
                else:
                    self.state = 'death_right'
                self.lock = 1
            if (self.state == 'death_left' or self.state == 'death_right') and self.index == 6:
                self.kill()
                game.score += 1
            if self.lock == 0:
                x = self.rect.centerx
                y = self.rect.centery
                distance = ((hero_center_pos[0]-x)**2 + (hero_center_pos[1]-y)**2)**0.5
                if distance < 350 and distance > 20:
                    if self.direction == 1:
                        self.state = 'run_left'
                    if self.direction == -1:
                        self.state = 'run_right'
                    if hero_center_pos[0] < x:
                        self.direction = 1
                        self.rect.move_ip(-1,0)
                    if hero_center_pos[0] > x:
                        self.direction = -1
                        self.rect.move_ip(1,0)
                    if hero_center_pos[1] < y:
                        self.rect.move_ip(0,-1)
                    if hero_center_pos[1] > y:
                        self.rect.move_ip(0,1)
                if distance <= 30 and time.time() - self.last > self.cd:
                    self.last = time.time()
                    if self.direction == 1:
                        self.state = 'attack_left'
                    if self.direction == -1:
                        self.state = 'attack_right'
                if distance >= 350:
                    if self.direction == 1:
                        self.state = 'idle_left'
                    if self.direction == -1:
                        self.state = 'idle_right'
        self.index = (self.index + 1)%len(self.image_rects[self.state])
        self.image.blit(self.image_surf,(0,0),self.image_rects[self.state][self.index])
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Warlock(pygame.sprite.Sprite):

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.maxHp = 40
        self.hp = 40
        self.attack = 10
        self.coolDown = 5
        self.damageCoolDown = 1.5
        self.status = 'idle'
        self.direction = 1
        self.velocity = 3
        self.index = 0
        self.last = time.time()
        self.lasthurt = time.time()
        self.images = {
            'idle': [pygame.image.load(Warlock_ASSET + f'Idle/Warlock_Idle_{i}.png') for i in range(0, 12)],
            'run': [pygame.image.load(Warlock_ASSET + f'Run/Warlock_Run_{i}.png') for i in range(0, 8)],
            'death': [pygame.image.load(Warlock_ASSET + f'Death/Warlock_Death_{i}.png') for i in range(0, 13)],
            'attack' : [pygame.image.load(Warlock_ASSET + f'Attack/Warlock_Attack_{i}.png') for i in range(0, 13)],
            'hurt': [pygame.image.load(Warlock_ASSET + f'Hurt/Warlock_Hurt_{i}.png') for i in range(0, 5)],
        }

        image_surf = pygame.image.load(Warlock_ASSET + 'idle/Warlock_Idle_0.png').convert()
        self.image = pygame.Surface((100,80))
        self.image.blit(image_surf, (0,0))
        self.image.set_colorkey((0,0,0))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self,controls):
        new = time.time()
        if self.hp <= 0:
            self.status = "death"
            if self.index == 12:
                self.kill()
        if controls['attack'] and (new-self.last > self.coolDown):
            self.status = "attack"
            self.index = 0
            self.last = time.time()
        elif controls['up']:
            self.status = 'run'
            self.rect.y -= self.velocity
        elif controls['down']:
            self.status = 'run'
            self.rect.y += self.velocity
        elif controls['left']:
            self.direction = -1
            self.status = 'run'
            self.rect.x -= self.velocity
        elif controls['right']:
            self.direction = 1
            self.status = 'run'
            self.rect.x += self.velocity
        elif controls['hurt']:
            self.status = 'hurt'
            self.index = 0
        else:
            self.status = 'idle'
        self.index = (self.index + 1) % len(self.images[self.status])
        self.image = self.images[self.status][self.index]
        self.mask = pygame.mask.from_surface(self.image)
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def setup_fonts(font_size, bold=False, italic=False):
    ''' Load a font, given a list of preferences

        The preference list is a sorted list of strings (should probably be a parameter),
        provided in a form from the FontBook list.
        Any available font that starts with the same letters (lowercased, spaces removed)
        as a font in the font_preferences list will be loaded.
        If no font can be found from the preferences list, the pygame default will be returned.

        returns -- A Font object
    '''
    font_preferences = ['Helvetica Neue', 'Iosevka Regular', 'Comic Sans', 'Courier New']
    available = pygame.font.get_fonts()
    prefs = [x.lower().replace(' ', '') for x in font_preferences]
    for pref in prefs:
        a = [x
             for x in available
             if x.startswith(pref)
            ]
        if a:
            fonts = ','.join(a) #SysFont expects a string with font names in it
            return pygame.font.SysFont(fonts, font_size, bold, italic)
    return pygame.font.SysFont(None, font_size, bold, italic)

class TextBox():

    def __init__(self, surface):
        self.status = 'close'
        self.surface = surface
        self.fontobj = setup_fonts(36)
        self.rect = pygame.Rect((0,0),(1080, 720))
        self.rect.center = (540, 360)
        self.image_surf = pygame.image.load('pop_up.jpg').convert()
        self.image_surf = pygame. transform. scale(self.image_surf, (1080, 720))



    def pop_up(self, texts):
        row = len(texts)
        self.surface.blit(self.image_surf, self.rect)
        for i in range(0, row):
            text = texts[i]
            text_surface = self.fontobj.render(text, True, (255, 255, 255))
            text_center = (540, 120 + (360 / (row + 1)) * (i+1))
            text_rect = text_surface.get_rect(center = text_center)
            self.surface.blit(text_surface, text_rect)
        self.status = 'pop_up'


    def update(self, control):
        if control['pop'] == True and self.status != 'pop_up':
            self.status = 'pop_up'
            return 'pause'
        elif control['pop'] == True and self.status == 'pop_up':
            self.status = 'close'
            return 'running'

class GameManager():

    def __init__(self):
        self.score = 0
        self.fontobj = setup_fonts(24)

    def draw(self, surface):
         text = self.fontobj.render("Score: "+str(self.score), True, (255, 255, 255))
         surface.blit(text,(16,80))
