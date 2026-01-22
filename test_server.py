"""
Integration tests for server functionality.
Tests multi-client connections and message routing.
"""

import socket
import threading
import time
import json
import config


def test_server_connection():
    """Test basic server connection."""
    print("\n" + "="*70)
    print("TEST 1: Server Connection")
    print("="*70)
    
    try:
        # Try to connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect(('localhost', config.DEFAULT_PORT))
        
        print("✓ Successfully connected to server")
        
        # Send test authentication
        auth_msg = f"{config.MSG_TYPE_AUTH}||TestUser||fake_public_key"
        client_socket.send(auth_msg.encode('utf-8'))
        
        # Wait for response
        response = client_socket.recv(config.BUFFER_SIZE).decode('utf-8')
        print(f"✓ Received response: {response}")
        
        client_socket.close()
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nMake sure server is running: python3 server.py")
        return False


def test_multiple_clients():
    """Test multiple client connections."""
    print("\n" + "="*70)
    print("TEST 2: Multiple Client Connections")
    print("="*70)
    
    clients = []
    usernames = ["Alice", "Bob", "Charlie"]
    
    try:
        # Connect multiple clients
        for username in usernames:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect(('localhost', config.DEFAULT_PORT))
            
            # Authenticate
            auth_msg = f"{config.MSG_TYPE_AUTH}||{username}||fake_public_key_{username}"
            client_socket.send(auth_msg.encode('utf-8'))
            
            response = client_socket.recv(config.BUFFER_SIZE).decode('utf-8')
            
            if response == "SUCCESS":
                print(f"✓ {username} connected successfully")
                clients.append((username, client_socket))
            else:
                print(f"✗ {username} failed to connect: {response}")
                return False
            
            time.sleep(0.5)
        
        print(f"\n✓ All {len(clients)} clients connected")
        
        # Clean up
        for username, sock in clients:
            sock.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Multiple client test failed: {e}")
        
        # Clean up
        for username, sock in clients:
            try:
                sock.close()
            except:
                pass
        
        return False


def test_message_routing():
    """Test message routing between clients."""
    print("\n" + "="*70)
    print("TEST 3: Message Routing")
    print("="*70)
    
    alice_socket = None
    bob_socket = None
    
    try:
        # Connect Alice
        alice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        alice_socket.settimeout(5)
        alice_socket.connect(('localhost', config.DEFAULT_PORT))
        
        auth_alice = f"{config.MSG_TYPE_AUTH}||Alice||pub_key_alice"
        alice_socket.send(auth_alice.encode('utf-8'))
        response = alice_socket.recv(config.BUFFER_SIZE).decode('utf-8')
        
        if response != "SUCCESS":
            print(f"✗ Alice authentication failed: {response}")
            return False
        
        print("✓ Alice connected")
        time.sleep(0.5)
        
        # Connect Bob
        bob_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bob_socket.settimeout(5)
        bob_socket.connect(('localhost', config.DEFAULT_PORT))
        
        auth_bob = f"{config.MSG_TYPE_AUTH}||Bob||pub_key_bob"
        bob_socket.send(auth_bob.encode('utf-8'))
        response = bob_socket.recv(config.BUFFER_SIZE).decode('utf-8')
        
        if response != "SUCCESS":
            print(f"✗ Bob authentication failed: {response}")
            return False
        
        print("✓ Bob connected")
        time.sleep(0.5)
        
        # Clear initial messages (user lists, key exchanges)
        def clear_messages(sock):
            sock.settimeout(1)
            try:
                while True:
                    sock.recv(config.BUFFER_SIZE)
            except socket.timeout:
                pass
            sock.settimeout(5)
        
        clear_messages(alice_socket)
        clear_messages(bob_socket)
        
        # Alice sends broadcast message
        print("\n✓ Testing broadcast message...")
        broadcast_msg = f"{config.MSG_TYPE_BROADCAST}||encrypted_test_message_from_alice"
        alice_socket.send(broadcast_msg.encode('utf-8'))
        
        # Bob should receive it
        received = bob_socket.recv(config.BUFFER_SIZE).decode('utf-8')
        
        if config.MSG_TYPE_BROADCAST in received and "Alice" in received:
            print("✓ Bob received broadcast message from Alice")
        else:
            print(f"✗ Unexpected message format: {received}")
            return False
        
        # Clean up
        alice_socket.close()
        bob_socket.close()
        
        print("\n✓ Message routing test passed")
        return True
        
    except Exception as e:
        print(f"✗ Message routing test failed: {e}")
        
        # Clean up
        if alice_socket:
            try:
                alice_socket.close()
            except:
                pass
        if bob_socket:
            try:
                bob_socket.close()
            except:
                pass
        
        return False


def test_duplicate_username():
    """Test handling of duplicate usernames."""
    print("\n" + "="*70)
    print("TEST 4: Duplicate Username Handling")
    print("="*70)
    
    client1 = None
    client2 = None
    
    try:
        # Connect first client
        client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client1.settimeout(5)
        client1.connect(('localhost', config.DEFAULT_PORT))
        
        auth_msg = f"{config.MSG_TYPE_AUTH}||DuplicateUser||pub_key_1"
        client1.send(auth_msg.encode('utf-8'))
        response = client1.recv(config.BUFFER_SIZE).decode('utf-8')
        
        if response != "SUCCESS":
            print(f"✗ First client authentication failed: {response}")
            return False
        
        print("✓ First 'DuplicateUser' connected")
        time.sleep(0.5)
        
        # Try to connect second client with same username
        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client2.settimeout(5)
        client2.connect(('localhost', config.DEFAULT_PORT))
        
        auth_msg = f"{config.MSG_TYPE_AUTH}||DuplicateUser||pub_key_2"
        client2.send(auth_msg.encode('utf-8'))
        response = client2.recv(config.BUFFER_SIZE).decode('utf-8')
        
        if "already taken" in response or "ERROR" in response:
            print(f"✓ Server correctly rejected duplicate username")
            print(f"  Response: {response}")
        else:
            print(f"✗ Server should have rejected duplicate, got: {response}")
            return False
        
        # Clean up
        client1.close()
        try:
            client2.close()
        except:
            pass
        
        print("\n✓ Duplicate username handling test passed")
        return True
        
    except Exception as e:
        print(f"✗ Duplicate username test failed: {e}")
        
        if client1:
            try:
                client1.close()
            except:
                pass
        if client2:
            try:
                client2.close()
            except:
                pass
        
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("CRYPTEX SERVER INTEGRATION TESTS")
    print("="*70)
    print("\nIMPORTANT: Make sure server.py is running before running these tests!")
    print("In another terminal, run: python3 server.py")
    
    input("\nPress Enter when server is ready...")
    
    results = []
    
    # Run tests
    results.append(("Server Connection", test_server_connection()))
    time.sleep(1)
    
    results.append(("Multiple Clients", test_multiple_clients()))
    time.sleep(1)
    
    results.append(("Message Routing", test_message_routing()))
    time.sleep(1)
    
    results.append(("Duplicate Username", test_duplicate_username()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
