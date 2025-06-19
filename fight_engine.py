# ✅ fight_engine.py (now with loader + leaderboard)
import importlib.util
import os
import pandas as pd
import pygame
import csv

# --- Ring ---
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

# --- Match Logger ---
class MatchLogger:
    def __init__(self, filename="fight_log.csv"):
        self.filename = filename
        self.header = [
            "match_id", "strategy_A", "strategy_B", "winner",
            "frames", "boxerA_HP", "boxerB_HP"
        ]
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

# --- Strategy Loader ---

def load_boxer(path, x, y, color, name):
    spec = importlib.util.spec_from_file_location("BoxerModule", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    boxer = module.Boxer(x, y, color, name)

    return boxer

def load_all_strategies(folder):
    files = sorted([f for f in os.listdir(folder) if f.endswith(".py")])
    paths = [os.path.join(folder, f) for f in files]
    return paths

# --- Leaderboard Printer ---
def print_leaderboard(log_path):
    df = pd.read_csv(log_path)

    def outcome(row):
        if row['winner'] == "BoxerA":
            return row['strategy_A']
        elif row['winner'] == "BoxerB":
            return row['strategy_B']
        else:
            return "Draw"

    df['result'] = df.apply(outcome, axis=1)

    summary = df['result'].value_counts().to_frame(name='Wins')
    summary['Matches'] = df['strategy_A'].append(df['strategy_B']).value_counts()
    summary['Win Rate (%)'] = (summary['Wins'] / summary['Matches']) * 100
    print("\n🏆 Leaderboard:")
    print(summary.sort_values(by='Win Rate (%)', ascending=False).fillna(0).round(2))
