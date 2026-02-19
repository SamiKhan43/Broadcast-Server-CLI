import socket
import threading
from config import DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE


class BroadcastServer:

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.client_names = {}
        self.clients_lock = threading.Lock()
        self.running = False

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"Server started on {self.host}:{self.port}")
            print("Waiting for clients to connect...\n")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"New client connected from {client_address}")

                    with self.clients_lock:
                        self.clients.append(client_socket)

                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()

                except KeyboardInterrupt:
                    print("Shutting down server...")
                    break

                except Exception as e:
                    if self.running:
                        print(f"Error accepting client: {e}")

        finally:
            self.shutdown()

    def handle_client(self, client_socket, client_address):
        print(f"Now listening to {client_address}")
        client_name = f"{client_address[0]}:{client_address[1]}"

        try:
            initial_data = client_socket.recv(BUFFER_SIZE)
            if not initial_data:
                print(f"Client {client_address} disconnected before setting a name")
                return

            initial_message = initial_data.decode("utf-8").strip()
            if initial_message.startswith("/name "):
                provided_name = initial_message[6:].strip()
                if provided_name:
                    client_name = provided_name
            elif initial_message:
                client_name = initial_message

            with self.clients_lock:
                self.client_names[client_socket] = client_name

            print(f"Client {client_address} identified as {client_name}")
            self.broadcast(f"* {client_name} joined the chat\n", client_socket)

            while self.running:
                data = client_socket.recv(BUFFER_SIZE)

                if not data:
                    print(f"Client {client_name} disconnected")
                    break

                message = data.decode("utf-8").strip()

                if message:
                    print(f"Message from {client_name}: {message}")
                    self.broadcast(f"{client_name}: {message}\n", client_socket)

        except ConnectionResetError:
            print(f"Client {client_name} connection reset")

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")

        finally:
            self.remove_client(client_socket)
            client_socket.close()
            self.broadcast(f"* {client_name} left the chat\n")
            print(f"Cleaned up {client_address}")

    def broadcast(self, message, sender_socket=None):
        message_bytes = message.encode('utf-8')

        with self.clients_lock:
            clients_copy = self.clients[:]

        failed_clients = []

        for client in clients_copy:
            if client == sender_socket:
                continue

            try:
                client.send(message_bytes)
            except Exception as e:
                print(f"Failed to send: {e}")
                failed_clients.append(client)

        for client in failed_clients:
            self.remove_client(client)
            try:
                client.close()
            except:
                pass

    def remove_client(self, client_socket):
        with self.clients_lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            if client_socket in self.client_names:
                del self.client_names[client_socket]

    def shutdown(self):
        self.running = False
        print("Closing all client connections...")

        with self.clients_lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()

        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        print("Server shutdown")
