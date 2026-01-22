"""
Server module for Cryptex secure chat application.
Handles client connections, user authentication, and message routing.
Includes comprehensive security audit logging.
"""

import socket
import threading
import json
import config
from utils import get_timestamp
from security_logger import SecurityLogger


class ChatServer:
    """Central server coordinating secure chat communication."""
    
    def __init__(self, host=config.DEFAULT_HOST, port=config.DEFAULT_PORT):
        """Initialize the chat server."""
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {username: socket}
        self.client_addresses = {}  # {username: address}
        self.public_keys = {}  # {username: public_key_pem}
        self.lock = threading.Lock()
        self.running = False
        
        # Initialize security audit logger
        self.security_log = SecurityLogger()
        
    def start(self):
        """Start the server and listen for connections."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(config.MAX_CONNECTIONS)
            self.running = True
            
            print(f"\n{'='*60}")
            print(f"🔒 CRYPTEX SERVER STARTED")
            print(f"{'='*60}")
            print(f"Host: {self.host}")
            print(f"Port: {self.port}")
            print(f"Max Connections: {config.MAX_CONNECTIONS}")
            print(f"Waiting for clients to connect...")
            print(f"{'='*60}\n")
            
            # Accept clients in main thread
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"[{get_timestamp()}] New connection from {address}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        print(f"[ERROR] Accept failed: {e}")
                        
        except Exception as e:
            print(f"[ERROR] Server start failed: {e}")
        finally:
            self.shutdown()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connection."""
        username = None
        
        try:
            # Receive authentication data (username + public key)
            auth_data = client_socket.recv(config.BUFFER_SIZE).decode('utf-8')
            
            if not auth_data:
                client_socket.close()
                return
            
            # Parse authentication: AUTH||username||public_key
            parts = auth_data.split(config.MSG_SEPARATOR, 2)
            
            if len(parts) != 3 or parts[0] != config.MSG_TYPE_AUTH:
                # Log authentication failure
                self.security_log.log_auth_failure('UNKNOWN', address[0], 'Invalid authentication format')
                client_socket.send(f"ERROR: Invalid authentication{config.MSG_DELIMITER}".encode('utf-8'))
                client_socket.close()
                return
            
            username = parts[1]
            public_key_pem = parts[2]
            
            # Check if username already exists
            with self.lock:
                if username in self.clients:
                    # Log duplicate username attempt
                    self.security_log.log_auth_failure(username, address[0], 'Username already taken')
                    client_socket.send(f"ERROR: Username '{username}' already taken{config.MSG_DELIMITER}".encode('utf-8'))
                    client_socket.close()
                    return
                
                # Register client
                self.clients[username] = client_socket
                self.client_addresses[username] = address
                self.public_keys[username] = public_key_pem
            
            # Send success response
            client_socket.send(f"SUCCESS{config.MSG_DELIMITER}".encode('utf-8'))
            
            print(f"[{get_timestamp()}] ✓ User '{username}' authenticated from {address}")
            
            # Log successful authentication
            self.security_log.log_auth_success(username, address[0])
            
            # Broadcast updated user list to all clients
            self.broadcast_user_list()
            
            # Send all public keys to new client
            self.send_all_public_keys(username)
            
            # Broadcast new user's public key to all existing clients
            self.broadcast_public_key(username, public_key_pem)
            
            # Listen for messages from this client
            while self.running:
                try:
                    message_data = client_socket.recv(config.BUFFER_SIZE).decode('utf-8')
                    
                    if not message_data:
                        break
                    
                    # Parse message: MESSAGE||recipient||encrypted_content
                    # or BROADCAST||encrypted_content
                    self.route_message(username, message_data)
                    
                except Exception as e:
                    print(f"[ERROR] Receiving from {username}: {e}")
                    break
                    
        except Exception as e:
            print(f"[ERROR] Client handler error: {e}")
        finally:
            # Client disconnected
            if username:
                with self.lock:
                    if username in self.clients:
                        del self.clients[username]
                    if username in self.client_addresses:
                        del self.client_addresses[username]
                    if username in self.public_keys:
                        del self.public_keys[username]
                
                print(f"[{get_timestamp()}] ✗ User '{username}' disconnected")
                self.broadcast_user_list()
                
            try:
                client_socket.close()
            except:
                pass
    
    def route_message(self, sender, message_data):
        """Route message to appropriate recipient(s)."""
        try:
            parts = message_data.split(config.MSG_SEPARATOR, 2)
            
            if len(parts) < 2:
                return
            
            msg_type = parts[0]
            
            if msg_type == config.MSG_TYPE_BROADCAST:
                # Broadcast to all users except sender
                encrypted_content = parts[1]
                self.broadcast_message(sender, encrypted_content)
                
            elif msg_type == config.MSG_TYPE_MESSAGE:
                # Direct message
                if len(parts) < 3:
                    return
                recipient = parts[1]
                encrypted_content = parts[2]
                self.send_direct_message(sender, recipient, encrypted_content)
                
        except Exception as e:
            print(f"[ERROR] Routing message: {e}")
    
    def send_direct_message(self, sender, recipient, encrypted_content):
        """Send encrypted message to specific recipient."""
        with self.lock:
            if recipient in self.clients:
                try:
                    message = f"{config.MSG_TYPE_MESSAGE}{config.MSG_SEPARATOR}{sender}{config.MSG_SEPARATOR}{encrypted_content}{config.MSG_DELIMITER}"
                    self.clients[recipient].send(message.encode('utf-8'))
                    print(f"[{get_timestamp()}] {sender} → {recipient} (encrypted)")
                    # Log message transmission
                    self.security_log.log_message_sent(sender, recipient, is_broadcast=False)
                except Exception as e:
                    print(f"[ERROR] Sending to {recipient}: {e}")
    
    def broadcast_message(self, sender, encrypted_content):
        """Broadcast encrypted message to all connected clients except sender."""
        with self.lock:
            disconnected = []
            for username, client_socket in self.clients.items():
                if username != sender:
                    try:
                        message = f"{config.MSG_TYPE_BROADCAST}{config.MSG_SEPARATOR}{sender}{config.MSG_SEPARATOR}{encrypted_content}{config.MSG_DELIMITER}"
                        client_socket.send(message.encode('utf-8'))
                    except Exception as e:
                        print(f"[ERROR] Broadcasting to {username}: {e}")
                        disconnected.append(username)
            
            # Remove disconnected clients
            for username in disconnected:
                if username in self.clients:
                    del self.clients[username]
        
        print(f"[{get_timestamp()}] {sender} → ALL (broadcast, encrypted)")
        # Log broadcast message
        self.security_log.log_message_sent(sender, 'ALL', is_broadcast=True)
    
    def broadcast_user_list(self):
        """Send updated user list to all connected clients."""
        with self.lock:
            user_list = list(self.clients.keys())
            user_list_json = json.dumps(user_list)
            message = f"{config.MSG_TYPE_USER_LIST}{config.MSG_SEPARATOR}{user_list_json}{config.MSG_DELIMITER}"
            
            disconnected = []
            for username, client_socket in self.clients.items():
                try:
                    client_socket.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"[ERROR] Sending user list to {username}: {e}")
                    disconnected.append(username)
            
            # Clean up disconnected
            for username in disconnected:
                if username in self.clients:
                    del self.clients[username]
    
    def send_all_public_keys(self, username):
        """Send all existing users' public keys to newly connected client."""
        with self.lock:
            if username not in self.clients:
                return
            
            client_socket = self.clients[username]
            
            for other_user, public_key in self.public_keys.items():
                if other_user != username:
                    try:
                        message = f"{config.MSG_TYPE_KEY_EXCHANGE}{config.MSG_SEPARATOR}{other_user}{config.MSG_SEPARATOR}{public_key}{config.MSG_DELIMITER}"
                        client_socket.send(message.encode('utf-8'))
                        # Log key exchange
                        self.security_log.log_key_exchange(other_user, username)
                    except Exception as e:
                        print(f"[ERROR] Sending public key to {username}: {e}")
    
    def broadcast_public_key(self, username, public_key):
        """Broadcast a user's public key to all other connected clients."""
        with self.lock:
            message = f"{config.MSG_TYPE_KEY_EXCHANGE}{config.MSG_SEPARATOR}{username}{config.MSG_SEPARATOR}{public_key}{config.MSG_DELIMITER}"
            
            for other_user, client_socket in self.clients.items():
                if other_user != username:
                    try:
                        client_socket.send(message.encode('utf-8'))
                    except Exception as e:
                        print(f"[ERROR] Broadcasting public key to {other_user}: {e}")
    
    def shutdown(self):
        """Shutdown the server gracefully."""
        print("\n[SERVER] Shutting down...")
        self.running = False
        
        with self.lock:
            # Close all client connections
            for username, client_socket in list(self.clients.items()):
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("[SERVER] Shutdown complete")


def main():
    """Main entry point for server."""
    import sys
    
    host = config.DEFAULT_HOST
    port = config.DEFAULT_PORT
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    server = ChatServer(host, port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n[SERVER] Interrupted by user")
        server.shutdown()


if __name__ == "__main__":
    main()
