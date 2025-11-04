#!/usr/bin/env python3
"""Simpler launcher: minimal dependencies and straightforward code.

Uses os.path and importlib to load `PlayerData.py` from the "Bonus Classes"
folder and runs `shroom_raider.py -f <level>` as a subprocess.
"""

import os, sys, subprocess, tempfile, json, time
from Bonus_Classes.PlayerData import Data

HERE = os.path.dirname(__file__)

def list_levels():
	lvl_dir = os.path.join(HERE, "Levels")
	if not os.path.isdir(lvl_dir):
		return []
	files = [f for f in sorted(os.listdir(lvl_dir)) if f.endswith('.txt')]
	return files

def choose_level(files):
	if not files:
		print("No levels in Bonus/Levels/")
		return None
	print("Available levels:")
	for i, name in enumerate(files, 1):
		print(" %d. %s" % (i, name))
	while True:
		choice = input("Select level number or 'q' to quit: ").strip()
		if choice == 'q': return None
		if choice.isdigit():
			n = int(choice)
			if 1 <= n <= len(files): return files[n-1]
		print("Invalid choice")

def launch_game(level_name):
	script = os.path.join(HERE, 'shroom_raider.py')
	level_path = os.path.join(HERE, 'Levels', level_name)
	# create a temporary report file path for the game to write its run summary

	# ! refactor this so its the job of PlayerData to detect and store changes in shroom_raider
	fd, report_path = tempfile.mkstemp(prefix='shroom_report_', suffix='.json', dir=HERE)
	os.close(fd)
	cmd = [sys.executable, script, '-f', level_path, '-R', report_path]
	print('Running:', ' '.join(cmd))
	rc = subprocess.call(cmd)
	report = None
	if os.path.exists(report_path):
		for attempt in range(5):
			try:
				if os.path.getsize(report_path) == 0:
					raise ValueError('report file empty')
				with open(report_path, 'r', encoding='utf-8') as f:
					report = json.load(f)
				break
			except Exception as e:
				if attempt < 4:
					time.sleep(0.1)
					continue
				print('Failed to read report:', e)
		try:
			os.remove(report_path)
		except Exception:
			pass
	return rc, report


def main():
	print('WELCOME TO SHROOM RAIDER')
	username = input("Username (Enter=guest): ").strip() or 'GUEST'
	pdata = None
	if Data is not None:
		try: pdata = Data(username); print('Loaded', pdata)
		except Exception: pdata = None

	# Main menu loop: choose a level, run it, then return here. Save data on
	# win (0) or loss (2). Choosing 'q' at level selection exits.
	while True:
		files = list_levels()
		lvl = choose_level(files)
		if not lvl:
			print('No level chosen, exiting.'); break

		# play loop for this level; after each run offer options
		while True:
			rc, report = launch_game(lvl)

			# One attempt to (re)create pdata if missing
			if pdata is None and Data is not None:
				try: pdata = Data(username)
				except Exception: pdata = None

			if pdata is not None:
				try:
					if report is not None:
						pdata.total_mushrooms_collected += int(report.get('mushrooms_collected', 0))
						pdata.total_tiles_walked += int(report.get('moves_made', 0))
						if report.get('win'): pdata.total_wins += 1
						pdata.total_times += 1
					elif rc in (0, 2):
						if rc == 0: pdata.total_wins += 1
						pdata.total_times += 1
					pdata.save(); print('PlayerData saved')
				except Exception as e:
					print('Save failed:', e)

			# present options to the player instead of immediately returning
			while True:
				print('\nRun finished. Options:')
				print("  r - replay level")
				print("  m - return to main menu")
				print("  s - view statistics")
				print("  q - quit launcher")
				choice = input('Choose (r/m/s/q): ').strip().lower()
				if choice in ('r', 'replay'):
					print('Replaying...')
					break  # break inner options loop to replay
				if choice in ('m', 'menu'):
					print('Returning to main menu...')
					break  # break inner options loop and outer play loop
				if choice in ('s', 'statistics'):
					# show stats (attempt to load/instantiate if needed)
					if pdata is None:
						try:
							# try a direct import now that package layout should exist
							from Bonus.Bonus_Classes.PlayerData import Data as DataClass
							pdata = DataClass(username)
						except Exception as e:
							print('Cannot load statistics:', e); pdata = None
					if pdata is None:
						print('No statistics available for this player')
					else:
						try:
							print('\nPlayer statistics:')
							print(pdata)
						except Exception as e:
							print('Failed to display statistics:', e)
					continue
				if choice in ('q', 'quit'):
					print('Quitting launcher.'); sys.exit(0)
				print('Invalid choice')

			# if user chose replay, continue playing this level
			if choice in ('r', 'replay'):
				continue
			# if user chose menu, break play loop to choose new level
			if choice in ('m', 'menu'):
				break
		# end play loop -> back to level selection


if __name__ == '__main__':
	main()

