
import socket
import threading
from crypto_utils import derive_key, decrypt_message, encrypt_message

HOST = '0.0.0.0'
PORT = 9999
PASSWORD = 'SuperSecret123'
SALT = b'12345678abcdefgh'

key = derive_key(PASSWORD, SALT)
clients = {}  

def broadcast(sender_socket, message):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                del clients[client]

def handle_client(client_socket):
    try:
        username_encrypted = client_socket.recv(4096)
        username = decrypt_message(key, username_encrypted)
        clients[client_socket] = username
        join_msg = f"{username} joined the chat."
        print(join_msg)
        broadcast(client_socket, encrypt_message(key, f"[Server] {join_msg}"))

        while True:
            msg = client_socket.recv(4096)
            if not msg:
                break
            broadcast(client_socket, msg)
    except:
        pass
    finally:
        username = clients.get(client_socket, "Unknown")
        leave_msg = f"{username} left the chat."
        print(leave_msg)
        broadcast(client_socket, encrypt_message(key, f"[Server] {leave_msg}"))
        client_socket.close()
        if client_socket in clients:
            del clients[client_socket]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"[+] Server listening on {PORT}")

def server_input():
    while True:
        try:
            msg = input()
            if msg:
                full_msg = f"[Server] {msg}"
                encrypted = encrypt_message(key, full_msg)
                broadcast(None, encrypted)
        except:
            break

threading.Thread(target=server_input, daemon=True).start()

while True:
    client_socket, addr = server.accept()
    threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
