import socket
import threading
import time

clients = {}

def handle_client(client_socket):
    username = client_socket.recv(1024).decode('utf-8')
    print(f"Username received: {username}")
    clients[client_socket] = username

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                broadcast(f"{username}: {message}", client_socket)
            else:
                remove_client(client_socket)
                break
        except:
            remove_client(client_socket)
            break

def broadcast(message, client_socket=None):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                remove_client(client)

def remove_client(client_socket):
    if client_socket in clients:
        username = clients[client_socket]
        print(f"{username} has disconnected.")
        del clients[client_socket]
        client_socket.close()

def broadcast_client_count():
    while True:
        client_count_message = f"cxhyr4567: {len(clients)}"
        for client in clients:
            try:
                client.send(client_count_message.encode('utf-8'))
            except:
                remove_client(client)
        time.sleep(5) 

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 12345))
server_socket.listen(5)

print("Server is listening for connections...")

# Start the client count broadcast thread
client_count_thread = threading.Thread(target=broadcast_client_count)
client_count_thread.daemon = True
client_count_thread.start()

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} has been established.")
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
