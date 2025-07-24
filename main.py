
import pygame
import numpy as np
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)

class SoundWave:
    def __init__(self, x, y, frequency, amplitude, color):
        self.x = x
        self.y = y
        self.frequency = frequency
        self.amplitude = amplitude
        self.color = color
        self.time = 0
        self.speed = 5
        
    def update(self):
        self.x += self.speed
        self.time += 0.1
        
    def draw(self, screen):
        points = []
        for i in range(50):
            wave_x = self.x + i * 5
            wave_y = self.y + math.sin(self.time + i * self.frequency * 0.1) * self.amplitude
            if 0 <= wave_x <= SCREEN_WIDTH and 0 <= wave_y <= SCREEN_HEIGHT:
                points.append((wave_x, wave_y))
        
        if len(points) > 1:
            pygame.draw.lines(screen, self.color, False, points, 3)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 2
        self.health = 100
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        # Health bar
        health_width = (self.health / 100) * self.width
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_width, 5))

class Audaman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.speed = 5
        self.frequency = 1.0
        self.amplitude = 20
        self.sound_waves = []
        
    def update(self, keys):
        # Movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y = max(0, self.y - self.speed)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y = min(SCREEN_HEIGHT - self.height, self.y + self.speed)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x = max(0, self.x - self.speed)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x = min(SCREEN_WIDTH - self.width, self.x + self.speed)
            
        # Frequency control
        if keys[pygame.K_q]:
            self.frequency = max(0.1, self.frequency - 0.1)
        if keys[pygame.K_e]:
            self.frequency = min(5.0, self.frequency + 0.1)
            
        # Amplitude control
        if keys[pygame.K_z]:
            self.amplitude = max(5, self.amplitude - 2)
        if keys[pygame.K_c]:
            self.amplitude = min(50, self.amplitude + 2)
            
        # Update sound waves
        for wave in self.sound_waves[:]:
            wave.update()
            if wave.x > SCREEN_WIDTH:
                self.sound_waves.remove(wave)
                
    def shoot_wave(self):
        color = BLUE if self.frequency < 2 else PURPLE if self.frequency < 4 else YELLOW
        wave = SoundWave(self.x + self.width, self.y + self.height // 2, 
                        self.frequency, self.amplitude, color)
        self.sound_waves.append(wave)
        
    def draw(self, screen):
        # Draw Audaman as a hero with sound symbol
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, WHITE, (self.x + 25, self.y + 25), 15)
        pygame.draw.circle(screen, BLUE, (self.x + 25, self.y + 25), 10)
        
        # Draw sound waves
        for wave in self.sound_waves:
            wave.draw(screen)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Audaman: The Frequency Hero")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.player = Audaman(50, SCREEN_HEIGHT // 2)
        self.enemies = []
        self.score = 0
        self.wave_timer = 0
        self.enemy_spawn_timer = 0
        
        # Initialize font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def spawn_enemy(self):
        y = random.randint(50, SCREEN_HEIGHT - 90)
        enemy = Enemy(SCREEN_WIDTH, y)
        self.enemies.append(enemy)
        
    def check_collisions(self):
        # Check wave-enemy collisions
        for wave in self.player.sound_waves[:]:
            for enemy in self.enemies[:]:
                if (wave.x < enemy.x + enemy.width and 
                    wave.x + 50 > enemy.x and
                    abs(wave.y - (enemy.y + enemy.height // 2)) < 30):
                    
                    # Damage based on frequency and amplitude
                    damage = int(wave.frequency * wave.amplitude * 0.5)
                    enemy.health -= damage
                    
                    if enemy in self.enemies:
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.score += 100
                        if wave in self.player.sound_waves:
                            self.player.sound_waves.remove(wave)
                        break
                        
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Frequency indicator
        freq_text = self.small_font.render(f"Frequency: {self.player.frequency:.1f} Hz", True, WHITE)
        self.screen.blit(freq_text, (10, 50))
        
        # Amplitude indicator
        amp_text = self.small_font.render(f"Amplitude: {self.player.amplitude}", True, WHITE)
        self.screen.blit(amp_text, (10, 75))
        
        # Instructions
        instructions = [
            "WASD/Arrows: Move",
            "SPACE: Shoot sound wave",
            "Q/E: Adjust frequency",
            "Z/C: Adjust amplitude"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 200, 10 + i * 25))
            
    def run(self):
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.shoot_wave()
                        
            # Get pressed keys
            keys = pygame.key.get_pressed()
            
            # Update game objects
            self.player.update(keys)
            
            for enemy in self.enemies:
                enemy.update()
                
            # Remove enemies that went off screen
            self.enemies = [enemy for enemy in self.enemies if enemy.x > -enemy.width]
            
            # Spawn enemies
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer > 120:  # Spawn every 2 seconds
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
                
            # Check collisions
            self.check_collisions()
            
            # Draw everything
            self.screen.fill(BLACK)
            
            # Draw grid background (sound visualization)
            for i in range(0, SCREEN_WIDTH, 50):
                pygame.draw.line(self.screen, (20, 20, 20), (i, 0), (i, SCREEN_HEIGHT))
            for i in range(0, SCREEN_HEIGHT, 50):
                pygame.draw.line(self.screen, (20, 20, 20), (0, i), (SCREEN_WIDTH, i))
            
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
