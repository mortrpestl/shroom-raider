import os, sys, subprocess, tempfile, json
from Bonus_Classes.PlayerData import PlayerData

HERE = os.path.dirname(__file__)
LEVELS_DIR = os.path.join(HERE, "Levels")

def list_levels():
    if not os.path.isdir(LEVELS_DIR):
        return []
    return sorted(f for f in os.listdir(LEVELS_DIR) if f.endswith('.txt'))

def choose_level(files):
    if not files:
        print("No levels in Levels/")
        return None
    print("Available levels:")
    for i, name in enumerate(files, 1):
        print(f" {i}. {name}")
    while True:
        choice = input("Select level number or 'q' to quit: ").strip()
        if choice.lower() == 'q':
            return None
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(files):
                return files[n - 1]
        print("Invalid choice.")

def launch_game(level_name):
    script = os.path.join(HERE, "shroom_raider.py")
    level_path = os.path.join(LEVELS_DIR, level_name)
    fd, report_path = tempfile.mkstemp(prefix='shroom_report_', suffix='.json', dir=HERE)
    os.close(fd)

    cmd = [sys.executable, script, "-f", level_path, "-R", report_path]
    print("Running:", " ".join(cmd))
    rc = subprocess.call(cmd)

    report = None
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
        except Exception as e:
            print("Failed to read report:", e)
        finally:
            os.remove(report_path)
    return rc, report

def update_player_data(pdata, report, rc):
    if report:
        pdata.total_mushrooms_collected += int(report.get("mushrooms_collected", 0))
        pdata.total_tiles_walked += int(report.get("moves_made", 0))
        if report.get("win"): pdata.total_wins += 1
        pdata.total_times += 1
    elif rc in (0, 2):
        if rc == 0: pdata.total_wins += 1
        pdata.total_times += 1
    pdata.save()
    print("PlayerData saved.")

def show_statistics(pdata):
    if pdata:
        print("\nPlayer statistics:")
        print(pdata)
    else:
        print("No statistics available.")

def main():
    print("WELCOME TO SHROOM RAIDER")
    username = input("Username (Enter=guest): ").strip() or "GUEST"
    pdata = None
    try:
        pdata = PlayerData(username)
        print("Loaded", pdata)
    except Exception:
        pdata = None

    while True:
        files = list_levels()
        lvl = choose_level(files)
        if not lvl:
            print("No level chosen, exiting.")
            break

        while True:
            rc, report = launch_game(lvl)
            if pdata:
                update_player_data(pdata, report, rc)

            # Post-run options
            while True:
                print("""
Run finished. Options:
  r - replay level
  m - return to main menu
  s - view statistics
  q - quit launcher
""")
                choice = input("Choose (r/m/s/q): ").strip().lower()
                if choice in ("r", "replay"):
                    break  # replay
                if choice in ("m", "menu"):
                    break  # return to menu
                if choice in ("s", "statistics"):
                    show_statistics(pdata)
                    continue
                if choice in ("q", "quit"):
                    print("Quitting launcher.")
                    sys.exit(0)
                print("Invalid choice.")

            if choice in ("r", "replay"):
                continue
            if choice in ("m", "menu"):
                break  # back to level selection

if __name__ == "__main__":
    main()
