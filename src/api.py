import requests
from datetime import datetime, timedelta
from config import API_BASE_URL, API_TIMEOUT


def fetch_matches(league, start_date, max_days_ahead=1, silent=False):
    today = datetime.now()
    current_year = today.strftime("%Y")
    
    for days_offset in range(max_days_ahead):
        check_date = start_date + timedelta(days=days_offset)
        formatted_check_date = check_date.strftime("%m%d")
        
        # Build API URL
        api_url = f'{API_BASE_URL}/{league}.1/scoreboard?dates={current_year}{formatted_check_date}'
        
        if not silent:
            print(f"Checking for matches on {formatted_check_date}...")

        try:
            scoreboard_data = requests.get(api_url, timeout=API_TIMEOUT)
            scoreboard_data.raise_for_status()  # Raise error for bad status codes
            matches = scoreboard_data.json().get('events')
            
            if matches:
                if not silent:
                    print(f"Found {len(matches)} match(es) on {formatted_check_date}")
                return matches, check_date
            else:
                if not silent:
                    print(f"No matches on {formatted_check_date}, checking next day...")
        
        except requests.Timeout:
            print(f"Timeout on {formatted_check_date}, skipping...")
        
        except requests.RequestException as e:
            print(f"API error on {formatted_check_date}: {e}, skipping...")
        
        except ValueError:
            print(f"Invalid JSON response on {formatted_check_date}, skipping...")
    
    # No matches found within search window
    if not silent:
        print(f"No matches found in {league} within the next {max_days_ahead} days")
    return None, None


def parse_match_data(match):
    competition = match['competitions'][0]
    teams = competition['competitors']

    team_a = teams[0]
    team_b = teams[1]

    red_cards_a = 0
    red_cards_b = 0

    events = competition.get('details', [])
    
    for event in events:
        # Check if this event is a Red Card
        if event.get('redCard', False):
            event_team_id = event.get('team', {}).get('id')
            
            if event_team_id == team_a['id']:
                red_cards_a += 1
            elif event_team_id == team_b['id']:
                red_cards_b += 1

    return {
        'competition': competition,
        'teams': teams,
        'status': competition['status']['type']['shortDetail'],
        'team_a': teams[0]['team']['abbreviation'],
        'team_b': teams[1]['team']['abbreviation'],
        'team_a_competitor': teams[0],
        'team_b_competitor': teams[1],
        'red_cards_a': red_cards_a,
        'red_cards_b': red_cards_b,
    }


def fetch_standings(league, silent=False):
    # Construct the URL (similar to scoreboard, but for standings)
    api_url = f'https://site.web.api.espn.com/apis/v2/sports/soccer/{league}.1/standings'
    
    if not silent:
        print(f"Fetching standings for {league}...")

    try:
        standings_data = requests.get(api_url, timeout=API_TIMEOUT)
        standings_data.raise_for_status()
        data = standings_data.json()
        
        entries = data['children'][0]['standings']['entries']
        
        standings = []
        for entry in entries:
            team_abbr = entry['team']['abbreviation']
            
            # Find points in the stats list safely
            points = 0
            for stat in entry['stats']:
                if stat['name'] == 'points':
                    points = stat['value']
                    break
            
            standings.append({
                'rank': len(standings) + 1,
                'team': team_abbr,
                'points': int(points)
            })
            
        return standings

    except Exception as e:
        if not silent:
            print(f"Error fetching standings: {e}")
        return None