# Broadcast Server CLI

A simple TCP broadcast chat app in Python.

## Features
- Start a broadcast server from CLI.
- Connect multiple terminal clients.
- Clients enter a username on connect.
- Messages are shown as `username: message`.
- Join/leave notifications are broadcast.

## Project Files
- `main.py`: CLI entrypoint (`start` / `connect`)
- `server.py`: Broadcast server
- `broadcast_client.py`: Interactive chat client
- `config.py`: Default host, port, and buffer size

## Requirements
- Python 3.10+ (tested on Python 3.12)

## Run
1. Open terminal 1:
```bash
cd /home/usama/Desktop/python/Broadcast-Server-cli
python3 main.py start
```

2. Open terminal 2 (and more terminals for more users):
```bash
cd /home/usama/Desktop/python/Broadcast-Server-cli
python3 main.py connect
```

3. When prompted:
- Enter your name.
- Type messages and press Enter.
- Type `/quit` to disconnect.

## Optional Host/Port
Use custom host/port:

```bash
python3 main.py start --host 127.0.0.1 --port 5000
python3 main.py connect --host 127.0.0.1 --port 5000
```

## Expected Behavior
- Server prints when clients connect/disconnect.
- Other clients see:
  - `* username joined the chat`
  - `username: message`
  - `* username left the chat`

## Troubleshooting
- `ImportError: cannot import name 'BroadcastClient'`:
  - Ensure `broadcast_client.py` contains the `BroadcastClient` class.
- `Address already in use`:
  - Change port with `--port` or stop the existing process.
- `Connection refused`:
  - Start the server first, then connect clients.
