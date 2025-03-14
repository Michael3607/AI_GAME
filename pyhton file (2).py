import pygame
import random
import math

# Initialize pygame
pygame.init()

# Set up display
width, height = 1500, 1000
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pygame Test Game")

# Set up the player
player_x, player_y = width // 2, height // 2
player_width, player_height = 50, 50
player_color = (0, 128, 255)
player_speed = 10
player_health = 100

# Projectile setup
projectiles = []
# 1 = bullet, 2 = teammate spawner
projectile_type = 1   
last_shot_time = 0  # time in milliseconds of the last shot
shoot_cooldown = 500  # time in milliseconds between shots
burstAmount = 0  # amount of bullets shot in a burst

class Projectile:
    def __init__(self, x, y, radius, color, velocity):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity = velocity

        # Calculate initial velocity based on mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
        self.x_vel = math.cos(angle) * self.velocity
        self.y_vel = math.sin(angle) * self.velocity

    def draw(self, window):
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)

    def move(self):
        # Move the projectile based on the initial velocity
        self.x += self.x_vel
        self.y += self.y_vel
        # Delete the projectile if it goes off the screen
        if self.x < 0 or self.x > width or self.y < 0 or self.y > height:
            projectiles.remove(self)

def shoot_projectile(x, y):
    global burstAmount
    burstAmount += 1
    projectile = Projectile(x, y, 5, (255, 0, 0), 25)
    projectiles.append(projectile)

buildings = []
# building setup
last_building_time = 0
building_cooldown = 500
class Building:

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

def build(type):
    if type == 1:
        typeW = 50
        typeH = 50
    if type == 2:
        typeW = 100
        typeH = 100
    x, y = pygame.mouse.get_pos()
    building = Building(x, y, typeW, typeH, (0, 255, 0))
    buildings.append(building)

def check_collision(rect, buildings):
    for building in buildings:
        building_rect = pygame.Rect(building.x, building.y, building.width, building.height)
        if rect.colliderect(building_rect):
            return True
    return False

enemies = []
kill_count = 0
class Enemy:
    def __init__(self, x, y, width, height, color, health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.health = health
        
    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

    def move(self):
        # Move towards the player
        if self.x < player_x:
            self.x += 1
        if self.x > player_x:
            self.x -= 1
        if self.y < player_y:
            self.y += 1
        if self.y > player_y:
            self.y -= 1

    def take_damage(self, damage):
        global kill_count
        self.health -= damage
        if self.health <= 0:
            enemies.remove(self)
            kill_count += 1

def spawn_enemy():
    x = random.randint(0, width)
    y = random.randint(0, height)
    enemy = Enemy(x, y, 50, 50, (255, 0, 0), 50)
    enemies.append(enemy)

# Run the game loop
running = True
while running:
    current_time = pygame.time.get_ticks()  # get the time in milliseconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # WASD controls
    keys = pygame.key.get_pressed()
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
        if player_rect.x >= 0 and not check_collision(player_rect, buildings):
            player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed
        if player_rect.x <= width - player_width and not check_collision(player_rect, buildings):
            player_x += player_speed
    if keys[pygame.K_UP]:
        player_rect.y -= player_speed
        if player_rect.y >= 0 and not check_collision(player_rect, buildings):
            player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_rect.y += player_speed
        if player_rect.y <= height - player_height and not check_collision(player_rect, buildings):
            player_y += player_speed

    # Mouse setup for shooting projectiles
    mouse = pygame.mouse.get_pressed()
    if mouse[0]:  # Left mouse button clicked
        if current_time - last_shot_time > shoot_cooldown:
            burstAmount = 0  # Reset burstAmount after cooldown
            last_shot_time = current_time  # Update last_shot_time
        if burstAmount < 5:
            shoot_projectile(player_x + player_width // 2, player_y)
            burstAmount += 1
    # Mouse setup for building buildings right click
    if mouse[2]:
        if current_time - last_building_time > building_cooldown:
            last_building_time = current_time
            build(1)
    # Mouse set up for middle click
    if mouse[1]:
        if current_time - last_building_time > building_cooldown:
            last_building_time = current_time
            build(2)
    # Remove extra buildings
    if len(buildings) >= 4:
        buildings.pop(0)

    # Spawn enemies periodically
    if len(enemies) < 5 and random.randint(0, 100) < 2:
        spawn_enemy()

    # Fill the background
    window.fill((0, 0, 0))

    # Move and draw projectiles
    for projectile in projectiles:
        projectile.move()
        projectile.draw(window)
        # Check for collisions with enemies
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if pygame.Rect(projectile.x - projectile.radius, projectile.y - projectile.radius, projectile.radius * 2, projectile.radius * 2).colliderect(enemy_rect):
                enemy.take_damage(25)
                if projectile in projectiles:
                    projectiles.remove(projectile)

    # Move and draw enemies
    for enemy in enemies:
        enemy.move()
        enemy.draw(window)
        # Check for collisions with player
        if pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height).colliderect(player_rect):
            player_health -= 1
            if player_health <= 0:
                running = False

    for building in buildings:
        building.draw(window)

    # Draw the player
    pygame.draw.rect(window, player_color, (player_x, player_y, player_width, player_height))

    # Draw player health
    font = pygame.font.SysFont(None, 36)
    health_text = font.render(f'Health: {player_health}', True, (255, 255, 255))
    window.blit(health_text, (10, 10))

    # Draw kill count
    kill_text = font.render(f'Kills: {kill_count}', True, (255, 255, 255))
    window.blit(kill_text, (10, 50))

    # Check for win condition
    if kill_count >= 100:
        win_text = font.render('You Win!', True, (255, 255, 255))
        window.blit(win_text, (width // 2 - 50, height // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit pygame
pygame.quit()