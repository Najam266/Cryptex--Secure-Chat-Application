"""
Client module for Cryptex secure chat application.
Handles connection to server and encrypted message exchange.
"""

import socket
import threading
import json
import config
from crypto_handler import CryptoHandler
from utils import get_timestamp


class ChatClient:
    """Client for secure encrypted chat communication."""
    
    def __init__(self, username, host='localhost', port=config.DEFAULT_PORT):
        """Initialize chat client."""
        self.username = username
        self.host = host
        self.port = port
        self.socket = None
        self.crypto = CryptoHandler()
        self.connected = False
        self.running = False
        
        # Callbacks for GUI
        self.on_message_received = None
        self.on_user_list_update = None
        self.on_connection_status = None
        self.on_error = None
        
        # Shared AES session key for all clients (hardcoded for simplicity in LAN)
        # In production, this would be negotiated via RSA-encrypted key exchange
        self.session_key = b'CryptexSecureKey2024LocalLAN'  # 28 bytes, padded to 32
        self.session_key = self.session_key.ljust(32, b'\0')  # Pad to 32 bytes for AES-256
        
    def connect(self):
        """Connect to the chat server and authenticate."""
        try:
            # Generate RSA keys
            print(f"[{get_timestamp()}] Generating encryption keys...")
            self.crypto.generate_rsa_keys()
            
            # Connect to server
            print(f"[{get_timestamp()}] Connecting to {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Send authentication (username + public key)
            public_key_pem = self.crypto.export_public_key()
            auth_message = f"{config.MSG_TYPE_AUTH}{config.MSG_SEPARATOR}{self.username}{config.MSG_SEPARATOR}{public_key_pem}"
            self.socket.send(auth_message.encode('utf-8'))
            
            # Wait for authentication response
            response = self.socket.recv(config.BUFFER_SIZE).decode('utf-8')
            # Extract just the response part (before delimiter if present)
            response = response.split(config.MSG_DELIMITER)[0].strip()
            
            if response == "SUCCESS":
                self.connected = True
                self.running = True
                print(f"[{get_timestamp()}] ✓ Connected and authenticated!")
                
                if self.on_connection_status:
                    self.on_connection_status(True, "Connected")
                
                # Start receive thread
                receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
                receive_thread.start()
                
                return True
            else:
                print(f"[{get_timestamp()}] ✗ Authentication failed: {response}")
                if self.on_error:
                    self.on_error(response)
                self.socket.close()
                return False
                
        except Exception as e:
            error_msg = f"Connection failed: {e}"
            print(f"[ERROR] {error_msg}")
            if self.on_error:
                self.on_error(error_msg)
            if self.on_connection_status:
                self.on_connection_status(False, error_msg)
            return False
    
    def receive_messages(self):
        """Receive and process messages from server."""
        buffer = ""  # Buffer for partial messages
        
        while self.running and self.connected:
            try:
                data = self.socket.recv(config.BUFFER_SIZE).decode('utf-8')
                
                if not data:
                    break
                
                # Add to buffer
                buffer += data
                
                # Process complete messages (separated by MSG_DELIMITER)
                while config.MSG_DELIMITER in buffer:
                    message, buffer = buffer.split(config.MSG_DELIMITER, 1)
                    if message.strip():  # Check if non-empty
                        self.process_message(message)  # Pass original, don't strip
                
            except Exception as e:
                if self.running:
                    print(f"[ERROR] Receive error: {e}")
                break
        
        # Disconnected
        self.connected = False
        if self.on_connection_status:
            self.on_connection_status(False, "Disconnected")
        print(f"[{get_timestamp()}] Disconnected from server")
    
    def process_message(self, data):
        """Process received message based on type."""
        try:
            parts = data.split(config.MSG_SEPARATOR, 2)
            
            if len(parts) < 2:
                return
            
            msg_type = parts[0]
            
            if msg_type == config.MSG_TYPE_USER_LIST:
                # Updated user list
                user_list_json = parts[1]
                user_list = json.loads(user_list_json)
                if self.on_user_list_update:
                    self.on_user_list_update(user_list)
                print(f"[{get_timestamp()}] Online users: {', '.join(user_list)}")
                
            elif msg_type == config.MSG_TYPE_KEY_EXCHANGE:
                # Public key from another user
                if len(parts) >= 3:
                    username = parts[1]
                    public_key = parts[2]
                    print(f"[DEBUG] Importing key for {username}, key length: {len(public_key)}, starts with: {public_key[:50] if len(public_key) > 50 else public_key}")
                    self.crypto.import_peer_public_key(username, public_key)
                    
            elif msg_type == config.MSG_TYPE_MESSAGE:
                # Direct encrypted message
                if len(parts) >= 3:
                    sender = parts[1]
                    encrypted_content = parts[2]
                    self.handle_encrypted_message(sender, encrypted_content)
                    
            elif msg_type == config.MSG_TYPE_BROADCAST:
                # Broadcast encrypted message
                if len(parts) >= 3:
                    sender = parts[1]
                    encrypted_content = parts[2]
                    self.handle_encrypted_message(sender, encrypted_content)
                    
        except Exception as e:
            print(f"[ERROR] Processing message: {e}")
    
    def handle_encrypted_message(self, sender, encrypted_data):
        """Decrypt and handle received encrypted message."""
        try:
            # For simplicity, we'll use the session key for all messages
            # In production, you'd negotiate separate keys per conversation
            decrypted_message = self.crypto.decrypt_message(encrypted_data, self.session_key)
            
            if decrypted_message:
                print(f"[{get_timestamp()}] {sender}: {decrypted_message}")
                if self.on_message_received:
                    self.on_message_received(sender, decrypted_message)
            else:
                print(f"[ERROR] Failed to decrypt message from {sender}")
                
        except Exception as e:
            print(f"[ERROR] Handling encrypted message: {e}")
    
    def send_message(self, recipient, message):
        """
        Send encrypted message to specific recipient.
        For broadcast, use recipient='ALL'
        """
        try:
            if not self.connected:
                print("[ERROR] Not connected to server")
                return False
            
            # Encrypt message with session key
            encrypted_message = self.crypto.encrypt_message(message, self.session_key)
            
            if not encrypted_message:
                print("[ERROR] Encryption failed")
                return False
            
            # Format and send
            if recipient == 'ALL':
                # Broadcast
                data = f"{config.MSG_TYPE_BROADCAST}{config.MSG_SEPARATOR}{encrypted_message}"
            else:
                # Direct message
                data = f"{config.MSG_TYPE_MESSAGE}{config.MSG_SEPARATOR}{recipient}{config.MSG_SEPARATOR}{encrypted_message}"
            
            self.socket.send(data.encode('utf-8'))
            return True
            
        except Exception as e:
            print(f"[ERROR] Sending message: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server."""
        print(f"[{get_timestamp()}] Disconnecting...")
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print(f"[{get_timestamp()}] Disconnected")


def main():
    """Test client in console mode."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python client.py <username> [host] [port]")
        sys.exit(1)
    
    username = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
    port = int(sys.argv[3]) if len(sys.argv) > 3 else config.DEFAULT_PORT
    
    # Create client
    client = ChatClient(username, host, port)
    
    # Set up callbacks
    def on_message(sender, message):
        print(f"\n{sender}: {message}")
        print(f"{username}> ", end='', flush=True)
    
    def on_users(users):
        print(f"\n[Online: {', '.join(users)}]")
        print(f"{username}> ", end='', flush=True)
    
    client.on_message_received = on_message
    client.on_user_list_update = on_users
    
    # Connect
    if not client.connect():
        print("Failed to connect")
        sys.exit(1)
    
    # Interactive message loop
    print("\nConnected! Type messages and press Enter to send.")
    print("Type 'quit' to exit.\n")
    
    try:
        while client.connected:
            message = input(f"{username}> ")
            
            if message.lower() == 'quit':
                break
            
            if message.strip():
                client.send_message('ALL', message)
                
    except KeyboardInterrupt:
        print("\n")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
