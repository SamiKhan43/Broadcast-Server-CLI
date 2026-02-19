# Broadcast Server - Modular Implementation

A multi-threaded TCP broadcast server with username support, built with Python using a clean modular architecture.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## ✨ Features

- ✅ **Multi-threaded server** - Handle multiple clients simultaneously
- 👤 **Username support** - Clients can set custom usernames
- 📡 **Real-time broadcasting** - Messages instantly sent to all connected clients
- 🔒 **Thread-safe** - Uses locks to prevent race conditions
- 🛡️ **Error handling** - Graceful handling of disconnections and errors
- 🎯 **Modular design** - Clean separation of concerns
- ⚙️ **Configurable** - Easy configuration through `config.py`
- 🚀 **CLI interface** - Professional command-line interface

---

## 📁 Project Structure

```
broadcast-server/
│
├── main.py                 # Entry point - CLI interface
├── server.py              # Server implementation
├── broadcast_client.py    # Client implementation
├── config.py              # Configuration settings
└── README.md              # This file
```

### File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | Command-line interface and argument parsing |
| `server.py` | `BroadcastServer` class - handles all server logic |
| `broadcast_client.py` | `BroadcastClient` class - handles client connections |
| `config.py` | Configuration constants (host, port, buffer size, etc.) |

---

## 🚀 Installation

### Prerequisites

- Python 3.6 or higher
- No external dependencies required (uses only Python standard library)

### Setup

1. Download all files to a directory:
   ```bash
   mkdir broadcast-server
   cd broadcast-server
   ```

2. Save these files in the directory:
   - `main.py`
   - `server.py`
   - `broadcast_client.py`
   - `config.py`

That's it! No `pip install` needed.

---

## ⚡ Quick Start

### Step 1: Start the Server

Open a terminal and run:

```bash
python main.py start
```

You should see:
```
🚀 Broadcast Server started on 127.0.0.1:5000
📡 Waiting for clients to connect...
Press Ctrl+C to stop the server
```

### Step 2: Connect First Client

Open a **new terminal** and run:

```bash
python main.py connect
```

You'll be prompted:
```
Enter your name: Alice
Connected to 127.0.0.1:5000
You are chatting as: Alice
Type messages and press Enter. Type '/quit' to disconnect.
```

### Step 3: Connect More Clients

Open **another terminal** and connect again:

```bash
python main.py connect
```

```
Enter your name: Bob
Connected to 127.0.0.1:5000
You are chatting as: Bob
Type messages and press Enter. Type '/quit' to disconnect.
```

### Step 4: Start Chatting!

In Alice's terminal, type:
```
Hello everyone!
```

Bob will instantly see:
```
Alice: Hello everyone!
```

In Bob's terminal, type:
```
Hi Alice! 👋
```

Alice will see:
```
Bob: Hi Alice! 👋
```

---

## 📖 Usage

### Server Commands

#### Start server on default settings
```bash
python main.py start
```

#### Start server on custom port
```bash
python main.py start --port 8080
```

#### Start server on specific host and port
```bash
python main.py start --host 0.0.0.0 --port 8080
```

**Note:** Using `0.0.0.0` allows connections from other computers on your network.

### Client Commands

#### Connect to server on default settings
```bash
python main.py connect
```

#### Connect to server on custom port
```bash
python main.py connect --port 8080
```

#### Connect to remote server
```bash
python main.py connect --host 192.168.1.100 --port 8080
```

### Client Commands While Connected

| Command | Action |
|---------|--------|
| Type message + Enter | Send message to all clients |
| `/quit` | Disconnect from server |
| `quit` | Disconnect from server |
| `exit` | Disconnect from server |
| `Ctrl+C` | Force disconnect |
| `Ctrl+D` (EOF) | Graceful disconnect |

### Getting Help

```bash
python main.py --help
python main.py start --help
python main.py connect --help
```

---

## 🔍 How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                    SERVER                        │
│                                                 │
│  Main Thread:          Handler Threads:         │
│  ┌──────────────┐    ┌──────────────┐         │
│  │ Accept new   │───▶│ Handle       │         │
│  │ connections  │    │ Client 1     │         │
│  └──────────────┘    └──────────────┘         │
│                      ┌──────────────┐         │
│                      │ Handle       │         │
│                      │ Client 2     │         │
│                      └──────────────┘         │
│                                                 │
│  Shared Data: clients = {socket: username}     │
│  Protected by: clients_lock                    │
└─────────────────────────────────────────────────┘
                         │
                         │ TCP Connections
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        ┌──────────┐          ┌──────────┐
        │ CLIENT 1 │          │ CLIENT 2 │
        │  (Alice) │          │  (Bob)   │
        │          │          │          │
        │ Receiver │          │ Receiver │
        │ Thread   │          │ Thread   │
        │          │          │          │
        │ Main     │          │ Main     │
        │ Thread   │          │ Thread   │
        └──────────┘          └──────────┘
```

### Message Flow

1. **Client connects:**
   - Client creates socket and connects to server
   - Server accepts connection and adds to clients dictionary
   - Client prompted for username
   
2. **Client sends username:**
   - Client sends `/name Username` to server
   - Server updates clients dictionary: `{socket: "Username"}`
   - Server broadcasts join notification to all other clients
   
3. **Client sends message:**
   - Client types message and presses Enter
   - Message sent to server
   - Server receives message from Client A
   - Server formats: `"ClientA: message"`
   - Server broadcasts to all clients except sender
   
4. **Client receives message:**
   - Client's receiver thread constantly listens
   - When data arrives, immediately displays it
   - User continues typing without interruption

### Threading Model

**Server:**
- **Main thread:** Accepts new client connections (blocking)
- **Handler threads:** One per client - receives and broadcasts messages
- **Thread safety:** `clients_lock` protects shared `clients` dictionary

**Client:**
- **Main thread:** Reads keyboard input and sends to server (blocking on input)
- **Receiver thread:** Listens for server messages and displays them (blocking on recv)

### Key Design Decisions

1. **Username Registration:**
   - Uses special `/name` command on connection
   - Server stores username with socket in dictionary
   - Clean separation between authentication and messaging

2. **No Message Delimiters:**
   - Since each message is a single `sendall()` call
   - TCP guarantees message boundaries for our use case
   - Simpler than newline-delimited protocol

3. **Daemon Threads:**
   - Receiver thread is daemon - dies with main program
   - Prevents zombie threads on unexpected exit

4. **Broadcasting:**
   - Sender excluded from broadcast (doesn't echo own messages)
   - Failed sends automatically remove disconnected clients

---

## ⚙️ Configuration

Edit `config.py` to customize settings:

```python
# Network configuration
DEFAULT_HOST = '127.0.0.1'  # Change to '0.0.0.0' for external access
DEFAULT_PORT = 5000          # Change to any port 1024-65535

# Buffer size for receiving data
BUFFER_SIZE = 1024

# Server limits
MAX_CLIENTS = 100           # Maximum simultaneous clients
CONNECTION_TIMEOUT = 300    # Timeout for inactive connections (seconds)

# Message settings
MAX_MESSAGE_LENGTH = 4096   # Maximum message length in bytes
MAX_NAME_LENGTH = 50        # Maximum username length
```

### Common Configuration Scenarios

**Allow External Connections:**
```python
DEFAULT_HOST = '0.0.0.0'  # Listen on all network interfaces
```

**Change Port:**
```python
DEFAULT_PORT = 8080  # Use port 8080 instead
```

**Increase Buffer Size:**
```python
BUFFER_SIZE = 4096  # For larger messages
```

---

## 📝 Examples

### Example 1: Basic Chat Session

**Server Terminal:**
```
$ python main.py start
🚀 Broadcast Server started on 127.0.0.1:5000
📡 Waiting for clients to connect...

✅ New connection from ('127.0.0.1', 54321)
👥 Total clients: 1
🔄 Started handler for ('127.0.0.1', 54321)
📝 Client set name: Alice

✅ New connection from ('127.0.0.1', 54322)
👥 Total clients: 2
🔄 Started handler for ('127.0.0.1', 54322)
📝 Client set name: Bob

📨 Alice: Hey Bob!
📨 Bob: Hi Alice! How are you?
📨 Alice: Great! This server is working perfectly 🎉
```

**Alice's Terminal:**
```
$ python main.py connect
Enter your name: Alice
Connected to 127.0.0.1:5000
You are chatting as: Alice
Type messages and press Enter. Type '/quit' to disconnect.
Welcome, Alice! You are now connected.
📢 Bob has joined the chat!
Hey Bob!
Bob: Hi Alice! How are you?
Great! This server is working perfectly 🎉
```

**Bob's Terminal:**
```
$ python main.py connect
Enter your name: Bob
Connected to 127.0.0.1:5000
You are chatting as: Bob
Type messages and press Enter. Type '/quit' to disconnect.
Welcome, Bob! You are now connected.
Alice: Hey Bob!
Hi Alice! How are you?
Alice: Great! This server is working perfectly 🎉
```

### Example 2: Multiple Clients

**Start server and 3 clients:**
```bash
# Terminal 1
python main.py start

# Terminal 2
python main.py connect
# Enter name: Alice

# Terminal 3
python main.py connect
# Enter name: Bob

# Terminal 4
python main.py connect
# Enter name: Charlie
```

**Everyone chats:**
- Alice sends: "Hello everyone!"
- Bob sees: "Alice: Hello everyone!"
- Charlie sees: "Alice: Hello everyone!"
- All messages broadcast to all clients

### Example 3: Client Disconnection

**Bob disconnects:**
```
/quit
Disconnected
```

**Alice sees:**
```
📢 Bob has left the chat.
```

**Server logs:**
```
👋 Bob disconnected
🧹 Cleaned up Bob
👥 Remaining clients: 2
```

### Example 4: Custom Port

**Start server on port 8080:**
```bash
python main.py start --port 8080
```

**Connect client:**
```bash
python main.py connect --port 8080
```

### Example 5: Network Chat

**Find your IP address:**
```bash
# Linux/Mac
hostname -I

# Windows
ipconfig
```

**Start server accepting external connections:**
```bash
python main.py start --host 0.0.0.0 --port 5000
```

**From another computer on same network:**
```bash
python main.py connect --host 192.168.1.100 --port 5000
```

---

## 🐛 Troubleshooting

### Problem: "Failed to connect" Error

**Symptoms:**
```
Failed to connect to 127.0.0.1:5000 - [Errno 111] Connection refused
```

**Causes:**
1. Server not running
2. Wrong port number
3. Firewall blocking connection

**Solutions:**
```bash
# 1. Check if server is running
# Look for "Broadcast Server started" message

# 2. Verify port numbers match
python main.py start --port 5000
python main.py connect --port 5000

# 3. Check firewall (Linux)
sudo ufw allow 5000/tcp

# Windows: Add inbound rule in Windows Firewall
```

### Problem: "Address already in use"

**Symptoms:**
```
OSError: [Errno 98] Address already in use
```

**Cause:** Port still occupied from previous run

**Solutions:**
```bash
# Option 1: Wait 30-60 seconds and try again

# Option 2: Find and kill process using port
lsof -ti:5000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :5000   # Windows (note PID, then taskkill)

# Option 3: Use different port
python main.py start --port 5001
```

### Problem: Messages not appearing

**Symptoms:** Type message but nothing happens

**Debugging:**
1. Check server terminal - do you see "📨 Username: message"?
2. If yes: Problem is in broadcasting
3. If no: Problem is in receiving

**Solutions:**
- Press Enter after typing (required to send)
- Check network connection
- Verify username was set successfully
- Restart client and server

### Problem: "Name cannot be empty"

**Cause:** Pressing Enter without typing a name

**Solution:** Type a username before pressing Enter

### Problem: Connection drops unexpectedly

**Symptoms:**
```
Connection error while receiving data
Disconnected
```

**Causes:**
1. Server crashed or stopped
2. Network interruption
3. Firewall blocked connection

**Solutions:**
- Check server is still running
- Check network connectivity
- Reconnect: `python main.py connect`

### Problem: Server is full

**Symptoms:**
```
Server is full. Try again later.
Disconnected
```

**Cause:** Max clients limit reached (default: 100)

**Solutions:**
```python
# Edit config.py and increase limit
MAX_CLIENTS = 200
```

---

## 🎓 Advanced Usage

### Running on Different Networks

**Scenario:** Run server on one computer, clients on others

**Step 1:** Find server's IP address
```bash
# Linux/Mac
hostname -I
# Example output: 192.168.1.100

# Windows
ipconfig
# Look for IPv4 Address
```

**Step 2:** Start server accepting external connections
```bash
python main.py start --host 0.0.0.0 --port 5000
```

**Step 3:** Configure firewall
```bash
# Linux (ufw)
sudo ufw allow 5000/tcp

# Windows: Windows Defender Firewall > Inbound Rules > New Rule
# Select Port > TCP > 5000 > Allow connection
```

**Step 4:** Connect from other computers
```bash
python main.py connect --host 192.168.1.100 --port 5000
```

### Port Forwarding for Internet Access

**Warning:** Only do this on trusted networks. Never expose ports directly to the internet without proper security.

**Step 1:** Configure router port forwarding
- Log into router admin panel (usually 192.168.1.1)
- Find "Port Forwarding" section
- Forward external port 5000 to internal IP:5000

**Step 2:** Find public IP
```bash
curl ifconfig.me
```

**Step 3:** Connect from anywhere
```bash
python main.py connect --host <YOUR_PUBLIC_IP> --port 5000
```

### Running as Background Service

**Linux (using systemd):**

Create `/etc/systemd/system/broadcast-server.service`:
```ini
[Unit]
Description=Broadcast Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/broadcast-server
ExecStart=/usr/bin/python3 main.py start
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable broadcast-server
sudo systemctl start broadcast-server
sudo systemctl status broadcast-server
```

### Logging

**Add logging to server:**

Edit `server.py` - add at top:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='server.log'
)
```

Replace `print()` statements:
```python
# Instead of:
print(f"New connection from {client_address}")

# Use:
logging.info(f"New connection from {client_address}")
```

### Security Considerations

**Current Implementation:**
- ❌ No encryption (messages sent in plain text)
- ❌ No authentication (anyone can connect)
- ❌ No rate limiting (vulnerable to spam)
- ❌ No input validation (vulnerable to malformed messages)

**For Production Use, Add:**
1. **TLS/SSL encryption** using `ssl` module
2. **Password authentication**
3. **Rate limiting** per client
4. **Input validation** and sanitization
5. **Connection limits** per IP
6. **Logging** for audit trail

---

## 🔧 Extending the Server

### Add Commands

**Idea:** Private messages with `/msg username message`

Edit `server.py` in `handle_client()`:
```python
if buffer.startswith("/msg "):
    parts = buffer.split(" ", 2)
    if len(parts) >= 3:
        target_name = parts[1]
        message = parts[2]
        
        # Find target client
        with self.clients_lock:
            for sock, name in self.clients.items():
                if name == target_name:
                    sock.send(f"[Private from {client_name}]: {message}".encode())
                    break
```

### Add Timestamps

```python
from datetime import datetime

# In broadcast():
timestamp = datetime.now().strftime("%H:%M:%S")
formatted = f"[{timestamp}] {message}"
```

### Add Message History

```python
# In server __init__:
self.message_history = []

# In handle_client:
self.message_history.append((client_name, message))

# When new client connects:
for name, msg in self.message_history[-10:]:  # Last 10 messages
    client_socket.send(f"{name}: {msg}\n".encode())
```

### Add Rooms/Channels

```python
# In server __init__:
self.rooms = {}  # {room_name: [socket1, socket2, ...]}

# Add /join command:
if buffer.startswith("/join "):
    room = buffer[6:].strip()
    if room not in self.rooms:
        self.rooms[room] = []
    self.rooms[room].append(client_socket)
```

---

## 📚 Code Documentation

### `config.py`

Configuration constants used throughout the application.

**Constants:**
- `DEFAULT_HOST`: Default IP to bind server or connect client
- `DEFAULT_PORT`: Default port number
- `BUFFER_SIZE`: Size of receive buffer in bytes
- `MAX_CLIENTS`: Maximum concurrent client connections
- `CONNECTION_TIMEOUT`: Timeout for inactive connections
- `MAX_MESSAGE_LENGTH`: Maximum message size
- `MAX_NAME_LENGTH`: Maximum username length

### `server.py`

**Class: `BroadcastServer`**

Main server implementation using TCP sockets and threading.

**Methods:**
- `__init__(host, port)`: Initialize server with host and port
- `start()`: Start server, bind to port, accept connections
- `handle_client(socket, address)`: Handle single client (runs in thread)
- `broadcast(message, exclude)`: Send message to all clients except exclude
- `remove_client(socket)`: Thread-safe removal of client
- `shutdown()`: Gracefully close all connections and stop server

**Attributes:**
- `clients`: Dictionary mapping sockets to usernames
- `clients_lock`: Threading lock for thread-safe access
- `running`: Boolean flag for server state

### `broadcast_client.py`

**Class: `BroadcastClient`**

Client implementation for connecting to server.

**Methods:**
- `__init__(host, port)`: Initialize client with server details
- `connect()`: Connect to server and start communication
- `_receive_loop()`: Continuously receive messages (runs in thread)
- `name()`: Prompt user for username
- `disconnect()`: Close connection and clean up

**Attributes:**
- `socket`: TCP socket connected to server
- `running`: Boolean flag for client state
- `host`, `port`: Server connection details

### `main.py`

**Functions:**
- `main()`: Parse arguments and route to start_server or start_client
- `start_server(args)`: Create and start BroadcastServer
- `start_client(args)`: Create and start BroadcastClient

---

## 🤝 Contributing Ideas

Want to improve this? Here are enhancement ideas:

1. **Security:**
   - Add TLS/SSL encryption
   - Implement password authentication
   - Add rate limiting

2. **Features:**
   - Private messaging
   - Chat rooms/channels
   - File sharing
   - Message history
   - User list command
   - Typing indicators

3. **UI:**
   - Colors in terminal
   - GUI client with Tkinter
   - Web interface with Flask

4. **Persistence:**
   - Save messages to database
   - User accounts and profiles
   - Message search

5. **Advanced:**
   - Voice/video chat
   - End-to-end encryption
   - Mobile app client

---

## 📜 License

This is educational code - free to use, modify, and learn from!

---

## ❓ FAQ

**Q: Can multiple clients have the same username?**  
A: Yes, currently there's no uniqueness check. You could add this in `handle_client()`.

**Q: What happens if a message is very long?**  
A: Messages are limited by `MAX_MESSAGE_LENGTH` in config (default 4096 bytes). TCP will fragment and reassemble automatically.

**Q: Why use threading instead of async/await?**  
A: Threading is simpler to understand for beginners. For production, `asyncio` is more efficient.

**Q: Can I use this in production?**  
A: This is educational code. For production, use frameworks like Socket.IO, Django Channels, or add security features.

**Q: How do I make it secure?**  
A: Add TLS/SSL encryption, authentication, input validation, and rate limiting. Use `ssl.wrap_socket()` for encryption.

**Q: Why does the client use `sendall()` instead of `send()`?**  
A: `sendall()` ensures all data is sent. `send()` might only send partial data.

**Q: How many clients can connect?**  
A: Default limit is 100 (configurable in `config.py`). Real limit depends on system resources.

**Q: Can I connect from a different network?**  
A: Yes! Use port forwarding on your router. See "Advanced Usage" section.

---

## 🎯 Testing Checklist

Test your implementation:

- [ ] Server starts without errors
- [ ] Client can connect
- [ ] Username prompt works
- [ ] Messages broadcast to all clients
- [ ] Multiple clients work simultaneously
- [ ] Client disconnection handled gracefully
- [ ] Server shutdown closes all connections
- [ ] Custom ports work
- [ ] `/quit` command disconnects client
- [ ] Empty messages are ignored
- [ ] New client sees join notification
- [ ] Disconnecting client shows leave notification

---

## 📞 Support

Having issues? Here's how to debug:

1. **Enable verbose output:** Add print statements
2. **Check server logs:** Look for error messages in server terminal
3. **Test locally first:** Use `127.0.0.1` before trying network
4. **Verify ports:** Make sure client and server use same port
5. **Check firewall:** Temporarily disable to test

---
[roadmap.sh](https://roadmap.sh/projects/broadcast-server)

**Happy Broadcasting! 📡**

Made with ❤️ for learning network programming
