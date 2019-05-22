# A Normal Platformer is developed by Christopher G. Rodriguez
# Created April 24, 2019 (Updated on May 22, 2019)
#
# 5th Period Programming
# See READ_ME file for instructions and credits!


# pylint: disable=import-error


# Imports
import pygame
import json
import os
import sys

# Initialize game engine
pygame.mixer.pre_init()
pygame.init()

# Window
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TITLE = "A Normal Platformer"
FPS = 30

# Optional grid for help with level design
show_grid = False
grid_color = (150, 150, 150)

#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.FULLSCREEN)
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption(TITLE)

# Helper functions for loading assets
def load_font(font_face, font_size):
    return pygame.font.Font(font_face, font_size)

def load_image(path):
    return pygame.image.load(path).convert_alpha()

def flip_image(img):
    return pygame.transform.flip(img, 1, 0)

def load_sound(path):
    return pygame.mixer.Sound(path)

# Helper functions for playing music
def play_music():
    pygame.mixer.music.play(-1)

def stop_music():
    pygame.mixer.music.stop()

def pause_music():
    pygame.mixer.music.pause()

def unpause_music():
    pygame.mixer.music.unpause()

# Colors
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
TURQUOISE = (0, 255, 255)
BLUE = (0, 64, 255)
PURPLE = (128, 0, 255)
GREEN = (64, 255, 0)
ORANGE = (255, 128, 0)
GRAY = (91, 91, 91)
BABY_BLUE = (185, 209, 247)
SKY_BLUE = (0, 200, 225)
BRIGHT_GREEN = (0, 200, 0)
STORMY_BLUE =  (114, 144, 169)

# Fonts
font_xs = load_font(None, 16)
font_sm = load_font(None, 32)
font_md = load_font(None, 48)
font_lg = load_font(None, 64)
font_xl = load_font("assets/fonts/Cheri.ttf", 80)

# Sounds
jump_snd = load_sound('assets/sounds/jump.ogg')
gem_snd = load_sound('assets/sounds/gem.ogg')

# Images
idle = load_image('assets/images/characters/platformChar_idle.png')
walk = [load_image('assets/images/characters/platformChar_walk1.png'),
        load_image('assets/images/characters/platformChar_walk2.png')]
jump = load_image('assets/images/characters/platformChar_jump.png')
hurt = load_image('assets/images/characters/platformChar_hurt.png')
                   
hero_images = { "idle_rt": idle,
                "walk_rt": walk,
                "jump_rt": jump,
                "hurt_rt": hurt,
                "idle_lt": flip_image(idle),
                "walk_lt" : [flip_image(img) for img in walk],
                "jump_lt": flip_image(jump),
                "hurt_lt": flip_image(hurt) }
             
tile_images = { "Dirt": load_image('assets/images/tiles/platformPack_tile001.png'),
                "Platform": load_image('assets/images/tiles/platformPack_tile041.png'),
                "Red_Platform": load_image('assets/images/tiles/platformPack_tile020.png'),
                "Sand": load_image('assets/images/tiles/platformPack_tile002.png'),
                "Dirt": load_image('assets/images/tiles/platformPack_tile004.png'),
                "Lava_Surface": load_image('assets/images/tiles/platformPack_tile006.png'),
                "Lava": load_image('assets/images/tiles/platformPack_tile018.png'),
                "Door": load_image('assets/images/tiles/platformPack_tile048.png') }
        
basic_enemy_images = [ load_image('assets/images/characters/platformPack_tile024a.png'),
                       load_image('assets/images/characters/platformPack_tile024b.png') ]

platform_enemy_images = [ load_image('assets/images/characters/platformPack_tile011a.png'),
                          load_image('assets/images/characters/platformPack_tile011b.png') ]

spike_enemy_images = [ load_image('assets/images/characters/platformPack_tile043.png') ]

item_images = { "Gem": load_image('assets/images/items/platformPack_item008.png') }

# Levels
levels = ["assets/levels/level_1.json",
          "assets/levels/level_2.json",
          "assets/levels/level_3.json",
          "assets/levels/level_4.json" ]
    
# Sprite classes
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Hero(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()

        self.images = images
        self.image = images["idle_rt"]
        self.rect = self.image.get_rect()

        self.speed = 10
        self.jump_power = 26
        self.vx = 0
        self.vy = 0

        self.hearts = 1
        self.hurt_timer = 0
    
        self.reached_goal = False
        self.score = 0

        self.facing_right = True
        self.steps = 0
        self.step_rate = 4
        self.walk_index = 0
        
    def move_to(self, x, y):
        self.rect.x = x
        self.rect.y = y
        
    def step(self):
        self.steps = (self.steps + 1) % self.step_rate

        if self.steps == 0:
            self.walk_index = (self.walk_index + 1) % len(self.images['walk_rt'])
        
    def move_left(self):
        self.vx = -self.speed
        self.facing_right = False
        self.step()
    
    def move_right(self):
        self.vx = self.speed
        self.facing_right = True
        self.step()
        
    def stop(self):
        self.vx = 0

    def can_jump(self, tiles):
        self.rect.y += 2
        hit_list = pygame.sprite.spritecollide(self, tiles, False)
        self.rect.y -= 2

        return len(hit_list) > 0
        
    def jump(self, tiles):
        if self.can_jump(tiles):
            self.vy = -self.jump_power
            jump_snd.play()

    def apply_gravity(self, level):
        self.vy += level.gravity

        if self.vy > level.terminal_velocity:
            self.vy = level.terminal_velocity

    def move_and_check_tiles(self, level):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right
            self.vx = 0
                
        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom
            self.vy = 0

    def process_items(self, level):
        hit_list = pygame.sprite.spritecollide(self, level.items, True)

        for hit in hit_list:
            self.score += hit.value
            hit.apply(self)

    def process_enemies(self, level):
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        else:
            hit_list = pygame.sprite.spritecollide(self, level.enemies, False)

            for hit in hit_list:
                self.hearts -= 1
                self.hurt_timer = 30
    
    def check_world_edges(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width

    def check_goal(self, level):
        self.reached_goal = level.goal.contains(self.rect)

    def set_image(self):
        if self.facing_right:
            idle = self.images['idle_rt']
            walk = self.images['walk_rt']
            jump = self.images['jump_rt']
            hurt = self.images['hurt_rt']
        else:
            idle = self.images['idle_lt']
            walk = self.images['walk_lt']
            jump = self.images['jump_lt']
            hurt = self.images['hurt_lt']

        if self.hurt_timer > 0:
            self.image = hurt
        elif self.vy != 0:
            self.image = jump
        elif self.vx == 0:
            self.image = idle
        else:
            self.image = walk[self.walk_index]
            
    def update(self, level):
        self.apply_gravity(level)
        self.move_and_check_tiles(level)
        self.check_world_edges(level)
        self.process_items(level)
        self.process_enemies(level)
        self.check_goal(level)
        self.set_image()


class BasicEnemy(pygame.sprite.Sprite):
    '''
    BasicEnemies move back and forth, turning around whenever
    they hit a block or the edge of the world. Gravity affects
    BasicEnemies, so they will walk off platforms.
    '''
    
    def __init__(self, x, y, images):
        super().__init__()

        self.images = images
        self.image = images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vx = -4
        self.vy = 0

        self.steps = 0
        self.step_rate = 6
        self.walk_index = 0
        
    def reverse(self):
        self.vx = -1 * self.vx
        
    def apply_gravity(self, level):
        self.vy += level.gravity

        if self.vy > level.terminal_velocity:
            self.vy = level.terminal_velocity

    def move_and_check_tiles(self, level):
        ''' Move and check tiles in the horizontal direction '''
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right
            self.should_reverse = True

        ''' Move and check tiles in the vertical direction '''
        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom

            self.vy = 0
            
    def check_world_edges(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.should_reverse = True
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.should_reverse = True
        
    def step(self):
        self.steps = (self.steps + 1) % self.step_rate

        if self.steps == 0:
            self.walk_index = (self.walk_index + 1) % len(self.images)

    def set_image(self):
        self.image = self.images[self.walk_index]
        
    def update(self, level):
        self.should_reverse = False
        
        self.apply_gravity(level)
        self.move_and_check_tiles(level)
        self.check_world_edges(level)
        
        if self.should_reverse:
            self.reverse()
            
        self.step()
        self.set_image()

            
class PlatformEnemy(BasicEnemy):
    '''
    PlatformEnemies behave the same as BasicEnemies, except
    that they are aware of platform edges and will turn around
    when the edge is reached. Only init and the overridden
    function move_and_check_walls needs to be included.
    '''
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

    def move_and_check_tiles(self, level):
        reverse = False

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right
            self.should_reverse = True

        self.rect.y += 2
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)
        
        on_platform = False

        for hit in hit_list:
            if self.vy >= 0:
                self.rect.bottom = hit.rect.top
                self.vy = 0

                if self.vx > 0 and self.rect.right <= hit.rect.right:
                    on_platform = True
                elif self.vx < 0 and self.rect.left >= hit.rect.left:
                    on_platform = True

            elif self.vy < 0:
                self.rect.top = hit.rect.bottom
                self.vy = 0

        if not on_platform:
            self.should_reverse = True


class FastEnemy(pygame.sprite.Sprite):
    '''
    FastEnemies move back and forth, turning around whenever
    they hit a block or the edge of the world. Gravity affects
    FastEnemies, so they will walk off platforms.
    '''
    
    def __init__(self, x, y, images):
        super().__init__()

        self.images = images
        self.image = images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vx = -8
        self.vy = 0

        self.steps = 0
        self.step_rate = 3
        self.walk_index = 0
        
    def reverse(self):
        self.vx = -1 * self.vx
        
    def apply_gravity(self, level):
        self.vy += level.gravity

        if self.vy > level.terminal_velocity:
            self.vy = level.terminal_velocity

    def move_and_check_tiles(self, level):
        ''' Move and check tiles in the horizontal direction '''
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right
            self.should_reverse = True

        ''' Move and check tiles in the vertical direction '''
        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom

            self.vy = 0
            
    def check_world_edges(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.should_reverse = True
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.should_reverse = True
        
    def step(self):
        self.steps = (self.steps + 1) % self.step_rate

        if self.steps == 0:
            self.walk_index = (self.walk_index + 1) % len(self.images)

    def set_image(self):
        self.image = self.images[self.walk_index]
        
    def update(self, level):
        self.should_reverse = False
        
        self.apply_gravity(level)
        self.move_and_check_tiles(level)
        self.check_world_edges(level)
        
        if self.should_reverse:
            self.reverse()
            
        self.step()
        self.set_image()


class SpikeEnemy(pygame.sprite.Sprite):
    
    def __init__(self, x, y, images):
        super().__init__()

        self.images = images
        self.image = images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vy = 0

        self.steps = 0
        self.step_rate = 1
        self.walk_index = 0

    def move_and_check_tiles(self, level):
        ''' Move and check tiles in the vertical direction '''
        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, level.main_tiles, False)

        for hit in hit_list:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom

            self.vy = 0

    def apply_gravity(self, level):
        self.vy += level.gravity

        if self.vy > level.terminal_velocity:
            self.vy = level.terminal_velocity

    def step(self):
        self.steps = (self.steps + 1) % self.step_rate

        if self.steps == 0:
            self.walk_index = (self.walk_index + 1) % len(self.images)

    def set_image(self):
        self.image = self.images[self.walk_index]
        
    def update(self, level):
        self.move_and_check_tiles(level)
        self.apply_gravity(level)
        self.step()
        self.set_image()
        
            
class Gem(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.value = 50

    def apply(self, hero):
        gem_snd.play()
        hero.score += self.value
        
    def update(self, level):
        '''
        Items may not do anything. If so, this function can
        be deleted. However if an item is animated or it moves,
        then here is where you can implement that.
        '''
        pass

class Level():
    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            data = f.read()

        self.map_data = json.loads(data)

        self.load_layout()
        self.load_music()
        self.load_background()
        self.load_physics()
        self.load_tiles()
        self.load_items()
        self.load_enemies()
        self.load_goal()
        
        self.generate_layers()
        self.prerender_inactive_layers()

        if show_grid:
            self.make_grid_layer()

    def load_layout(self):
        self.scale =  self.map_data['layout']['scale']
        self.width =  self.map_data['layout']['size'][0] * self.scale
        self.height = self.map_data['layout']['size'][1] * self.scale
        self.start_x = self.map_data['layout']['start'][0] * self.scale
        self.start_y = self.map_data['layout']['start'][1] * self.scale

    def load_music(self):
        pygame.mixer.music.load(self.map_data['music'])
        
    def load_physics(self):
        self.gravity = self.map_data['physics']['gravity']
        self.terminal_velocity = self.map_data['physics']['terminal_velocity']

    def load_background(self):
        self.bg_color = self.map_data['background']['color']
        path1 = self.map_data['background']['image1']
        path2 = self.map_data['background']['image2']

        if os.path.isfile(path1):
            self.bg_image1 = pygame.image.load(path1).convert_alpha()
        else:
            self.bg_image1 = None

        if os.path.isfile(path2):
            self.bg_image2 = pygame.image.load(path2).convert_alpha()
        else:
            self.bg_image2 = None

        self.parallax_speed1 = self.map_data['background']['parallax_speed1']
        self.parallax_speed2 = self.map_data['background']['parallax_speed2']
        
    def load_tiles(self):
        self.midground_tiles = pygame.sprite.Group()
        self.main_tiles = pygame.sprite.Group()
        self.foreground_tiles = pygame.sprite.Group()

        for group_name in self.map_data['tiles']:
            tile_group = self.map_data['tiles'][group_name]
            
            for element in tile_group:
                x = element[0] * self.scale
                y = element[1] * self.scale
                kind = element[2]

                t = Tile(x, y, tile_images[kind])

                if group_name == 'midground':
                    self.midground_tiles.add(t)
                elif group_name == 'main':
                    self.main_tiles.add(t)
                elif group_name == 'foreground':
                    self.foreground_tiles.add(t)
            
    def load_items(self):
        self.items = pygame.sprite.Group()
        
        for element in self.map_data['items']:
            x = element[0] * self.scale
            y = element[1] * self.scale
            kind = element[2]
            
            if kind == "Gem":
                s = Gem(x, y, item_images[kind])
                
            self.items.add(s)

    def load_enemies(self):
        self.enemies = pygame.sprite.Group()
        
        for element in self.map_data['enemies']:
            x = element[0] * self.scale
            y = element[1] * self.scale
            kind = element[2]
            
            if kind == "BasicEnemy":
                s = BasicEnemy(x, y, basic_enemy_images)
            elif kind == "PlatformEnemy":
                s = PlatformEnemy(x, y, platform_enemy_images)
            elif kind == "FastEnemy":
                s = FastEnemy(x, y, basic_enemy_images)
            elif kind == "SpikeEnemy":
                s = SpikeEnemy(x, y, spike_enemy_images)
                
            self.enemies.add(s)

    def load_goal(self):
        g = self.map_data['layout']['goal']

        if isinstance(g, int):
            x = g * self.scale
            y = 0
            w = self.width - x
            h = self.height
        elif isinstance(g, list):
            x = g[0] * self.scale
            y = g[1] * self.scale
            w = g[2] * self.scale
            h = g[3] * self.scale

        self.goal = pygame.Rect([x, y, w, h])

    def generate_layers(self):
        self.world = pygame.Surface([self.width, self.height])
        self.background1 = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.background2 = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.inactive = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.active = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.foreground = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)

    def tile_image(self, img, surf):
        surf_w = surf.get_width()
        surf_h = surf.get_height()
        img_w = img.get_width()
        img_h = img.get_height()
        
        for x in range(0, surf_w, img_w):
            #for y in range(0, surf_h, img_h):
            y = surf_h - img_h
            surf.blit(img, [x, y])
                
    def prerender_inactive_layers(self):
        self.background1.fill(self.bg_color)
        
        if self.bg_image1 != None:
            self.tile_image(self.bg_image1, self.background1)
            
        if self.bg_image2 != None:
            self.tile_image(self.bg_image2, self.background2)
                    
        self.midground_tiles.draw(self.inactive)
        self.main_tiles.draw(self.inactive)        
        self.foreground_tiles.draw(self.foreground)

    def make_grid_layer(self):
        self.grid = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        
        for x in range(0, self.width, self.scale):
            pygame.draw.line(self.grid, grid_color, [x,0], [x, self.height], 1)
        for y in range(0, self.width, self.scale):
            pygame.draw.line(self.grid, grid_color, [0, y], [self.width, y], 1)
            
        for x in range(0, self.width, self.scale):
            for y in range(0, self.width, self.scale):
                coordinate = str(x // self.scale) + ", " + str(y // self.scale)
                text = font_xs.render(coordinate, 1, grid_color)
                self.grid.blit(text, [x + 4, y + 4])     

# Main game class
class Game():

    START = 0
    PLAYING = 1
    CLEARED = 2
    WIN = 3
    LOSE = 4
    PAUSE = 5

    def __init__(self, levels):
        self.clock = pygame.time.Clock()
        self.running = True
        self.levels = levels
        self.level_change_delay = 90
    
    def setup(self):
        self.hero = Hero(hero_images)
        self.player = pygame.sprite.GroupSingle()
        self.player.add(self.hero)

        self.stage = Game.START
        self.current_level = 1
        self.load_level()

    def load_level(self):
        level_index = self.current_level - 1
        level_data = self.levels[level_index] 
        self.level = Level(level_data) 

        self.hero.move_to(self.level.start_x, self.level.start_y)
        self.hero.reached_goal = False

        self.active_sprites = pygame.sprite.Group()
        self.active_sprites.add(self.hero, self.level.items, self.level.enemies)

    def start_level(self):
        play_music()
        self.stage = Game.PLAYING
            
    def advance(self):
        if self.current_level < len(self.levels):
            self.current_level += 1
            self.load_level()
            self.start_level()
        else:
            self.stage = Game.WIN

    def show_title_screen(self):
        text = font_xl.render(TITLE, 1, WHITE)
        rect = text.get_rect()
        rect.centerx = SCREEN_WIDTH // 2
        rect.centery = 320
        screen.blit(text, rect)
        
        text = font_md.render("Press SPACE to start!", 1, WHITE)
        rect = text.get_rect()
        rect.centerx = SCREEN_WIDTH // 2
        rect.centery = 380
        screen.blit(text, rect)
        
    def show_cleared_screen(self):
        text = font_lg.render("Level cleared!", 1, TURQUOISE)
        rect = text.get_rect()
        rect.centerx = SCREEN_WIDTH // 2
        rect.centery = 360
        screen.blit(text, rect)

    def show_win_screen(self):
        text = font_lg.render("You win!", 1, TURQUOISE)
        text2 = font_md.render("Press SPACE to play again or ESC to exit!", 1, WHITE)
        rect = text.get_rect()
        rect2 = text2.get_rect()
        rect.centerx = SCREEN_WIDTH // 2
        rect.centery = 330
        rect2.centerx = SCREEN_WIDTH // 2
        rect2.centery = 380
        screen.blit(text, rect)
        screen.blit(text2, rect2)

    def show_lose_screen(self):
        text = font_lg.render("YOU HAVE DIED.", 1, RED)
        text2 = font_md.render("Press SPACE to play again or ESC to exit.", 1, WHITE)
        rect = text.get_rect()
        rect2 = text2.get_rect()
        rect.centerx = SCREEN_WIDTH // 2
        rect.centery = 330
        rect2.centerx = SCREEN_WIDTH // 2
        rect2.centery = 380
        screen.blit(text, rect)
        screen.blit(text2, rect2)

    def show_pause(self):
        t1 = font_lg.render("PAUSED", True, WHITE)
        t2 = font_md.render("(Press SPACE to resume.)", True, YELLOW)
        w1 = t1.get_width()
        w2 = t2.get_width()
        screen.blit(t1, [SCREEN_WIDTH/2 - w1/2, 330])
        screen.blit(t2, [SCREEN_WIDTH/2 - w2/2, 380])

    def show_stats(self):
        level_str = "Level: " + str(self.current_level)
        
        text = font_md.render(level_str, 1, YELLOW)
        rect = text.get_rect()
        rect.left = 24
        rect.top = 24
        screen.blit(text, rect)
    
        score_str = "Score: " + str(self.hero.score)
        
        text = font_md.render(score_str, 1, YELLOW)
        rect = text.get_rect()
        rect.right = SCREEN_WIDTH - 24
        rect.top = 24
        screen.blit(text, rect)        
                   
    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + SCREEN_WIDTH / 2
        y = -1 * self.hero.rect.centery + SCREEN_HEIGHT / 2

        ''' Horizontal offset '''
        if self.hero.rect.centerx < SCREEN_WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - SCREEN_WIDTH / 2:
            x = -1 * self.level.width + SCREEN_WIDTH

        ''' Vertical offset '''
        if self.hero.rect.centery < SCREEN_HEIGHT / 2:
            y = 0
        elif self.hero.rect.centery > self.level.height - SCREEN_HEIGHT / 2:
            y = -1 * self.level.height + SCREEN_HEIGHT

        return round(x), round(y)

    def process_input(self):     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                if self.stage == Game.START:
                    if event.key == pygame.K_SPACE:
                        self.start_level()
                        
                elif self.stage == Game.PLAYING:
                    if event.key == pygame.K_UP:
                        self.hero.jump(self.level.main_tiles)
                    elif event.key == pygame.K_r:
                        self.setup()
                    elif event.key == pygame.K_p:
                        self.stage = Game.PAUSE
                        pause_music()

                elif self.stage == Game.PAUSE:
                    if event.key == pygame.K_SPACE:
                        self.stage = Game.PLAYING
                        unpause_music()

                elif self.stage == Game.WIN or self.stage == Game.LOSE:
                    if event.key == pygame.K_SPACE:
                        self.setup()

        pressed = pygame.key.get_pressed()
        
        if self.stage == Game.PLAYING:
            if pressed[pygame.K_LEFT]:
                self.hero.move_left()
            elif pressed[pygame.K_RIGHT]:
                self.hero.move_right()
            else:
                self.hero.stop()
     
    def update(self):
        if self.stage == Game.PLAYING:
            self.active_sprites.update(self.level)

            if self.hero.reached_goal:
                stop_music()
                self.stage = Game.CLEARED
                self.cleared_timer = self.level_change_delay
            elif self.hero.hearts == 0:
                self.stage = Game.LOSE
                stop_music()
                
        elif self.stage == Game.CLEARED:
            self.cleared_timer -= 1

            if self.cleared_timer == 0:
                self.advance()
            
    def render(self):
        self.level.active.fill([0, 0, 0, 0])
        self.active_sprites.draw(self.level.active)

        offset_x, offset_y = self.calculate_offset()
        bg1_offset_x = -1 * offset_x * self.level.parallax_speed1
        bg1_offset_y = -1 * offset_y * self.level.parallax_speed1
        bg2_offset_x = -1 * offset_x * self.level.parallax_speed2
        bg2_offset_y = -1 * offset_y * self.level.parallax_speed2
        
        self.level.world.blit(self.level.background1, [bg1_offset_x, bg1_offset_y])
        self.level.world.blit(self.level.background2, [bg2_offset_x, bg2_offset_y])
        self.level.world.blit(self.level.inactive, [0, 0])
        self.level.world.blit(self.level.active, [0, 0])
        self.level.world.blit(self.level.foreground, [0, 0])

        if show_grid:
            self.level.world.blit(self.level.grid, [0, 0])                     

        screen.blit(self.level.world, [offset_x, offset_y])

        self.show_stats()
        
        if self.stage == Game.START:
            self.show_title_screen()        
        elif self.stage == Game.CLEARED:
            self.show_cleared_screen()
        elif self.stage == Game.WIN:
            self.show_win_screen()
        elif self.stage == Game.LOSE:
            self.show_lose_screen()
        elif self.stage == Game.PAUSE:
            self.show_pause()

        pygame.display.flip()
            
    def run(self):        
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

            
# Let's do this!
if __name__ == "__main__":
    g = Game(levels)
    g.setup()
    g.run()
    
    pygame.quit()
    sys.exit()
