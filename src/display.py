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
    
    # Render team logos
    matrix.SetImage(team_a_logo.convert('RGB'), -15, 0)
    matrix.SetImage(team_b_logo.convert('RGB'), 47, 0)


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