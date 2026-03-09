import socket
import threading
from config import DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE


class BroadcastServer:

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.server_socket = None  # Main socket that listens for incoming connections
        self.clients = []          # List of all connected client sockets
        self.client_names = {}     # Maps client socket -> display name
        self.clients_lock = threading.Lock()  # Prevents race conditions when modifying client list
        self.running = False       # Controls the main server loop

    def start(self):
        try:
            # Create a TCP/IP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Allow reuse of the address immediately after the server closes
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            # Allow up to 5 queued connections before refusing new ones
            self.server_socket.listen(5)
            self.running = True

            print(f"Server started on {self.host}:{self.port}")
            print("Waiting for clients to connect...\n")

            # Main accept loop — runs until server is stopped
            while self.running:
                try:
                    # Block until a new client connects
                    client_socket, client_address = self.server_socket.accept()
                    print(f"New client connected from {client_address}")

                    # Add new client to the shared list (thread-safe)
                    with self.clients_lock:
                        self.clients.append(client_socket)

                    # Handle each client in its own daemon thread so the
                    # main thread stays free to accept new connections
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
            # Always clean up, even if an exception is raised above
            self.shutdown()

    def handle_client(self, client_socket, client_address):
        """Manages the lifecycle of a single connected client."""
        print(f"Now listening to {client_address}")
        # Default name uses IP:port in case no name is provided
        client_name = f"{client_address[0]}:{client_address[1]}"

        try:
            # First message from the client is expected to be their name
            initial_data = client_socket.recv(BUFFER_SIZE)
            if not initial_data:
                print(f"Client {client_address} disconnected before setting a name")
                return

            initial_message = initial_data.decode("utf-8").strip()

            # Support both "/name Alice" command format and plain "Alice" name format
            if initial_message.startswith("/name "):
                provided_name = initial_message[6:].strip()
                if provided_name:
                    client_name = provided_name
            elif initial_message:
                client_name = initial_message

            # Register the client's chosen name
            with self.clients_lock:
                self.client_names[client_socket] = client_name

            print(f"Client {client_address} identified as {client_name}")
            # Notify all other clients that someone new has joined
            self.broadcast(f"* {client_name} joined the chat\n", client_socket)

            # Continuously receive messages until the client disconnects
            while self.running:
                data = client_socket.recv(BUFFER_SIZE)

                # Empty data means the client closed the connection
                if not data:
                    print(f"Client {client_name} disconnected")
                    break

                message = data.decode("utf-8").strip()

                if message:
                    print(f"Message from {client_name}: {message}")
                    # Relay the message to everyone except the sender
                    self.broadcast(f"{client_name}: {message}\n", client_socket)

        except ConnectionResetError:
            # Client disconnected abruptly without a clean close
            print(f"Client {client_name} connection reset")

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")

        finally:
            # Always clean up the client on exit, regardless of how the loop ended
            self.remove_client(client_socket)
            client_socket.close()
            # Notify remaining clients that this user has left
            self.broadcast(f"* {client_name} left the chat\n")
            print(f"Cleaned up {client_address}")

    def broadcast(self, message, sender_socket=None):
        """Sends a message to all connected clients except the sender."""
        message_bytes = message.encode('utf-8')

        # Snapshot the client list to avoid holding the lock during sending
        with self.clients_lock:
            clients_copy = self.clients[:]

        failed_clients = []  # Track clients that failed so we can remove them after

        for client in clients_copy:
            # Skip the sender — they don't need to see their own message echoed back
            if client == sender_socket:
                continue

            try:
                client.send(message_bytes)
            except Exception as e:
                print(f"Failed to send: {e}")
                failed_clients.append(client)

        # Remove and close any clients we couldn't reach
        for client in failed_clients:
            self.remove_client(client)
            try:
                client.close()
            except:
                pass

    def remove_client(self, client_socket):
        """Removes a client socket from the tracking list and name registry."""
        with self.clients_lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            if client_socket in self.client_names:
                del self.client_names[client_socket]

    def shutdown(self):
        """Gracefully stops the server and closes all open connections."""
        self.running = False
        print("Closing all client connections...")

        # Close every connected client socket
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()

        # Close the main listening socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        print("Server shutdown")
