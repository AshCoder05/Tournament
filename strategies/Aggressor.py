# Boxer class for a simple boxing game simulation
# This class represents a boxer with attributes and methods for movement, attacking, and drawing on the screen.
#Aggressor is a simple AI that follows and attacks the opponent.

# aggressor.py
import pygame
import random

# Constants (should be imported from your main config ideally)
BOXER_RADIUS = 20
SPEED = 2
STOP_DISTANCE = 40
ATTACK_RANGE = 40
ATTACK_COOLDOWN = 60
DAMAGE = 10
FPS = 60
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)

class Boxer:
    def __init__(self, x, y, color, name, strategy="aggressor"):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.strategy = strategy
        self.facing = pygame.math.Vector2(1, 0)
        self.health = 100
        self.cooldown = 0
        self.last_attack_frame = -ATTACK_COOLDOWN

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), BOXER_RADIUS)
        fx = self.x + self.facing.x * BOXER_RADIUS
        fy = self.y + self.facing.y * BOXER_RADIUS
        pygame.draw.line(win, BLACK, (self.x, self.y), (fx, fy), 2)

        if self.cooldown == 1:
            punch_pos = pygame.math.Vector2(self.x, self.y) + self.facing * ATTACK_RANGE
            pygame.draw.circle(win, BLACK, (int(punch_pos.x), int(punch_pos.y)), 8)

    def update_cooldown(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def try_attack(self, opponent, frame_count):
        if self.health <= 0 or opponent.health <= 0:
            return

        if frame_count - self.last_attack_frame >= ATTACK_COOLDOWN:
            attack_pos = pygame.math.Vector2(self.x, self.y) + self.facing * ATTACK_RANGE
            opponent_pos = pygame.math.Vector2(opponent.x, opponent.y)
            if attack_pos.distance_to(opponent_pos) <= BOXER_RADIUS:
                opponent.health -= DAMAGE
                print(f"[{frame_count}] {self.name} hit {opponent.name}! {opponent.name} HP: {opponent.health}")
            self.last_attack_frame = frame_count
            self.cooldown = ATTACK_COOLDOWN

    def decide_movement(self, opponent, ring):
        direction = pygame.math.Vector2(opponent.x - self.x, opponent.y - self.y)
        distance = direction.length()

        if distance == 0:
            return

        direction = direction.normalize()
        self.facing = direction

        if distance > STOP_DISTANCE * 0.9:
            next_x = self.x + direction.x * SPEED
            next_y = self.y + direction.y * SPEED
            if ring.in_bounds(next_x, next_y):
                self.x = next_x
                self.y = next_y
        else:
            self.facing = direction

        # Clamp to ring
        self.x = max(ring.margin, min(ring.width - ring.margin, self.x))
        self.y = max(ring.margin, min(ring.height - ring.margin, self.y))
