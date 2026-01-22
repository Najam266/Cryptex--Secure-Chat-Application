"""
Unit tests for cryptography module.
Tests RSA key generation, AES encryption/decryption, and message integrity.
"""

import unittest
import sys
from crypto_handler import CryptoHandler


class TestCryptoHandler(unittest.TestCase):
    """Test cases for CryptoHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.crypto1 = CryptoHandler()
        self.crypto2 = CryptoHandler()
        
    def test_rsa_key_generation(self):
        """Test RSA key pair generation."""
        self.crypto1.generate_rsa_keys()
        
        self.assertIsNotNone(self.crypto1.rsa_key)
        self.assertIsNotNone(self.crypto1.public_key)
        self.assertIsNotNone(self.crypto1.private_key)
        print("✓ RSA key generation successful")
    
    def test_public_key_export(self):
        """Test public key export in PEM format."""
        self.crypto1.generate_rsa_keys()
        public_key_pem = self.crypto1.export_public_key()
        
        self.assertIsNotNone(public_key_pem)
        self.assertIn("BEGIN PUBLIC KEY", public_key_pem)
        self.assertIn("END PUBLIC KEY", public_key_pem)
        print("✓ Public key export successful")
    
    def test_peer_key_import(self):
        """Test importing peer's public key."""
        self.crypto1.generate_rsa_keys()
        self.crypto2.generate_rsa_keys()
        
        public_key_1 = self.crypto1.export_public_key()
        success = self.crypto2.import_peer_public_key("Alice", public_key_1)
        
        self.assertTrue(success)
        self.assertIn("Alice", self.crypto2.peer_public_keys)
        print("✓ Peer key import successful")
    
    def test_aes_key_generation(self):
        """Test AES session key generation."""
        aes_key = self.crypto1.generate_aes_key()
        
        self.assertIsNotNone(aes_key)
        self.assertEqual(len(aes_key), 32)  # 256 bits = 32 bytes
        print("✓ AES key generation successful")
    
    def test_aes_encryption_decryption(self):
        """Test AES message encryption and decryption."""
        self.crypto1.generate_rsa_keys()
        aes_key = self.crypto1.generate_aes_key()
        
        original_message = "Hello, this is a secret message! 🔒"
        
        # Encrypt
        encrypted = self.crypto1.encrypt_message(original_message, aes_key)
        self.assertIsNotNone(encrypted)
        self.assertNotEqual(encrypted, original_message)
        
        # Decrypt
        decrypted = self.crypto1.decrypt_message(encrypted, aes_key)
        self.assertEqual(decrypted, original_message)
        
        print(f"✓ AES encryption/decryption successful")
        print(f"  Original: {original_message}")
        print(f"  Encrypted: {encrypted[:50]}...")
        print(f"  Decrypted: {decrypted}")
    
    def test_rsa_key_exchange(self):
        """Test RSA-based AES key exchange between two parties."""
        # Both parties generate keys
        self.crypto1.generate_rsa_keys()
        self.crypto2.generate_rsa_keys()
        
        # Exchange public keys
        pub_key_1 = self.crypto1.export_public_key()
        pub_key_2 = self.crypto2.export_public_key()
        
        self.crypto1.import_peer_public_key("Bob", pub_key_2)
        self.crypto2.import_peer_public_key("Alice", pub_key_1)
        
        # Alice generates AES key and encrypts it for Bob
        aes_key = self.crypto1.generate_aes_key()
        encrypted_key = self.crypto1.encrypt_aes_key_with_rsa(aes_key, "Bob")
        self.assertIsNotNone(encrypted_key)
        
        # Bob decrypts the AES key
        decrypted_key = self.crypto2.decrypt_aes_key_with_rsa(encrypted_key)
        self.assertEqual(aes_key, decrypted_key)
        
        print("✓ RSA key exchange successful")
    
    def test_end_to_end_encryption(self):
        """Test complete end-to-end encryption workflow."""
        # Setup
        self.crypto1.generate_rsa_keys()
        self.crypto2.generate_rsa_keys()
        
        pub_key_1 = self.crypto1.export_public_key()
        pub_key_2 = self.crypto2.export_public_key()
        
        self.crypto1.import_peer_public_key("Bob", pub_key_2)
        self.crypto2.import_peer_public_key("Alice", pub_key_1)
        
        # Alice creates and shares AES key
        aes_key = self.crypto1.generate_aes_key()
        
        # Alice encrypts message
        original_message = "Top secret message from Alice to Bob! 🔐"
        encrypted_message = self.crypto1.encrypt_message(original_message, aes_key)
        
        # Bob receives and decrypts using same key
        decrypted_message = self.crypto2.decrypt_message(encrypted_message, aes_key)
        
        self.assertEqual(decrypted_message, original_message)
        print("✓ End-to-end encryption successful")
    
    def test_message_signature(self):
        """Test digital signature creation and verification."""
        self.crypto1.generate_rsa_keys()
        self.crypto2.generate_rsa_keys()
        
        # Exchange public keys
        pub_key_1 = self.crypto1.export_public_key()
        self.crypto2.import_peer_public_key("Alice", pub_key_1)
        
        # Alice signs a message
        message = "This message is authentic"
        signature = self.crypto1.sign_message(message)
        self.assertIsNotNone(signature)
        
        # Bob verifies the signature
        is_valid = self.crypto2.verify_signature(message, signature, "Alice")
        self.assertTrue(is_valid)
        
        # Test with tampered message
        tampered_message = "This message is tampered"
        is_valid_tampered = self.crypto2.verify_signature(tampered_message, signature, "Alice")
        self.assertFalse(is_valid_tampered)
        
        print("✓ Digital signature verification successful")
    
    def test_long_message_encryption(self):
        """Test encryption of long messages."""
        self.crypto1.generate_rsa_keys()
        aes_key = self.crypto1.generate_aes_key()
        
        # Create long message
        long_message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
        
        # Encrypt and decrypt
        encrypted = self.crypto1.encrypt_message(long_message, aes_key)
        decrypted = self.crypto1.decrypt_message(encrypted, aes_key)
        
        self.assertEqual(decrypted, long_message)
        print(f"✓ Long message encryption successful ({len(long_message)} chars)")
    
    def test_special_characters(self):
        """Test encryption with special characters and emojis."""
        self.crypto1.generate_rsa_keys()
        aes_key = self.crypto1.generate_aes_key()
        
        special_message = "Hello! 你好! Привет! مرحبا! 🔒🔐🌟💬"
        
        encrypted = self.crypto1.encrypt_message(special_message, aes_key)
        decrypted = self.crypto1.decrypt_message(encrypted, aes_key)
        
        self.assertEqual(decrypted, special_message)
        print(f"✓ Special characters encryption successful")


def run_tests():
    """Run all tests with custom output."""
    print("="*70)
    print("CRYPTEX CRYPTOGRAPHY MODULE TESTS")
    print("="*70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCryptoHandler)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
