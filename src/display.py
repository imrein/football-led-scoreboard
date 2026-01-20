from rgbmatrix import RGBMatrix, graphics
from config import get_matrix_options, get_colors, load_fonts
from utils import get_team_logo, get_team_goals, format_match_time
from api import parse_match_data


# Global matrix and display objects (initialized once)
_matrix = None
_fonts = None
_colors = None


def setup_matrix():
    global _matrix, _fonts, _colors
    
    print("Initializing LED matrix...")
    
    if _matrix is None:
        print("  - Setting up matrix hardware...")
        options = get_matrix_options()
        _matrix = RGBMatrix(options=options)
        print("  -> Matrix hardware ready")
    
    if _fonts is None:
        print("  - Loading fonts...")
        _fonts = load_fonts()
        print("  -> Fonts loaded")
    
    if _colors is None:
        print("  - Initializing colors...")
        _colors = get_colors()
        print("  -> Colors ready")
    
    print("LED matrix initialization complete!\n")
    
    return _matrix


def clear_matrix(matrix):
    matrix.Clear()


def display_match(matrix, match, league):
    # Parse match data
    match_data = parse_match_data(match)
    competition = match_data['competition']
    match_status = match_data['status']
    team_a = match_data['team_a']
    team_b = match_data['team_b']
    
    # Get team goals
    team_a_goals = get_team_goals(match_data['team_a_competitor'], match_status)
    team_b_goals = get_team_goals(match_data['team_b_competitor'], match_status)
    score = f'{team_a_goals}-{team_b_goals}'
    
    # Load team logos
    team_a_logo = get_team_logo(league, team_a, flip=False)
    team_b_logo = get_team_logo(league, team_b, flip=True)
    
    # Clear the display
    matrix.Clear()
    
    # Display based on match status
    if match_status == 'Scheduled':
        display_scheduled(matrix, competition)
    elif match_status == 'HT':
        display_halftime(matrix, score)
    elif match_status == 'FT':
        display_fulltime(matrix, score)
    else:
        display_live(matrix, match_status, score)

    # Render red cards
    draw_red_cards(matrix, match_data['red_cards_a'], match_data['red_cards_b'])

    # Render team logos
    matrix.SetImage(team_a_logo.convert('RGB'), -15, 0)
    matrix.SetImage(team_b_logo.convert('RGB'), 47, 0)


def draw_red_cards(matrix, red_a, red_b):
    # Height of 3 pixels: Row 10 to 13 (Just above the score numbers)
    y_start = 10
    y_end = 13

    # Cap at 3 cards max to prevent drawing over logos
    count_a = min(red_a, 3)
    count_b = min(red_b, 3)

    # Team A
    # Start at x=24 and move LEFT for each extra card (-3 pixels per card)
    for i in range(count_a):
        start_x = 24 - (i * 3)
        for x in range(start_x, start_x + 2): # Width 2
            for y in range(y_start, y_end):
                matrix.SetPixel(x, y, 255, 0, 0)

    # Team B
    # Start at x=39 and move RIGHT for each extra card (+3 pixels per card)
    for i in range(count_b):
        start_x = 39 + (i * 3)
        for x in range(start_x, start_x + 2): # Width 2
            for y in range(y_start, y_end):
                matrix.SetPixel(x, y, 255, 0, 0)


def display_standings(matrix, standings):
    font_5x7 = _fonts[0]
    color_white = _colors[0]
    color_red = _colors[1]
    
    # Clear the display
    matrix.Clear()
    
    # Only show the top 4 teams to fit the screen
    top_teams = standings[:4]
    
    # Layout configuration
    start_y = 7
    line_height = 8
    
    # Column positions
    x_rank = 2
    x_team = 18
    x_points = 50
    
    for i, team in enumerate(top_teams):
        y_pos = start_y + (i * line_height)
        
        # Draw Rank (e.g. "1.")
        graphics.DrawText(matrix, font_5x7, x_rank, y_pos, color_red, f"{team['rank']}.")
        
        # Draw Team (e.g. "BAY")
        graphics.DrawText(matrix, font_5x7, x_team, y_pos, color_white, team['team'])
        
        # Draw Points (e.g. "45")
        points_str = str(team['points'])
        
        # Simple alignment for points
        x_adj = 0 if len(points_str) > 1 else 4
        graphics.DrawText(matrix, font_5x7, x_points + x_adj, y_pos, color_white, points_str)


def display_scheduled(matrix, competition):
    font_5x7, font_6x10 = _fonts
    color_white, color_red = _colors
    
    scheduled_time = competition["date"]
    match_time, match_date = format_match_time(scheduled_time)
    
    graphics.DrawText(matrix, font_5x7, 20, 7, color_white, match_time)
    graphics.DrawText(matrix, font_6x10, 27, 20, color_red, 'VS')
    graphics.DrawText(matrix, font_5x7, 20, 31, color_white, match_date)


def display_halftime(matrix, score):
    font_5x7, font_6x10 = _fonts
    color_white, color_red = _colors
    
    graphics.DrawText(matrix, font_6x10, 27, 8, color_red, 'HT')
    graphics.DrawText(matrix, font_6x10, 24, 22, color_white, score)


def display_fulltime(matrix, score):
    font_5x7, font_6x10 = _fonts
    color_white, color_red = _colors
    
    graphics.DrawText(matrix, font_6x10, 27, 8, color_red, 'FT')
    graphics.DrawText(matrix, font_6x10, 24, 22, color_white, score)


def display_live(matrix, match_status, score):
    font_5x7, font_6x10 = _fonts
    color_white, color_red = _colors
    
    # Position status text based on length
    if len(match_status) > 3:
        x_pos = 18
    else:
        x_pos = 27
    
    graphics.DrawText(matrix, font_6x10, x_pos, 8, color_white, match_status)
    graphics.DrawText(matrix, font_6x10, 24, 22, color_white, score)