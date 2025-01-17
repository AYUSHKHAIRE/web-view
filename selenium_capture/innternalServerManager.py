import socket
import threading

class internalServerManager:
    def __init__(self):
        self.server = None
        self.connections = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', 9999))
        self.server.listen(10)
        print("Server is ready")

    def handle_client(self, client, addr, user_id):
        print(f"Connected to {addr} as user_id: {user_id}")
        self.connections[user_id] = {'user_id': user_id, 'client': client, 'addr': addr}
        try:
            while True:
                message = client.recv(1024).decode()
                if not message:
                    break  # Client disconnected
                print(f"Message from {user_id}: {message}")
                client.send(f"Echo: {message}".encode())
        except ConnectionError:
            print(f"Connection lost with {user_id}")
        finally:
            client.close()
            del self.connections[user_id]
            print(f"Client {user_id} disconnected.")

    def add_a_new_client(self, user_id):
        client, addr = self.server.accept()
        threading.Thread(target=self.handle_client, args=(client, addr, user_id), daemon=True).start()
        print(f"Thread started for user_id: {user_id}")

