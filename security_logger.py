"""
Security audit logging module for Cryptex.
Provides comprehensive logging for authentication, key exchanges, and suspicious activities.
"""

import logging
import os
from datetime import datetime


class SecurityLogger:
    """Handles security audit logging for compliance and forensic analysis."""
    
    def __init__(self, log_file='security_audit.log'):
        """
        Initialize security logger.
        
        Args:
            log_file: Path to audit log file
        """
        self.log_file = log_file
        self.logger = logging.getLogger('CryptexSecurity')
        
        # Prevent duplicate handlers if logger already configured
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Log initialization
        self.logger.info("="*60)
        self.logger.info("CRYPTEX SECURITY AUDIT LOG INITIALIZED")
        self.logger.info("="*60)
    
    def log_auth_success(self, username, ip):
        """Log successful authentication."""
        self.logger.info(f"AUTH_SUCCESS | User: {username} | IP: {ip}")
    
    def log_auth_failure(self, username, ip, reason):
        """Log failed authentication attempt."""
        self.logger.warning(f"AUTH_FAILED | User: {username} | IP: {ip} | Reason: {reason}")
    
    def log_key_exchange(self, user1, user2):
        """Log public key exchange between users."""
        self.logger.info(f"KEY_EXCHANGE | {user1} <-> {user2}")
    
    def log_message_sent(self, sender, recipient, is_broadcast=False):
        """Log message transmission."""
        if is_broadcast:
            self.logger.info(f"MESSAGE_SENT | From: {sender} | To: ALL (broadcast) | Encrypted: Yes")
        else:
            self.logger.info(f"MESSAGE_SENT | From: {sender} | To: {recipient} | Encrypted: Yes")
    
    def log_suspicious_activity(self, username, activity):
        """Log suspicious or abnormal activity."""
        self.logger.critical(f"SUSPICIOUS_ACTIVITY | User: {username} | Activity: {activity}")
    
    def log_connection(self, username, ip, action="CONNECTED"):
        """Log client connection/disconnection."""
        self.logger.info(f"{action} | User: {username} | IP: {ip}")
    
    def log_server_event(self, event):
        """Log general server events."""
        self.logger.info(f"SERVER_EVENT | {event}")
    
    def log_error(self, context, error_msg):
        """Log errors and exceptions."""
        self.logger.error(f"ERROR | Context: {context} | Message: {error_msg}")


# Convenience function for quick logging setup
def get_logger(log_file='security_audit.log'):
    """Get or create security logger instance."""
    return SecurityLogger(log_file)
