import socket
import threading

from config import BUFFER_SIZE, DEFAULT_HOST, DEFAULT_PORT


class BroadcastClient:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
        except Exception as exc:
            print(f"Failed to connect to {self.host}:{self.port} - {exc}")
            return

        name = self._prompt_for_name()
        try:
            self.socket.sendall(f"/name {name}".encode("utf-8"))
        except Exception as exc:
            print(f"Failed to send your name - {exc}")
            self.disconnect()
            return

        self.running = True
        print(f"Connected to {self.host}:{self.port}")
        print(f"You are chatting as: {name}")
        print("Type messages and press Enter. Type '/quit' to disconnect.")

        listener = threading.Thread(target=self._receive_loop, daemon=True)
        listener.start()

        try:
            while self.running:
                try:
                    message = input()
                except EOFError:
                    break

                if message.strip().lower() in {"/quit", "quit", "exit"}:
                    break

                if not message.strip():
                    continue

                try:
                    self.socket.sendall(message.encode("utf-8"))
                except Exception as exc:
                    print(f"Failed to send message - {exc}")
                    break
        finally:
            self.disconnect()

    def _receive_loop(self):
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    print("Server closed the connection")
                    self.running = False
                    break

                print(data.decode("utf-8"), end="")
            except Exception:
                if self.running:
                    print("Connection error while receiving data")
                self.running = False
                break

    def _prompt_for_name(self):
        while True:
            try:
                name = input("Enter your name: ").strip()
            except EOFError:
                return "Guest"

            if name:
                return name
            print("Name cannot be empty.")

    def disconnect(self):
        if not self.running and self.socket is None:
            return

        self.running = False

        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None

        print("Disconnected")
