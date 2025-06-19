import pygame
import sys
import random
# A simple 2D boxing match simulation using Pygame
# Init
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D vs 3D - Punch Combat")

FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

BOXER_RADIUS = 20
SPEED = 2
STOP_DISTANCE = 50
ATTACK_RANGE = 40
ATTACK_COOLDOWN = 60  # frames (1 second at 60 FPS)
DAMAGE = 10

font = pygame.font.SysFont("Arial", 20)
class Ring:
    def __init__(self, width, height, margin):
        self.width = width
        self.height = height
        self.margin = margin

    def in_bounds(self, x, y):
        return (
            self.margin <= x <= self.width - self.margin and
            self.margin <= y <= self.height - self.margin
        )

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            (180, 180, 180),
            (self.margin, self.margin, self.width - 2 * self.margin, self.height - 2 * self.margin),
            2
        )
import csv
import os

import os

class MatchLogger:
    def __init__(self, filename="fight_log.csv"):
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Folder where script is
        self.filename = os.path.join(script_dir, filename)
        self.header = [
            "match_id", "strategy_A", "strategy_B", "winner",
            "frames", "boxerA_HP", "boxerB_HP"
        ]
        # Clear file if exists
        with open(self.filename, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.header)
        self.match_id = 1

    def log_result(self, strategy_A, strategy_B, winner, frames, hpA, hpB):
        row = [
            self.match_id,
            strategy_A,
            strategy_B,
            winner,
            frames,
            hpA,
            hpB
        ]
        with open(self.filename, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        self.match_id += 1
logger = MatchLogger()
# This class handles the logging of match results to a CSV file.

# Boxer class represents a fighter in the boxing match
# It includes methods for movement, attacking, and drawing the boxer on the screen.
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
        self.orbit_dir = 1  # 1 = CW, -1 = CCW
        self.orbit_timer = 0
        self.is_escaping = False
        self.escape_dir = pygame.math.Vector2(0, 0)
        self.escape_timer = 0

    def will_collide(self, x, y, opponent):
        next_pos = pygame.math.Vector2(x, y)
        opponent_pos = pygame.math.Vector2(opponent.x, opponent.y)
        return next_pos.distance_to(opponent_pos) < BOXER_RADIUS * 2.2


    
    def clamp_position(self):
        self.x = max(BOXER_RADIUS, min(WIDTH - BOXER_RADIUS, self.x))
        self.y = max(BOXER_RADIUS, min(HEIGHT - BOXER_RADIUS, self.y))


    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), BOXER_RADIUS)
        # Facing direction line
        fx = self.x + self.facing.x * BOXER_RADIUS
        fy = self.y + self.facing.y * BOXER_RADIUS
        pygame.draw.line(win, BLACK, (self.x, self.y), (fx, fy), 2)

        # Show attack
        if self.cooldown == 1:
            punch_pos = pygame.math.Vector2(self.x, self.y) + self.facing * ATTACK_RANGE
            pygame.draw.circle(win, BLACK, (int(punch_pos.x), int(punch_pos.y)), 8)

    def decide_movement(self, opponent, ring):
        direction = pygame.math.Vector2(opponent.x - self.x, opponent.y - self.y)
        distance = direction.length()

        if distance == 0:
            return

        direction = direction.normalize()
        self.facing = direction

        # ESCAPE MODE (only when cornered)
        margin = ring.margin
        at_left = self.x <= margin
        at_right = self.x >= ring.width - margin
        at_top = self.y <= margin
        at_bottom = self.y >= ring.height - margin

        if self.strategy == "dancer":
            if (at_left or at_right) and (at_top or at_bottom):
                self.is_escaping = True
                self.escape_timer = FPS
                dx = 1 if at_left else (-1 if at_right else 0)
                dy = 1 if at_top else (-1 if at_bottom else 0)
                self.escape_dir = pygame.math.Vector2(dx, dy)

            if self.is_escaping:
                next_x = self.x + self.escape_dir.x * SPEED
                next_y = self.y + self.escape_dir.y * SPEED
                if ring.in_bounds(next_x, next_y):
                    self.x = next_x
                    self.y = next_y
                self.escape_timer -= 1
                if self.escape_timer <= 0:
                    self.is_escaping = False
                return

        # AGGRESSOR
        if self.strategy == "aggressor":
            if distance > STOP_DISTANCE:
                next_x = self.x + direction.x * SPEED
                next_y = self.y + direction.y * SPEED
                if ring.in_bounds(next_x, next_y):
                    self.x = next_x
                    self.y = next_y
            return

        # DANCER MAIN BEHAVIOR
        if self.strategy == "dancer":
            self.orbit_timer += 1
            if self.orbit_timer > FPS * 2:
                self.orbit_dir *= -1
                self.orbit_timer = 0

            moved = False

            # Try orbit first
            perpendicular = pygame.math.Vector2(
                direction.y * self.orbit_dir,
                -direction.x * self.orbit_dir
            )
            next_x = self.x + perpendicular.x * SPEED
            next_y = self.y + perpendicular.y * SPEED
            if ring.in_bounds(next_x, next_y) and not self.will_collide(next_x, next_y, opponent):
                self.x = next_x
                self.y = next_y
                moved = True

            # If too close and orbit failed, try retreat
            if not moved and distance < STOP_DISTANCE + 20:
                retreat_x = self.x - direction.x * SPEED
                retreat_y = self.y - direction.y * SPEED
                if ring.in_bounds(retreat_x, retreat_y):
                    self.x = retreat_x
                    self.y = retreat_y
                    moved = True

            # If still stuck, try a small wiggle
            if not moved:
                wiggle = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize() * SPEED
                wiggle_x = self.x + wiggle.x
                wiggle_y = self.y + wiggle.y
                if ring.in_bounds(wiggle_x, wiggle_y):
                    self.x = wiggle_x
                    self.y = wiggle_y






    def try_attack(self, opponent, frame_count):
        if self.health <= 0 or opponent.health <= 0:
            return  # Skip if fight is over

        if frame_count - self.last_attack_frame >= ATTACK_COOLDOWN:
            # Check if opponent is in range
            attack_pos = pygame.math.Vector2(self.x, self.y) + self.facing * ATTACK_RANGE
            opponent_pos = pygame.math.Vector2(opponent.x, opponent.y)
            if attack_pos.distance_to(opponent_pos) <= BOXER_RADIUS:
                opponent.health -= DAMAGE
                print(f"[{frame_count}] {self.name} hit {opponent.name}! {opponent.name} HP: {opponent.health}")
            self.last_attack_frame = frame_count
            self.cooldown = ATTACK_COOLDOWN

    def update_cooldown(self):
        if self.cooldown > 0:
            self.cooldown -= 1

def draw_window(boxer1, boxer2, frame_count, ring):
    WIN.fill(WHITE)
    ring.draw(WIN)
    boxer1.draw(WIN)
    boxer2.draw(WIN)

    h1 = font.render(f"{boxer1.name} HP: {boxer1.health}", True, RED)
    h2 = font.render(f"{boxer2.name} HP: {boxer2.health}", True, BLUE)
    time_display = font.render(f"Frame: {frame_count}", True, BLACK)

    WIN.blit(h1, (20, 20))
    WIN.blit(h2, (WIDTH - 180, 20))
    WIN.blit(time_display, (WIDTH // 2 - 60, 20))

    pygame.display.update()


def main():
    clock = pygame.time.Clock()
    ring = Ring(WIDTH, HEIGHT, BOXER_RADIUS)

    boxerA = Boxer(100, 300, RED, "BoxerA", strategy="aggressor")
    boxerB = Boxer(700, 300, BLUE, "BoxerB", strategy="dancer")

    run = True
    frame_count = 0
    pygame.time.wait(1000)

    while run:
        clock.tick(FPS)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        boxerA.decide_movement(boxerB, ring)
        boxerB.decide_movement(boxerA, ring)

        boxerA.try_attack(boxerB, frame_count)
        boxerB.try_attack(boxerA, frame_count)

        boxerA.update_cooldown()
        boxerB.update_cooldown()

        draw_window(boxerA, boxerB, frame_count, ring)

        winner = "Draw"

        if boxerA.health <= 0 and boxerB.health <= 0:
            print(f"[{frame_count}] 🤝 DRAW!")
            pygame.time.wait(2000)
            winner = "Draw"
            run = False

        elif boxerA.health <= 0:
            print(f"[{frame_count}] 🏆 BoxerB WINS!")
            pygame.time.wait(2000)
            winner = "BoxerB"
            run = False
        elif boxerB.health <= 0:
            print(f"[{frame_count}] 🏆 BoxerA WINS!")
            pygame.time.wait(2000)
            winner = "BoxerA"
            run = False
    # Log the match result
    
        

    logger.log_result(
            strategy_A=boxerA.strategy,
            strategy_B=boxerB.strategy,
            winner=winner,
            frames=frame_count,
            hpA=boxerA.health,
            hpB=boxerB.health
    )

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
# This code simulates a simple 2D boxing match between two fighters using Pygame.