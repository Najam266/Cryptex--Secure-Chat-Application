"""
Configuration constants for Cryptex secure chat application.
"""

# Message Delimiter (unique string to separate messages in TCP stream)
MSG_DELIMITER = "\n###MSG###\n"

# Server Configuration
DEFAULT_HOST = '0.0.0.0'  # Listen on all network interfaces
DEFAULT_PORT = 5555
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 10
CONNECTION_TIMEOUT = 300  # seconds

# Encryption Configuration
RSA_KEY_SIZE = 2048  # bits
AES_KEY_SIZE = 32    # 256 bits (32 bytes)
AES_IV_SIZE = 16     # 128 bits (16 bytes)

# Message Protocol
MSG_SEPARATOR = "||"
MSG_TYPE_AUTH = "AUTH"
MSG_TYPE_KEY_EXCHANGE = "KEY_EXCHANGE"
MSG_TYPE_MESSAGE = "MESSAGE"
MSG_TYPE_BROADCAST = "BROADCAST"
MSG_TYPE_USER_LIST = "USER_LIST"
MSG_TYPE_DISCONNECT = "DISCONNECT"

# GUI Configuration - WhatsApp Dark Mode
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# WhatsApp Dark Mode Color Scheme
WHATSAPP_TEAL = "#075E54"        # Header/accent color
WHATSAPP_TEAL_DARK = "#054e45"   # Darker teal for hover
WHATSAPP_DARK_BG = "#0B141A"     # App background (very dark)
WHATSAPP_CHAT_BG = "#0B141A"     # Chat background
WHATSAPP_SIDEBAR = "#111B21"     # Sidebar background (dark gray)
WHATSAPP_SENT_BUBBLE = "#005C4B" # Sent message bubble (dark green)
WHATSAPP_RECEIVED_BUBBLE = "#202C33" # Received message bubble (dark gray)
WHATSAPP_INPUT_BG = "#202C33"    # Input field background
WHATSAPP_BORDER = "#2A3942"      # Border color
WHATSAPP_HEADER = "#202C33"      # Header background

# Semantic color mapping
MAIN_BG_COLOR = WHATSAPP_CHAT_BG
SIDEBAR_BG_COLOR = WHATSAPP_SIDEBAR
MESSAGE_AREA_BG = WHATSAPP_CHAT_BG
INPUT_BG_COLOR = WHATSAPP_INPUT_BG
TEXT_COLOR = "#E9EDEF"           # Light gray/white for text
SENT_MSG_COLOR = "#E9EDEF"       # Light text for sent messages
RECEIVED_MSG_COLOR = "#E9EDEF"   # Light text for received messages
BUTTON_COLOR = "#00A884"         # WhatsApp green for buttons
BUTTON_HOVER_COLOR = "#06CF9C"   # Lighter green for hover
ACCENT_COLOR = "#00A884"         # WhatsApp signature green
BUBBLE_SENT_BG = WHATSAPP_SENT_BUBBLE
BUBBLE_RECEIVED_BG = WHATSAPP_RECEIVED_BUBBLE
TIMESTAMP_COLOR = "#8696A0"      # Gray for timestamps
SYSTEM_MSG_BG = "#182229"        # System message background
SYSTEM_MSG_TEXT = "#8696A0"      # System message text

# Fonts
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 13
FONT_SIZE_SMALL = 11
FONT_SIZE_LARGE = 16
