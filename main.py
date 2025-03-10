import pygame
import time
import random
import os
from os import path

# Settings
pygame.init()
pygame.mixer.init()  # Sounds
WIDTH = 800
HEIGHT = 800
Screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooting Game!")
clock = pygame.time.Clock()
FPS = 60  # frame per second

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
  
# Images and Sounds
game_folder = path.dirname(__file__)
assets_folder = os.path.join(game_folder, "assets")
background = pygame.image.load(os.path.join(assets_folder, "space.jpg")).convert()


# bullets and explosion images
bullet_img = pygame.image.load(os.path.join(assets_folder, "bullets.png")).convert_alpha()
explosion_img = pygame.image.load(os.path.join(assets_folder, "explosion.jpg")).convert_alpha()

# Load player ship image
player_img = pygame.image.load(os.path.join(assets_folder, "space-shooter-ship.png")).convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 40))  # Adjust size as needed

meteor_original = pygame.image.load(os.path.join(assets_folder, "meteors.webp")).convert()
bullet_img = pygame.image.load(os.path.join(assets_folder, "bullets.png")).convert_alpha()
explosion_img = pygame.image.load(os.path.join(assets_folder, "explosion.jpg")).convert()

# Create different sized versions of the meteor
meteor_img = []
for scale in [30, 25, 35]:  # Different sizes for variety
    sized_meteor = pygame.transform.scale(meteor_original, (scale, scale))
    # Make black background transparent (if needed)
    sized_meteor.set_colorkey(BLACK)
    meteor_img.append(sized_meteor)

# Game Classes
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((5, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10  # Negative so bullet goes up
    
    def update(self):
        self.rect.y += self.speed_y
        # Kill the bullet when it goes off screen
        if self.rect.bottom < 0:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.speed = 8
        self.last_bullet_shot = pygame.time.get_ticks()
        self.health = 100

    def shoot_bullet(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_bullet_shot > 200:
            self.last_bullet_shot = current_time
            b = Bullet(self.rect.centerx, self.rect.top)
            all_bullets.add(b)
            all_sprites.add(b)

    def update(self):
        self.movement()
        self.boundaries()
        # Check for spacebar press to shoot
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE]:
            self.shoot_bullet()
    
    def movement(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_RIGHT]:
            self.speed_x = self.speed
        if keystate[pygame.K_LEFT]:
            self.speed_x = -self.speed
        self.rect.x += self.speed_x
    
    def boundaries(self):
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = random.choice(meteor_img)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speed_y = random.randrange(2, 8)
        self.speed_x = random.randrange(-3, 3)
        self.last_rotation = pygame.time.get_ticks()
        self.rotation_degree = 0
        self.rotation_speed = random.randrange(3, 8)
    
    def rotate(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_rotation > 25:  # ms
            self.last_rotation = current_time
            self.rotation_degree = (self.rotation_degree + self.rotation_speed) % 360
            old_center = self.rect.center
            self.image = pygame.transform.rotate(self.original_image, self.rotation_degree)
            self.rect = self.image.get_rect()
            self.rect.center = old_center
    
    def spawn_new_meteor(self):
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speed_y = random.randrange(2, 5)
        self.speed_x = random.randrange(-3, 3)
        self.rotation_speed = random.randrange(3, 8)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.rotate()  # Add rotation for visual effect
        
        # Reset if meteor goes off screen
        if self.rect.top > HEIGHT or self.rect.left > WIDTH + 20 or self.rect.right < -20:
            self.spawn_new_meteor()

# Function to check collisions
def check_collisions():
    # Check if bullets hit meteors
    hits = pygame.sprite.groupcollide(all_meteors, all_bullets, True, True)
    for hit in hits:
        # Spawn a new meteor when one is destroyed
        m = Meteor()
        all_sprites.add(m)
        all_meteors.add(m)
        global score
        score += 10
    
    # Check if meteors hit player
    hits = pygame.sprite.spritecollide(player, all_meteors, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.health -= 20
        # Spawn a new meteor when one hits the player
        m = Meteor()
        all_sprites.add(m)
        all_meteors.add(m)

# Game Sprites
all_sprites = pygame.sprite.Group()
all_meteors = pygame.sprite.Group()
all_bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create meteors
for i in range(8):
    m = Meteor()
    all_meteors.add(m)
    all_sprites.add(m)

# Game score
score = 0
font = pygame.font.Font(None, 36)

# Main Game
running = True
while running:
    clock.tick(FPS)
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update sprites
    all_sprites.update()
    
    # Check for collisions
    check_collisions()
    
    # End game if player health is depleted
    if player.health <= 0:
        print("Game Over! Your score:", score)
        running = False
    
    # Draw everything
    Screen.blit(background, (0, 0))  # Draw background
    all_sprites.draw(Screen)
    
    # Draw health bar
    pygame.draw.rect(Screen, GREEN, (10, 10, player.health, 20))
    pygame.draw.rect(Screen, WHITE, (10, 10, 100, 20), 2)
    
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    Screen.blit(score_text, (WIDTH - 150, 10))
    
    # Update display
    pygame.display.flip()

pygame.quit()