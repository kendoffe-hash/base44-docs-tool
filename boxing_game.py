#!/usr/bin/env python3
"""
Boxing Game - A 2D boxing game with player vs AI combat
Controls:
    Arrow Keys - Move left/right
    A - Jab (fast, low damage)
    S - Hook (medium speed, medium damage)
    D - Uppercut (slow, high damage)
    SPACE - Block
    ESC - Pause/Menu
"""

import pygame
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
GREEN = (50, 200, 50)
YELLOW = (255, 220, 50)
DARK_RED = (150, 30, 30)
DARK_BLUE = (30, 60, 150)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
ORANGE = (255, 150, 50)

# Game States
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4

# Punch Types
class PunchType(Enum):
    JAB = 1
    HOOK = 2
    UPPERCUT = 3

class Particle:
    """Visual effect particle for hits"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -3)
        self.color = color
        self.life = 30
        self.size = random.randint(3, 8)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # Gravity
        self.life -= 1
        self.size = max(1, self.size - 0.2)
    
    def draw(self, screen):
        if self.life > 0:
            alpha = int((self.life / 30) * 255)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Punch:
    """Represents an active punch"""
    def __init__(self, x, y, punch_type, direction):
        self.x = x
        self.y = y
        self.punch_type = punch_type
        self.direction = direction  # 1 for right, -1 for left
        self.active = True
        self.frame = 0
        self.max_frames = 15
        
        # Punch properties based on type
        if punch_type == PunchType.JAB:
            self.damage = 5
            self.speed = 15
            self.range = 60
            self.color = YELLOW
        elif punch_type == PunchType.HOOK:
            self.damage = 10
            self.speed = 10
            self.range = 50
            self.color = ORANGE
        else:  # UPPERCUT
            self.damage = 15
            self.speed = 8
            self.range = 45
            self.color = RED
    
    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.active = False
        self.x += self.speed * self.direction
    
    def get_hitbox(self):
        return pygame.Rect(self.x, self.y - 20, 30, 40)
    
    def draw(self, screen):
        if self.active:
            # Draw punch effect
            alpha = int((1 - self.frame / self.max_frames) * 200)
            size = int(20 + (self.frame / self.max_frames) * 15)
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(s, color_with_alpha, (size, size), size)
            screen.blit(s, (int(self.x - size), int(self.y - size)))

class Boxer:
    """Base class for boxers (player and AI)"""
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 100
        self.color = color
        self.name = name
        self.health = 100
        self.max_health = 100
        self.speed = 5
        self.direction = 1  # 1 for facing right, -1 for facing left
        
        # Combat stats
        self.is_blocking = False
        self.is_punching = False
        self.punch_cooldown = 0
        self.block_cooldown = 0
        self.hit_stun = 0
        self.score = 0
        
        # Animation
        self.bob_offset = 0
        self.bob_direction = 1
        
    def update(self):
        # Update cooldowns
        if self.punch_cooldown > 0:
            self.punch_cooldown -= 1
        if self.block_cooldown > 0:
            self.block_cooldown -= 1
        if self.hit_stun > 0:
            self.hit_stun -= 1
        
        # Bobbing animation
        self.bob_offset += 0.1 * self.bob_direction
        if abs(self.bob_offset) > 3:
            self.bob_direction *= -1
        
        # Keep in bounds
        self.x = max(50, min(SCREEN_WIDTH - 50 - self.width, self.x))
    
    def move(self, dx):
        if self.hit_stun == 0 and not self.is_blocking:
            self.x += dx * self.speed
    
    def punch(self, punch_type):
        if self.punch_cooldown == 0 and self.hit_stun == 0 and not self.is_blocking:
            self.is_punching = True
            self.punch_cooldown = 30
            
            # Create punch object
            punch_x = self.x + (self.width if self.direction > 0 else 0)
            punch_y = self.y + self.height // 2
            return Punch(punch_x, punch_y, punch_type, self.direction)
        return None
    
    def block(self):
        if self.block_cooldown == 0 and self.hit_stun == 0:
            self.is_blocking = True
    
    def take_damage(self, damage):
        if self.is_blocking:
            damage = damage // 3  # Reduce damage when blocking
        
        self.health = max(0, self.health - damage)
        self.hit_stun = 15
        self.is_blocking = False
        return damage
    
    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        # Draw shadow
        shadow_y = SCREEN_HEIGHT - 150
        pygame.draw.ellipse(screen, (0, 0, 0, 50), 
                          (self.x + 5, shadow_y, self.width - 10, 15))
        
        # Apply hit stun effect
        color = self.color
        if self.hit_stun > 0 and self.hit_stun % 4 < 2:
            color = tuple(min(255, c + 100) for c in self.color)
        
        # Draw body
        body_y = self.y + int(self.bob_offset)
        pygame.draw.rect(screen, color, (self.x, body_y, self.width, self.height), border_radius=10)
        
        # Draw head
        head_size = 30
        head_x = self.x + self.width // 2
        head_y = body_y - head_size // 2
        pygame.draw.circle(screen, color, (head_x, head_y), head_size // 2)
        
        # Draw gloves
        glove_color = RED if color == BLUE else BLUE
        glove_size = 15
        
        if self.is_blocking:
            # Blocking pose - gloves up
            pygame.draw.circle(screen, glove_color, 
                             (self.x + 15, body_y + 20), glove_size)
            pygame.draw.circle(screen, glove_color, 
                             (self.x + self.width - 15, body_y + 20), glove_size)
        else:
            # Normal pose
            pygame.draw.circle(screen, glove_color, 
                             (self.x + 10, body_y + 50), glove_size)
            pygame.draw.circle(screen, glove_color, 
                             (self.x + self.width - 10, body_y + 50), glove_size)
        
        # Draw eyes
        eye_color = WHITE
        eye_size = 5
        pygame.draw.circle(screen, eye_color, 
                         (head_x - 8, head_y - 5), eye_size)
        pygame.draw.circle(screen, eye_color, 
                         (head_x + 8, head_y - 5), eye_size)
        
        # Draw blocking indicator
        if self.is_blocking:
            pygame.draw.rect(screen, YELLOW, 
                           (self.x - 5, body_y - 10, self.width + 10, self.height + 20), 3)

class Player(Boxer):
    """Player-controlled boxer"""
    def __init__(self):
        super().__init__(150, SCREEN_HEIGHT - 250, BLUE, "PLAYER")
        self.direction = 1

class Opponent(Boxer):
    """AI-controlled opponent"""
    def __init__(self):
        super().__init__(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 250, RED, "OPPONENT")
        self.direction = -1
        self.ai_timer = 0
        self.ai_state = "idle"
        self.ai_decision_cooldown = 0
    
    def ai_update(self, player):
        """Simple AI behavior"""
        self.ai_timer += 1
        
        if self.ai_decision_cooldown > 0:
            self.ai_decision_cooldown -= 1
            return None
        
        # Calculate distance to player
        distance = abs(self.x - player.x)
        
        # AI decision making
        if self.hit_stun > 0:
            return None
        
        # Random decision every 60 frames
        if self.ai_timer % 60 == 0:
            action = random.choice(["move", "punch", "block", "idle"])
            
            if action == "move":
                if distance > 200:
                    # Move closer
                    self.move(-1)
                elif distance < 100:
                    # Move away
                    self.move(1)
            
            elif action == "punch" and distance < 150:
                # Choose random punch type
                punch_type = random.choice([PunchType.JAB, PunchType.HOOK, PunchType.UPPERCUT])
                punch = self.punch(punch_type)
                self.ai_decision_cooldown = 30
                return punch
            
            elif action == "block":
                self.block()
                self.ai_decision_cooldown = 20
        
        # Stop blocking after a while
        if self.is_blocking and self.ai_timer % 30 == 0:
            self.is_blocking = False
        
        return None

class BoxingGame:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Boxing Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Game objects
        self.player = None
        self.opponent = None
        self.punches = []
        self.particles = []
        
        # UI
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Round timer
        self.round_time = 180  # 3 minutes in seconds
        self.timer = self.round_time * FPS
        
    def reset_game(self):
        """Reset game state for new round"""
        self.player = Player()
        self.opponent = Opponent()
        self.punches = []
        self.particles = []
        self.timer = self.round_time * FPS
        self.state = GameState.PLAYING
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_a:
                        punch = self.player.punch(PunchType.JAB)
                        if punch:
                            self.punches.append(punch)
                    elif event.key == pygame.K_s:
                        punch = self.player.punch(PunchType.HOOK)
                        if punch:
                            self.punches.append(punch)
                    elif event.key == pygame.K_d:
                        punch = self.player.punch(PunchType.UPPERCUT)
                        if punch:
                            self.punches.append(punch)
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_q:
                        self.state = GameState.MENU
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
    
    def update(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move(-1)
        if keys[pygame.K_RIGHT]:
            self.player.move(1)
        if keys[pygame.K_SPACE]:
            self.player.block()
        else:
            self.player.is_blocking = False
        
        # Update player and opponent
        self.player.update()
        self.opponent.update()
        
        # AI behavior
        ai_punch = self.opponent.ai_update(self.player)
        if ai_punch:
            self.punches.append(ai_punch)
        
        # Update punches
        for punch in self.punches[:]:
            punch.update()
            if not punch.active:
                self.punches.remove(punch)
                continue
            
            # Check collision with player
            if punch.direction > 0 and punch.get_hitbox().colliderect(self.opponent.get_hitbox()):
                damage = self.opponent.take_damage(punch.damage)
                self.player.score += damage
                self.create_hit_effect(self.opponent.x + self.opponent.width // 2, 
                                     self.opponent.y + self.opponent.height // 2, RED)
                self.punches.remove(punch)
            
            # Check collision with opponent
            elif punch.direction < 0 and punch.get_hitbox().colliderect(self.player.get_hitbox()):
                damage = self.player.take_damage(punch.damage)
                self.opponent.score += damage
                self.create_hit_effect(self.player.x + self.player.width // 2, 
                                     self.player.y + self.player.height // 2, BLUE)
                self.punches.remove(punch)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # Update timer
        self.timer -= 1
        
        # Check win conditions
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
        elif self.opponent.health <= 0:
            self.state = GameState.GAME_OVER
        elif self.timer <= 0:
            self.state = GameState.GAME_OVER
    
    def create_hit_effect(self, x, y, color):
        """Create particle effect for hits"""
        for _ in range(10):
            self.particles.append(Particle(x, y, color))
    
    def draw_background(self):
        """Draw boxing ring background"""
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            color_value = int(30 + (y / SCREEN_HEIGHT) * 50)
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 20), 
                           (0, y), (SCREEN_WIDTH, y))
        
        # Ring canvas
        canvas_y = SCREEN_HEIGHT - 150
        pygame.draw.rect(self.screen, (180, 150, 120), 
                        (0, canvas_y, SCREEN_WIDTH, 150))
        
        # Ring lines
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, (160, 130, 100), 
                           (i, canvas_y), (i + 25, canvas_y), 3)
        
        # Ring ropes
        rope_colors = [RED, RED, RED]
        rope_heights = [canvas_y - 30, canvas_y - 60, canvas_y - 90]
        for height, color in zip(rope_heights, rope_colors):
            pygame.draw.line(self.screen, color, (0, height), (SCREEN_WIDTH, height), 5)
    
    def draw_ui(self):
        """Draw UI elements"""
        # Health bars
        bar_width = 300
        bar_height = 30
        bar_y = 30
        
        # Player health bar
        pygame.draw.rect(self.screen, DARK_GRAY, (50, bar_y, bar_width, bar_height))
        player_health_width = int((self.player.health / self.player.max_health) * bar_width)
        pygame.draw.rect(self.screen, BLUE, (50, bar_y, player_health_width, bar_height))
        pygame.draw.rect(self.screen, WHITE, (50, bar_y, bar_width, bar_height), 3)
        
        # Player name and health
        player_text = self.font_small.render(f"{self.player.name}: {int(self.player.health)}", 
                                            True, WHITE)
        self.screen.blit(player_text, (50, bar_y - 30))
        
        # Opponent health bar
        opp_bar_x = SCREEN_WIDTH - 50 - bar_width
        pygame.draw.rect(self.screen, DARK_GRAY, (opp_bar_x, bar_y, bar_width, bar_height))
        opp_health_width = int((self.opponent.health / self.opponent.max_health) * bar_width)
        pygame.draw.rect(self.screen, RED, (opp_bar_x, bar_y, opp_health_width, bar_height))
        pygame.draw.rect(self.screen, WHITE, (opp_bar_x, bar_y, bar_width, bar_height), 3)
        
        # Opponent name and health
        opp_text = self.font_small.render(f"{self.opponent.name}: {int(self.opponent.health)}", 
                                         True, WHITE)
        self.screen.blit(opp_text, (opp_bar_x, bar_y - 30))
        
        # Timer
        seconds = self.timer // FPS
        minutes = seconds // 60
        seconds = seconds % 60
        timer_text = self.font_medium.render(f"{minutes}:{seconds:02d}", True, YELLOW)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(timer_text, timer_rect)
        
        # Scores
        score_text = self.font_small.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (50, bar_y + 40))
        
        opp_score_text = self.font_small.render(f"Score: {self.opponent.score}", True, WHITE)
        opp_score_rect = opp_score_text.get_rect(right=SCREEN_WIDTH - 50, top=bar_y + 40)
        self.screen.blit(opp_score_text, opp_score_rect)
        
        # Controls hint
        controls = self.font_small.render("A:Jab S:Hook D:Uppercut SPACE:Block", True, LIGHT_GRAY)
        controls_rect = controls.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.screen.blit(controls, controls_rect)
    
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_large.render("BOXING GAME", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "Controls:",
            "Arrow Keys - Move",
            "A - Jab (fast, low damage)",
            "S - Hook (medium)",
            "D - Uppercut (slow, high damage)",
            "SPACE - Block",
            "",
            "Press ENTER to Start",
            "Press ESC to Quit"
        ]
        
        y = 280
        for line in instructions:
            text = self.font_small.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 45
    
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Determine winner
        if self.player.health <= 0:
            winner_text = "OPPONENT WINS!"
            winner_color = RED
        elif self.opponent.health <= 0:
            winner_text = "PLAYER WINS!"
            winner_color = BLUE
        else:
            # Time ran out - check scores
            if self.player.score > self.opponent.score:
                winner_text = "PLAYER WINS BY POINTS!"
                winner_color = BLUE
            elif self.opponent.score > self.player.score:
                winner_text = "OPPONENT WINS BY POINTS!"
                winner_color = RED
            else:
                winner_text = "DRAW!"
                winner_color = YELLOW
        
        # Winner announcement
        winner = self.font_large.render(winner_text, True, winner_color)
        winner_rect = winner.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(winner, winner_rect)
        
        # Final scores
        score_text = self.font_medium.render(
            f"Player: {self.player.score}  -  Opponent: {self.opponent.score}", 
            True, WHITE
        )
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(score_text, score_rect)
        
        # Options
        restart = self.font_small.render("Press ENTER to Play Again", True, WHITE)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(restart, restart_rect)
        
        menu = self.font_small.render("Press ESC for Menu", True, WHITE)
        menu_rect = menu.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(menu, menu_rect)
    
    def draw_paused(self):
        """Draw pause screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        paused = self.font_large.render("PAUSED", True, YELLOW)
        paused_rect = paused.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(paused, paused_rect)
        
        # Options
        resume = self.font_small.render("Press ESC to Resume", True, WHITE)
        resume_rect = resume.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(resume, resume_rect)
        
        quit_text = self.font_small.render("Press Q for Menu", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(quit_text, quit_rect)
    
    def draw(self):
        """Draw everything"""
        if self.state == GameState.MENU:
            self.draw_menu()
        
        elif self.state == GameState.PLAYING:
            self.draw_background()
            
            # Draw game objects
            self.player.draw(self.screen)
            self.opponent.draw(self.screen)
            
            for punch in self.punches:
                punch.draw(self.screen)
            
            for particle in self.particles:
                particle.draw(self.screen)
            
            self.draw_ui()
        
        elif self.state == GameState.PAUSED:
            self.draw_background()
            self.player.draw(self.screen)
            self.opponent.draw(self.screen)
            self.draw_ui()
            self.draw_paused()
        
        elif self.state == GameState.GAME_OVER:
            self.draw_background()
            self.player.draw(self.screen)
            self.opponent.draw(self.screen)
            self.draw_ui()
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    """Entry point"""
    game = BoxingGame()
    game.run()

if __name__ == "__main__":
    main()
