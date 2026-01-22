"""
Cryptography handler for Cryptex application.
Implements hybrid encryption using RSA (key exchange) and AES (message encryption).
Includes HMAC for message authentication and integrity.
"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import hmac
import hashlib
import config


class CryptoHandler:
    """Handles all cryptographic operations for secure communication."""
    
    def __init__(self):
        """Initialize crypto handler with RSA key pair."""
        self.rsa_key = None
        self.public_key = None
        self.private_key = None
        self.peer_public_keys = {}  # Store public keys of other users
        
    def generate_rsa_keys(self):
        """Generate RSA key pair for asymmetric encryption."""
        self.rsa_key = RSA.generate(config.RSA_KEY_SIZE)
        self.public_key = self.rsa_key.publickey()
        self.private_key = self.rsa_key
        print(f"[CRYPTO] RSA key pair generated ({config.RSA_KEY_SIZE} bits)")
        
    def export_public_key(self):
        """Export public key in PEM format for sharing."""
        if self.public_key:
            return self.public_key.export_key().decode('utf-8')
        return None
    
    def import_peer_public_key(self, username, public_key_pem):
        """Import and store a peer's public key."""
        try:
            peer_key = RSA.import_key(public_key_pem.encode('utf-8'))
            self.peer_public_keys[username] = peer_key
            print(f"[CRYPTO] Imported public key for user: {username}")
            return True
        except Exception as e:
            print(f"[CRYPTO ERROR] Failed to import public key: {e}")
            return False
    
    def generate_aes_key(self):
        """Generate random AES session key."""
        return get_random_bytes(config.AES_KEY_SIZE)
    
    def generate_aes_iv(self):
        """Generate random AES initialization vector."""
        return get_random_bytes(config.AES_IV_SIZE)
    
    def encrypt_aes_key_with_rsa(self, aes_key, recipient_username):
        """
        Encrypt AES key with recipient's RSA public key.
        This allows secure key exchange.
        """
        try:
            if recipient_username not in self.peer_public_keys:
                raise ValueError(f"No public key found for {recipient_username}")
            
            peer_public_key = self.peer_public_keys[recipient_username]
            cipher_rsa = PKCS1_OAEP.new(peer_public_key)
            encrypted_key = cipher_rsa.encrypt(aes_key)
            return base64.b64encode(encrypted_key).decode('utf-8')
        except Exception as e:
            print(f"[CRYPTO ERROR] RSA encryption failed: {e}")
            return None
    
    def decrypt_aes_key_with_rsa(self, encrypted_key_b64):
        """
        Decrypt AES key using own RSA private key.
        """
        try:
            encrypted_key = base64.b64decode(encrypted_key_b64.encode('utf-8'))
            cipher_rsa = PKCS1_OAEP.new(self.private_key)
            aes_key = cipher_rsa.decrypt(encrypted_key)
            return aes_key
        except Exception as e:
            print(f"[CRYPTO ERROR] RSA decryption failed: {e}")
            return None
    
    def encrypt_message(self, message, aes_key):
        """
        Encrypt message using AES-256 in CBC mode.
        Returns: base64 encoded string of (IV + ciphertext)
        """
        try:
            # Generate random IV for this message
            iv = self.generate_aes_iv()
            
            # Pad message to be multiple of 16 bytes
            message_bytes = message.encode('utf-8')
            padding_length = AES.block_size - (len(message_bytes) % AES.block_size)
            padded_message = message_bytes + (bytes([padding_length]) * padding_length)
            
            # Encrypt with AES
            cipher = AES.new(aes_key, AES.MODE_CBC, iv)
            ciphertext = cipher.encrypt(padded_message)
            
            # Combine IV and ciphertext, then encode
            encrypted_data = iv + ciphertext
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            print(f"[CRYPTO ERROR] AES encryption failed: {e}")
            return None
    
    def decrypt_message(self, encrypted_message_b64, aes_key):
        """
        Decrypt AES encrypted message.
        """
        try:
            # Decode base64
            encrypted_data = base64.b64decode(encrypted_message_b64.encode('utf-8'))
            
            # Extract IV and ciphertext
            iv = encrypted_data[:config.AES_IV_SIZE]
            ciphertext = encrypted_data[config.AES_IV_SIZE:]
            
            # Decrypt
            cipher = AES.new(aes_key, AES.MODE_CBC, iv)
            padded_message = cipher.decrypt(ciphertext)
            
            # Remove padding
            padding_length = padded_message[-1]
            message = padded_message[:-padding_length]
            
            return message.decode('utf-8')
        except Exception as e:
            print(f"[CRYPTO ERROR] AES decryption failed: {e}")
            return None
    
    def sign_message(self, message):
        """
        Create digital signature for message integrity verification.
        """
        try:
            message_hash = SHA256.new(message.encode('utf-8'))
            signature = pkcs1_15.new(self.private_key).sign(message_hash)
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            print(f"[CRYPTO ERROR] Signing failed: {e}")
            return None
    
    def verify_signature(self, message, signature_b64, sender_username):
        """
        Verify digital signature to ensure message integrity.
        """
        try:
            if sender_username not in self.peer_public_keys:
                print(f"[CRYPTO WARN] No public key for {sender_username}")
                return False
            
            signature = base64.b64decode(signature_b64.encode('utf-8'))
            message_hash = SHA256.new(message.encode('utf-8'))
            peer_public_key = self.peer_public_keys[sender_username]
            
            pkcs1_15.new(peer_public_key).verify(message_hash, signature)
            return True
        except Exception as e:
            print(f"[CRYPTO ERROR] Signature verification failed: {e}")
            return False
    
    def create_hmac(self, message, key):
        """
        Create HMAC-SHA256 for message authentication.
        
        Args:
            message: Message string to authenticate
            key: Secret key (AES key) for HMAC
        
        Returns:
            Hex string of HMAC digest
        """
        try:
            message_bytes = message.encode('utf-8') if isinstance(message, str) else message
            hmac_obj = hmac.new(key, message_bytes, hashlib.sha256)
            return hmac_obj.hexdigest()
        except Exception as e:
            print(f"[CRYPTO ERROR] HMAC creation failed: {e}")
            return None
    
    def verify_hmac(self, message, received_hmac, key):
        """
        Verify HMAC to ensure message integrity and authenticity.
        
        Args:
            message: Original message string
            received_hmac: HMAC hex string to verify
            key: Secret key (AES key) used for HMAC
        
        Returns:
            True if HMAC is valid, False otherwise
        """
        try:
            expected_hmac = self.create_hmac(message, key)
            if expected_hmac is None:
                return False
            
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_hmac, received_hmac)
        except Exception as e:
            print(f"[CRYPTO ERROR] HMAC verification failed: {e}")
            return False


# Convenience functions for quick encryption/decryption
def quick_encrypt(message, key):
    """Quick AES encryption for simple use cases."""
    handler = CryptoHandler()
    return handler.encrypt_message(message, key)


def quick_decrypt(encrypted_message, key):
    """Quick AES decryption for simple use cases."""
    handler = CryptoHandler()
    return handler.decrypt_message(encrypted_message, key)
