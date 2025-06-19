#Dancer Boxer Class
# This class represents a boxer that moves in a circular orbit around an opponent
# and attacks when close enough. It is designed to be used in a Pygame environment.
# dancer.py
import pygame
import random

# Constants (ideally shared or imported)
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
    def __init__(self, x, y, color, name, strategy="dancer"):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.strategy = strategy
        self.facing = pygame.math.Vector2(1, 0)
        self.health = 100
        self.cooldown = 0
        self.last_attack_frame = -ATTACK_COOLDOWN
        self.orbit_dir = 1
        self.orbit_timer = 0
        self.escape_timer = 0
        self.is_escaping = False
        self.escape_dir = pygame.math.Vector2(0, 0)

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

        margin = ring.margin
        at_left = self.x <= margin
        at_right = self.x >= ring.width - margin
        at_top = self.y <= margin
        at_bottom = self.y >= ring.height - margin

        # Escape logic
        if (at_left or at_right) and (at_top or at_bottom):
            self.is_escaping = True
            self.escape_timer = FPS
            dx = 1 if at_left else (-1 if at_right else 0)
            dy = 1 if at_top else (-1 if at_bottom else 0)
            self.escape_dir = pygame.math.Vector2(dx, dy)

        if self.is_escaping:
            self.x += self.escape_dir.x * SPEED
            self.y += self.escape_dir.y * SPEED
            self.escape_timer -= 1
            if self.escape_timer <= 0:
                self.is_escaping = False
            self.clamp(ring)
            return

        # Orbit logic
        self.orbit_timer += 1
        if self.orbit_timer > FPS * 2:
            self.orbit_dir *= -1
            self.orbit_timer = 0

        moved = False

        # Perpendicular orbit movement
        perpendicular = pygame.math.Vector2(
            direction.y * self.orbit_dir,
            -direction.x * self.orbit_dir
        )

        next_x = self.x + perpendicular.x * SPEED
        next_y = self.y + perpendicular.y * SPEED
        if ring.in_bounds(next_x, next_y):
            self.x = next_x
            self.y = next_y
            moved = True

        # Retreat if too close and not orbiting successfully
        if not moved and distance < STOP_DISTANCE + 20:
            self.x -= direction.x * SPEED
            self.y -= direction.y * SPEED
            moved = True

        # Last resort wiggle
        if not moved:
            wiggle = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize() * SPEED
            self.x += wiggle.x
            self.y += wiggle.y

        self.clamp(ring)

    def clamp(self, ring):
        self.x = max(ring.margin, min(ring.width - ring.margin, self.x))
        self.y = max(ring.margin, min(ring.height - ring.margin, self.y))

