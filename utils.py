"""
Utility functions for Cryptex application.
"""

from datetime import datetime
import re


def get_timestamp():
    """Generate current timestamp in readable format."""
    return datetime.now().strftime("%H:%M:%S")


def format_message(username, message, timestamp=None):
    """Format a message for display."""
    if timestamp is None:
        timestamp = get_timestamp()
    return f"[{timestamp}] {username}: {message}"


def validate_username(username):
    """
    Validate username format.
    Rules: 3-20 characters, alphanumeric and underscores only.
    """
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 20:
        return False, "Username must not exceed 20 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, "Valid username"


def validate_ip(ip):
    """Validate IP address format."""
    if ip == "localhost":
        return True, "Valid"
    
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False, "Invalid IP format"
    
    parts = ip.split('.')
    for part in parts:
        if int(part) > 255:
            return False, "IP octets must be 0-255"
    
    return True, "Valid IP"


def validate_port(port):
    """Validate port number."""
    try:
        port_num = int(port)
        if 1024 <= port_num <= 65535:
            return True, "Valid port"
        else:
            return False, "Port must be between 1024 and 65535"
    except ValueError:
        return False, "Port must be a number"


def truncate_text(text, max_length=50):
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def parse_message_data(data_str):
    """Parse message data string into components."""
    try:
        parts = data_str.split("||", 2)
        if len(parts) >= 2:
            return parts
        return None
    except Exception:
        return None
