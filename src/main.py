import time
import os
from click import command, option
from datetime import datetime
from pathlib import Path
from config import DISPLAY_MATCH_DURATION, DISPLAY_STANDINGS_DURATION
from display import setup_matrix, display_match, display_standings
from utils import show_startup_screen, start_background_updater, get_latest_data, parse_date_input

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

@command()
@option("-l", "--league", envvar="LEAGUE", default="bel")
@option("-d", "--date", envvar="DATE", default=None)

def main(league, date):
    print(f"Starting LED Matrix Scoreboard for league: {league}")
    
    # Setup the LED matrix
    matrix = setup_matrix()
    
    # Show startup screen
    show_startup_screen(matrix, league)

    # Parse the date input
    if date:
        current_date = parse_date_input(date)
        print(f"Using date: {current_date.strftime('%d/%m/%Y')}")
        start_background_updater(league, current_date)
    else:
        print(f"Using today's date: {datetime.now().strftime('%d/%m/%Y')}")
        start_background_updater(league, None)

    # Wait for initial data
    print("Waiting for initial data...")
    while True:
        matches, standings = get_latest_data()
        if matches:
            print("Initial data loaded!")
            break
        time.sleep(1)

    # Main display loop
    while True:
        # Display Matches
        matches, _ = get_latest_data()
        
        for match in matches:
            display_match(matrix, match, league)
            time.sleep(DISPLAY_MATCH_DURATION)

        # Display Standings
        _ , standings = get_latest_data()

        if standings:
            display_standings(matrix, standings)
            time.sleep(DISPLAY_STANDINGS_DURATION)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        pass