# main.py

import os
from fight_engine import MatchLogger
from simulate_match import simulate_match

# Paths
STRATEGY_DIR = "strategies"
LOG_DIR = "logs"
LOG_FILENAME = "fight_log.csv"

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Get all .py strategy files from strategies folder
strategies = sorted([
    f for f in os.listdir(STRATEGY_DIR) if f.endswith(".py")
])

# Initialize logger
logger = MatchLogger(filename=os.path.join(LOG_DIR, LOG_FILENAME))

# Round-robin tournament
for i in range(len(strategies)):
    for j in range(i + 1, len(strategies)):
        fileA = strategies[i]
        fileB = strategies[j]

        pathA = os.path.join(STRATEGY_DIR, fileA)
        pathB = os.path.join(STRATEGY_DIR, fileB)

        print(f"🔁 MATCH: {fileA} vs {fileB}")
        simulate_match(pathA, pathB, logger, display=True)

print(f"\n✅ Tournament complete! Results saved to: {os.path.join(LOG_DIR, LOG_FILENAME)}")
