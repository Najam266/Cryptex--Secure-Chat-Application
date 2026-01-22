# Cryptex - Secure Local Chat Application

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-Educational-green)
![Encryption](https://img.shields.io/badge/Encryption-RSA%2BAES-red)

## 🔒 Overview

**Cryptex** is a secure, encrypted local chat application designed for safe peer-to-peer communication over a Local Area Network (LAN). Built with hybrid cryptography combining **RSA** (for key exchange) and **AES** (for message encryption), Cryptex ensures data confidentiality, integrity, and authentication without relying on internet or third-party servers.

### Key Features

- 🔐 **End-to-End Encryption**: Hybrid RSA (2048-bit) + AES (256-bit) encryption
- 🌐 **LAN-Based**: No internet required, works entirely on local network
- 👥 **Multi-User Support**: Multiple clients can connect simultaneously
- 💬 **Broadcast & Direct Messaging**: Send to all users or specific recipients
- 🔑 **Secure Key Exchange**: Automated RSA public key distribution
- ✅ **Message Integrity**: Digital signatures for verification
- 🎨 **Modern GUI**: Professional dark-theme Tkinter interface
- 🚀 **Real-Time Communication**: Low-latency message delivery

---

## 📋 Requirements

- **Python 3.7+**
- **Operating System**: Windows, macOS, or Linux
- **Network**: Local Area Network (LAN) connection

---

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd "IS project"
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

This will install:
- `pycryptodome` - Cryptography library for RSA and AES encryption

### 3. Verify Installation

```bash
python3 -c "from Crypto.Cipher import AES; print('✓ Dependencies installed successfully')"
```

---

## 🎯 Usage

### Running the Server

The server coordinates all client connections and message routing. Start it on one machine:

```bash
python3 server.py
```

**Custom Port (Optional):**
```bash
python3 server.py 6000
```

The server will display:
```
============================================================
🔒 CRYPTEX SERVER STARTED
============================================================
Host: 0.0.0.0
Port: 5555
Max Connections: 10
Waiting for clients to connect...
============================================================
```

### Running the GUI Client

Launch the graphical client on each user's machine:

```bash
python3 gui_client.py
```

**Steps:**
1. **Login Window** appears
2. Enter your **username** (3-20 characters, alphanumeric)
3. Enter **server host** (IP address or `localhost`)
4. Enter **server port** (default: `5555`)
5. Click **Connect**

### Running Console Client (Alternative)

For testing or headless environments:

```bash
python3 client.py <username> [host] [port]
```

**Example:**
```bash
python3 client.py Alice localhost 5555
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Client 1  │         │   Server    │         │   Client 2  │
│  (GUI/CLI)  │◄───────►│  (Hub)      │◄───────►│  (GUI/CLI)  │
└─────────────┘         └─────────────┘         └─────────────┘
      │                       │                       │
   RSA Keys              Key Exchange             RSA Keys
   AES Session           Message Routing          AES Session
```

### Encryption Flow

1. **Key Generation**: Each client generates RSA key pair (2048-bit)
2. **Authentication**: Client sends username + public key to server
3. **Key Distribution**: Server distributes public keys to all clients
4. **Message Encryption**: 
   - Sender encrypts message with AES-256 (CBC mode)
   - AES session key is shared among clients
5. **Message Routing**: Server forwards encrypted message to recipient(s)
6. **Decryption**: Recipient decrypts message with shared AES key

### Security Features

| Feature | Implementation |
|---------|----------------|
| **Asymmetric Encryption** | RSA 2048-bit for key exchange |
| **Symmetric Encryption** | AES 256-bit CBC mode for messages |
| **Digital Signatures** | PKCS#1 v1.5 with SHA-256 |
| **Key Management** | Automated public key distribution |
| **Session Security** | Unique initialization vectors per message |

---

## 📁 Project Structure

```
IS project/
├── server.py              # Server module (message routing)
├── client.py              # Client backend (encryption/networking)
├── gui_client.py          # GUI application (Tkinter)
├── crypto_handler.py      # Cryptography module (RSA + AES)
├── config.py              # Configuration constants
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── test_crypto.py         # Cryptography unit tests
├── test_server.py         # Server integration tests
└── README.md              # This file
```

---

## 🧪 Testing

### Unit Tests - Cryptography

Test encryption/decryption functionality:

```bash
python3 test_crypto.py
```

### Integration Tests - Server

Test server with multiple clients:

```bash
python3 test_server.py
```

### Manual Testing

**Scenario 1: Local Testing (Same Machine)**
1. Terminal 1: `python3 server.py`
2. Terminal 2: `python3 gui_client.py` (User: Alice)
3. Terminal 3: `python3 gui_client.py` (User: Bob)

**Scenario 2: LAN Testing (Different Machines)**
1. **Server Machine**: 
   - Find IP: `ifconfig` (macOS/Linux) or `ipconfig` (Windows)
   - Start server: `python3 server.py`
2. **Client Machines**:
   - Run `python3 gui_client.py`
   - Enter server's IP address in login

---

## 🎨 GUI Features

### Login Window
- Modern dark theme design
- Input validation for username, host, and port
- Clean, professional interface

### Chat Window
- **Left Sidebar**: Online user list with selection
- **Main Area**: Color-coded message display
  - 🔵 Blue: Your sent messages
  - 🟢 Green: Received messages
  - ⚙️ Gray: System notifications
- **Input Area**: Multi-line text input with Send button
- **Top Bar**: Connection status indicator (🟢 Connected / 🔴 Disconnected)
- **Encryption Indicator**: 🔒 icon on Send button

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Server Settings
DEFAULT_PORT = 5555
MAX_CONNECTIONS = 10

# Encryption Settings
RSA_KEY_SIZE = 2048
AES_KEY_SIZE = 32  # 256 bits

# GUI Theme
MAIN_BG_COLOR = "#1e1e1e"
ACCENT_COLOR = "#007acc"
```

---

## 🛡️ Security Considerations

### What Cryptex Provides
✅ End-to-end encryption for messages  
✅ Secure key exchange using RSA  
✅ Message integrity verification  
✅ Protection against eavesdropping on LAN

### Limitations
⚠️ **Local Network Only**: Not designed for internet communication  
⚠️ **Educational Project**: Not audited for production use  
⚠️ **Simplified Key Management**: Uses shared session keys for simplicity  
⚠️ **No Persistence**: Messages not stored after session ends

---

## 🐛 Troubleshooting

### Connection Issues

**Problem**: Client can't connect to server  
**Solutions**:
- Verify server is running: Check terminal for "SERVER STARTED" message
- Check firewall: Allow Python through firewall on server machine
- Verify IP address: Use `ifconfig`/`ipconfig` to confirm server IP
- Test connectivity: `ping <server_ip>` from client machine

**Problem**: "Username already taken"  
**Solution**: Choose a different username (each must be unique)

### Installation Issues

**Problem**: `ModuleNotFoundError: No module named 'Crypto'`  
**Solution**: Install dependencies: `pip3 install pycryptodome`

**Problem**: `tkinter` import error  
**Solution**: Install tkinter:
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- macOS: Included with Python (use official Python.org installer)
- Windows: Included with Python

---

## 📚 Technical Details

### Message Protocol

All messages follow this format: `TYPE||FIELD1||FIELD2||...`

| Message Type | Format | Purpose |
|-------------|--------|---------|
| `AUTH` | `AUTH\|\|username\|\|public_key` | User authentication |
| `KEY_EXCHANGE` | `KEY_EXCHANGE\|\|username\|\|public_key` | Public key distribution |
| `MESSAGE` | `MESSAGE\|\|recipient\|\|encrypted_content` | Direct message |
| `BROADCAST` | `BROADCAST\|\|encrypted_content` | Broadcast message |
| `USER_LIST` | `USER_LIST\|\|user_list_json` | Online users update |

### Encryption Details

**RSA Key Exchange**:
- Algorithm: RSA with OAEP padding
- Key Size: 2048 bits
- Hash: SHA-256

**AES Message Encryption**:
- Algorithm: AES-256
- Mode: CBC (Cipher Block Chaining)
- IV: Random 16 bytes per message
- Padding: PKCS#7

---

## 👥 Authors

- **Najam Ul Islam Saeed** - 22l-7497 - BS(DS)
- **Annas Ali** - 22l-7480 - BS(DS)
- **Shahmir Iqbal** - 22l-7471 - BS(DS)

---

## 📖 References

1. William Stallings, *Cryptography and Network Security: Principles and Practice*, Pearson
2. Python Documentation – Socket Programming and Cryptography Libraries
3. Research Papers on Hybrid Cryptography and Secure Communication Models

---

## 📄 License

This project is developed for educational purposes as part of an Information Security course.

---

## 🎓 Project Purpose

Cryptex demonstrates the implementation of secure communication principles including:
- Hybrid cryptography (combining asymmetric and symmetric encryption)
- Socket programming for network communication
- Multi-threaded server architecture
- User authentication and key management
- Graphical user interface design

Perfect for learning secure communication protocols and cryptographic applications!

---

**🔒 Stay Secure. Stay Connected. Cryptex.**
