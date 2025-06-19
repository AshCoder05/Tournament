# validate_strategies.py

from fight_engine import load_all_strategies, load_boxer
import pygame

def validate_all_strategies(strategies_path="strategies/"):
    paths = load_all_strategies(strategies_path)
    errors = []

    print(f"🧪 Validating {len(paths)} strategy files...\n")

    for i, path in enumerate(paths, 1):
        try:
            boxer = load_boxer(path, 100, 100, (100, 100, 255), "TestBoxer")
            print(f"{i}. ✅ {boxer.strategy} ({boxer.__class__.__name__}) - {path}")
        except Exception as e:
            print(f"{i}. ❌ ERROR in {path}: {e}")
            errors.append((path, str(e)))

    if errors:
        print(f"\n🚫 {len(errors)} invalid strategies found.")
    else:
        print("\n✅ All strategies passed validation.")

if __name__ == "__main__":
    pygame.init()  # Needed to construct vector and avoid init errors
    validate_all_strategies()
