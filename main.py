import pygame
import time  # for time delay and timestamps
import random # random values for meteor mov't
import os # for interaction with operating sysyem
from os import path # file management
from functools import wraps # for implementing decorators

# Game settings
pygame.init()
pygame.mixer.init()  # for game sounds
WIDTH = 480
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter!") # title
clock = pygame.time.Clock()
FPS = 60

# Some colors we'll use(RGB values)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
  
# Load assets
game_folder = path.dirname(__file__)
assets_folder = os.path.join(game_folder, "assets")
background = pygame.image.load(os.path.join(assets_folder, "space.jpg")).convert()# conversion for faster rendering

# images
bullet_img = pygame.image.load(os.path.join(assets_folder, "bullets.png")).convert_alpha() # optimizing transparecy for the images
explosion_img = pygame.image.load(os.path.join(assets_folder, "explosion.jpg")).convert_alpha()
player_img = pygame.image.load(os.path.join(assets_folder, "space-shooter-ship.png")).convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 40))
meteor_original = pygame.image.load(os.path.join(assets_folder, "meteors.png")).convert()

# sound effects
shoot_sound = pygame.mixer.Sound(os.path.join(assets_folder, "laser.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join(assets_folder, "explosion.wav"))

#  variable names 
bulletImg = pygame.image.load(os.path.join(assets_folder, "bullets.png")).convert_alpha()
explosionImg = pygame.image.load(os.path.join(assets_folder, "explosion.jpg")).convert() #.convert() to improve performance , same pixels as the screen

# Create different meteor size
meteor_img = []
meteor_sizes = [25 , 40, 15] 
for scale in meteor_sizes:
    sized_meteor = pygame.transform.scale(meteor_original, (scale, scale))
    sized_meteor.set_colorkey(BLACK)  # transparency
    meteor_img.append(sized_meteor)

 #decorators
def rate_limited(cooldown):
    
    def decorator(func):
        last_time = {}  # different variable name than other decorators
        @wraps(func) #   ensures the decorated function retains data such as name of the original function 
        def wrapper(self, *args, **kwargs): 
            now = pygame.time.get_ticks() 
            if self not in last_time or now - last_time[self] > cooldown * 1000:
                last_time[self] = now
                return func(self, *args, **kwargs)
        return wrapper
    return decorator


def keep_in_bounds(function):
    
    @wraps(function)
    def wrapper(self, *args, **kwargs):
    
        result = function(self, *args, **kwargs)
        
        
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        return result
    return wrapper

 #Controls sprite rotation timing#
def rotate_sprite(ms=25):
    
    def decorator(func):
        last_time = {}
        @wraps(func) # preserving metadata of the original functin data like(name)
        def wrapper(self, *args, **kwargs):
            t = pygame.time.get_ticks()
            
            if self not in last_time or t - last_time[self] > ms:
                last_time[self] = t # updating the last recorded time 
                return func(self, *args, **kwargs) # calling the original function
        return wrapper
    return decorator

# Game Classes
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y): # x & y center of the ship
        super().__init__() # initializing parent class functionality
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10  # moving upwards
    
    def update(self):
        self.rect.y += self.speedy
      
        if self.rect.bottom < 0:
            self.kill() # remove the bullet that goes of the screen

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.image = pygame.transform.scale(explosion_img, (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame > 8: 
                self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
    
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10 # placing the player near the bottom
        self.speedx = 0  
        self.speed = 8
        self._health = 100 
        
    # Property for health
    @property
    def health(self):
        return self._health
        
    @health.setter  
    def health(self, val): 
        
        if val > 100:
            self._health = 100
        elif val < 0:
            self._health = 0
        else:
            self._health = val

    
    @rate_limited(0.2) # prevents bullets being fired every 0.2sec
    def shoot_bullet(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_bullets.add(bullet)
        all_sprites.add(bullet)
        shoot_sound.play()  # Play shooting sound
        

    def update(self):
        self.move()  
        
        # Check for spacebar to shoot
        keys = pygame.key.get_pressed()  
        if keys[pygame.K_SPACE]:
            self.shoot_bullet()
    
    @keep_in_bounds
    def move(self): # Ensure player stays within the screen boundary
        """Player movement with keyboard controls"""
        self.speedx = 0
        keys = pygame.key.get_pressed()
        
        # Different if-statement formatting
        if keys[pygame.K_RIGHT]:
            self.speedx = self.speed
        if keys[pygame.K_LEFT]:
            self.speedx = -self.speed
            
        self.rect.x += self.speedx

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        # Parent class init
        super().__init__()
        
        # Visual setup
        self.original_image = random.choice(meteor_img) # random meter size
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        
        # Physics attributes
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100) # starting off the screen
        self.speedy = random.randrange(2, 8)  
        self.speedx = random.randrange(-3, 3) 
        
        # Rotation attributes
        self.rot = 0  
        self.rot_speed = random.randrange(3, 8)
    
    @rotate_sprite(25) # rotation runs only every 25ms 
    def rotate(self):
        
        self.rot = (self.rot + self.rot_speed) % 360
        center = self.rect.center  # different variable name
        self.image = pygame.transform.rotate(self.original_image, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = center
    
    def reset(self):
        """Reset meteor position when it goes off screen"""
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(2, 5)
        self.speedx = random.randrange(-3, 3)
        self.rot_speed = random.randrange(3, 8)

    def update(self):
        # Update position
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        # Rotate sprite
        self.rotate()
        
    
        if (self.rect.top > HEIGHT or 
            self.rect.left > WIDTH + 20 or 
            self.rect.right < -20):
            self.reset()
    
    @classmethod
    def create_many(cls, count, groups): # cls to instantiate objects of the class
        
        meteors = []
    
        for i in range(count):
            m = cls()
            for group in groups:
                group.add(m)
            meteors.append(m)
        return meteors


def check_collisions(game_sprites, bullets, meteors, player): 
    # Check if bullets hit meteors
    hits = pygame.sprite.groupcollide(meteors, bullets, True, True)
    for hit in hits:
        # Play explosion sound
        explosion_sound.play()
        
        # Create explosion effect
        expl = Explosion(hit.rect.center, hit.rect.width * 2)
        game_sprites.add(expl)
        
        # Create new meteor and add score
        m = Meteor()
        game_sprites.add(m)
        meteors.add(m)
        global score
        score += 10
    
    
    hits = pygame.sprite.spritecollide(player, meteors, True, pygame.sprite.collide_circle)
    for hit in hits:
        # Play explosion sound
        explosion_sound.play()
        
        # Create explosion effect
        expl = Explosion(hit.rect.center, hit.rect.width * 2)
        game_sprites.add(expl)
        
        player.health -= 20
        # Spawn replacement meteor 
        m = Meteor()
        game_sprites.add(m)
        meteors.add(m)

# Game setup
all_sprites = pygame.sprite.Group()
all_meteors = pygame.sprite.Group()
all_bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

Meteor.create_many(8, [all_sprites, all_meteors])

# Initialize score
score = 0
font = pygame.font.Font(None, 36)

# Main game loop
running = True
while running:
    # Keep game running at the right speed
    clock.tick(FPS)
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update all sprites
    all_sprites.update()
    
    
    check_collisions(all_sprites, all_bullets, all_meteors, player)
    
    # Check if game over
    if player.health <= 0:
        print(f"Game Over! Final score: {score}") 
        running = False
    

    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    

    pygame.draw.rect(screen, GREEN, (10, 10, player.health, 20))
    pygame.draw.rect(screen, WHITE, (10, 10, 100, 20), 2)
    
    # Draw score with slightly different positioning
    score_text = font.render("Score: " + str(score), True, WHITE) 
    screen.blit(score_text, (WIDTH - 140, 10))
    
    # Update screen
    pygame.display.flip()

# Quit game
pygame.quit()