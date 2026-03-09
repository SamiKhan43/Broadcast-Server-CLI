import socket
import threading
from config import BUFFER_SIZE, DEFAULT_HOST, DEFAULT_PORT


class BroadcastClient:

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.socket = None    # The TCP socket used to communicate with the server
        self.running = False  # Controls the receive loop and main input loop

    def connect(self):
        # Create a TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.host, self.port))
        except Exception as exc:
            print(f"Failed to connect to {self.host}:{self.port} - {exc}")
            return

        # Ask the user for a display name before entering the chat
        name = self._prompt_for_name()

        try:
            # Send the name to the server using the /name command format it expects
            self.socket.sendall(f"/name {name}".encode("utf-8"))
        except Exception as exc:
            print(f"Failed to send your name - {exc}")
            self.disconnect()
            return

        self.running = True
        print(f"Connected to {self.host}:{self.port}")
        print(f"You are chatting as: {name}")
        print("Type messages and press Enter. Type '/quit' to disconnect.")

        # Start the listener in a daemon thread so it doesn't block the input loop,
        # and so it automatically dies if the main thread exits
        listener = threading.Thread(target=self._receive_loop, daemon=True)
        listener.start()

        try:
            # Main input loop — reads user input and sends it to the server
            while self.running:
                try:
                    message = input()
                except EOFError:
                    # EOFError occurs when stdin is closed (e.g. piped input ends)
                    break

                # Allow the user to gracefully exit with common quit commands
                if message.strip().lower() in {"/quit", "quit", "exit"}:
                    break

                # Don't send empty messages
                if not message.strip():
                    continue

                try:
                    self.socket.sendall(message.encode("utf-8"))
                except Exception as exc:
                    print(f"Failed to send message - {exc}")
                    break

        finally:
            # Always clean up the connection when the input loop ends
            self.disconnect()

    def _receive_loop(self):
        # Runs on a background thread, printing incoming messages as they arrive.
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE)

                # Empty data signals the server has closed the connection
                if not data:
                    print("Server closed the connection")
                    self.running = False
                    break

                # Print without a newline since the server already appends one
                print(data.decode("utf-8"), end="")

            except Exception:
                # Only report the error if we didn't intentionally stop running
                if self.running:
                    print("Connection error while receiving data")
                self.running = False
                break

    def _prompt_for_name(self):
        # Prompts the user for a non-empty display name before joining the chat.
        while True:
            try:
                name = input("Enter your name: ").strip()
            except EOFError:
                # Fall back to a default name if stdin is unavailable
                return "Guest"

            if name:
                return name

            print("Name cannot be empty.")

    def disconnect(self):
        # Cleanly shuts down the socket and stops all loops.
        # Guard against being called multiple times or before connecting
        if not self.running and self.socket is None:
            return

        self.running = False

        if self.socket:
            try:
                # Shut down both send and receive before closing
                # to unblock any pending recv() calls in the listener thread
                self.socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass

            try:
                self.socket.close()
            except Exception:
                pass

            self.socket = None

        print("Disconnected")
