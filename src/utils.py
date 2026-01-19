import os
import time
import threading
from datetime import datetime
from PIL import Image
from functools import lru_cache
from zoneinfo import ZoneInfo
from config import LOGO_SIZE, LOGOS_BASE_PATH, LOCAL_TIMEZONE, MAX_DAYS_AHEAD
from api import fetch_matches, fetch_standings

_current_matches = []
_current_standings = []
_current_match_date = None
_data_lock = threading.Lock()


def parse_date_input(date_string):
    today = datetime.now()
    parsed_date = datetime.strptime(date_string, "%m%d").replace(year=today.year)
    
    # If date is in the past, assume next year
    if parsed_date.date() < today.date():
        parsed_date = parsed_date.replace(year=today.year + 1)
    
    return parsed_date


def show_startup_screen(matrix, league):
    # Load league logo
    league_logo_path = f'{LOGOS_BASE_PATH}/{league}/league_logo.png'
    
    try:
        league_logo = Image.open(league_logo_path)
        league_logo = league_logo.resize(LOGO_SIZE)
        
        # Center the logo on the 64x32 display
        x_position = (64 - league_logo.width) // 2
        y_position = (32 - league_logo.height) // 2
        
        matrix.Clear()
        matrix.SetImage(league_logo.convert('RGB'), x_position, y_position)
        
    except Exception as e:
        print(f"Could not load league logo: {e}")


@lru_cache(maxsize=32)
def get_team_logo(league, team_abbr, flip=False):
    logo_path = f'{LOGOS_BASE_PATH}/{league}/{team_abbr}.png'
    
    if not os.path.exists(logo_path):
        logo_path = f'{LOGOS_BASE_PATH}/{league}/league_logo.png'
    
    # Load and resize
    logo = Image.open(logo_path)
    logo = logo.resize(LOGO_SIZE)
    
    if flip:
        logo = logo.transpose(Image.FLIP_LEFT_RIGHT)
    
    return logo

def get_team_goals(competitor, match_status):
    if match_status == "Scheduled":
        return '0'

    if 'score' in competitor:
        return competitor['score']

    if 'statistics' in competitor:
        for stat in competitor['statistics']:
            if stat.get('name') == 'goals':
                return stat['displayValue']

    return 'x'


def format_match_time(scheduled_time):
    dt = datetime.fromisoformat(scheduled_time.replace("Z", "+00:00"))
    local = dt.astimezone(ZoneInfo(LOCAL_TIMEZONE))

    match_time = local.strftime("%H:%M")
    match_date = local.strftime("%d/%m")
    
    return match_time, match_date


def start_background_updater(league, start_date):
    thread = threading.Thread(target=_background_data_updater, args=(league, start_date), daemon=True)
    thread.start()


def _background_data_updater(league, fixed_start_date):
    global _current_matches, _current_standings, _current_match_date
    
    print(f"Background Updater: Started. Fixed Start Date: {fixed_start_date}")
    
    # Track date that's currently used (locked)
    locked_date = None
    last_checked_day = datetime.now().date()
    
    while True:
        try:
            # Check for new day
            current_day = datetime.now().date()
            if current_day != last_checked_day:
                print(f"New day detected! Releasing date lock and searching from {current_day}...")
                last_checked_day = current_day
                locked_date = None  # Force re-search from today

            new_matches = None
            found_date = None

            # Decide where to start scanning from
            if fixed_start_date:
                scan_start_date = fixed_start_date
            else:
                scan_start_date = datetime.now()
            
            # Refresh data
            if locked_date:
                # Keep silent to avoid spam
                matches_on_day, date_on_day = fetch_matches(league, locked_date, max_days_ahead=1, silent=True)
                
                if matches_on_day:
                    print(f" -> Refreshing data for locked date: {locked_date.strftime('%d/%m')}")
                    new_matches = matches_on_day
                    found_date = date_on_day
                else:
                    print(f" -> Matches finished/gone on {locked_date.strftime('%d/%m')}. Releasing lock.")
                    locked_date = None

            # Go to next day if no scheduled matches
            if not new_matches:
                matches_found, date_found = fetch_matches(league, scan_start_date, MAX_DAYS_AHEAD, silent=False)
                
                if matches_found:
                    new_matches = matches_found
                    found_date = date_found
                    locked_date = found_date

            if new_matches:
                with _data_lock:
                    _current_matches = new_matches
                    _current_match_date = found_date
            
            # Update data
            new_standings = fetch_standings(league, silent=True)
            
            if new_standings:
                with _data_lock:
                    _current_standings = new_standings
            
        except Exception as e:
            print(f"Background Updater Error: {e}")
            
        time.sleep(5)


def get_latest_data():
    with _data_lock:
        return list(_current_matches), list(_current_standings)