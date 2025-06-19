# simulate_match.py

import pygame
import sys
from fight_engine import Ring, MatchLogger, load_boxer

WIDTH, HEIGHT = 800, 600
FPS = 60

def simulate_match(pathA, pathB, logger=None, display=False):
    pygame.init()
    if display:
        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    else:
        WIN = pygame.Surface((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    ring = Ring(WIDTH, HEIGHT, 20)

    boxerA = load_boxer(pathA, 100, 300, (255, 0, 0), "BoxerA")
    boxerB = load_boxer(pathB, 700, 300, (0, 0, 255), "BoxerB")

    frame_count = 0
    run = True
    while run:
        clock.tick(FPS)
        frame_count += 1

        boxerA.decide_movement(boxerB, ring)
        boxerB.decide_movement(boxerA, ring)

        boxerA.try_attack(boxerB, frame_count)
        boxerB.try_attack(boxerA, frame_count)

        boxerA.update_cooldown()
        boxerB.update_cooldown()

        if display:
            WIN.fill((255, 255, 255))
            ring.draw(WIN)
            boxerA.draw(WIN)
            boxerB.draw(WIN)
            pygame.display.update()

        if boxerA.health <= 0 or boxerB.health <= 0:
            run = False

    winner = "Draw"
    if boxerA.health <= 0 and boxerB.health > 0:
        winner = "BoxerB"
    elif boxerB.health <= 0 and boxerA.health > 0:
        winner = "BoxerA"

    if logger:
        logger.log_result(
            strategy_A=boxerA.strategy,
            strategy_B=boxerB.strategy,
            winner=winner,
            frames=frame_count,
            hpA=boxerA.health,
            hpB=boxerB.health
        )

    pygame.quit()

# CLI support
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simulate_match.py strategies/a.py strategies/b.py")
        sys.exit(1)

    pathA = sys.argv[1]
    pathB = sys.argv[2]

    simulate_match(pathA, pathB, logger=None, display=True)
