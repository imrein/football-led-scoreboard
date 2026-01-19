from rgbmatrix import RGBMatrixOptions, graphics

# Matrix config
MATRIX_ROWS = 32
MATRIX_COLS = 64
MATRIX_CHAIN_LENGTH = 1
MATRIX_PARALLEL = 1
MATRIX_HARDWARE_MAPPING = 'adafruit-hat-pwm'
MATRIX_GPIO_SLOWDOWN = 2
MATRIX_BRIGHTNESS = 70
MATRIX_REFRESH_RATE = 60

# Display config
LOGO_SIZE = (32, 32)
DISPLAY_MATCH_DURATION = 10  # seconds
DISPLAY_STANDINGS_DURATION = 10  # seconds

# Paths
LOGOS_BASE_PATH = "assets/logos"

# Fonts
FONT_5X7_PATH = "assets/fonts/5x7.bdf"
FONT_6X10_PATH = "assets/fonts/6x10.bdf"

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)

# API settings
API_BASE_URL = 'https://site.api.espn.com/apis/site/v2/sports/soccer'
API_TIMEOUT = 15  # seconds
MAX_DAYS_AHEAD = 5   # days to search for matches

# Timezone
LOCAL_TIMEZONE = "Europe/Brussels"


def get_matrix_options():
    options = RGBMatrixOptions()
    options.rows = MATRIX_ROWS
    options.cols = MATRIX_COLS
    options.chain_length = MATRIX_CHAIN_LENGTH
    options.parallel = MATRIX_PARALLEL
    options.hardware_mapping = MATRIX_HARDWARE_MAPPING
    options.gpio_slowdown = MATRIX_GPIO_SLOWDOWN
    options.brightness = MATRIX_BRIGHTNESS
    options.limit_refresh_rate_hz = MATRIX_REFRESH_RATE

    return options


def get_colors():
    color_white = graphics.Color(*COLOR_WHITE)
    color_red = graphics.Color(*COLOR_RED)

    return color_white, color_red


def load_fonts():
    font_5x7 = graphics.Font()
    font_5x7.LoadFont(FONT_5X7_PATH)
    
    font_6x10 = graphics.Font()
    font_6x10.LoadFont(FONT_6X10_PATH)
    
    return font_5x7, font_6x10