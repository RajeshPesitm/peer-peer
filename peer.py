import socket
import threading
import time

HOST = "127.0.0.1"
BOOTSTRAP_PORT = 4000
known_peers = set()

# ---------------------------
# Listen thread
# ---------------------------
def handle_peer(conn, addr):
    message = conn.recv(1024).decode()
    if message.startswith("JOIN"):
        new_peer_port = int(message.split()[1])
        print(f"Join request from peer {new_peer_port}")
        decision = input("Allow this peer? (y/n): ").strip().lower()
        if decision == "y":
            conn.sendall(b"ALLOW")
            known_peers.add((HOST, new_peer_port))
        else:
            conn.sendall(b"DENY")
    conn.close()

def listen(server_socket):
    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_peer, args=(conn, addr), daemon=True).start()

# ---------------------------
# Join existing peers
# ---------------------------
def join_network(peers):
    approvals = 0
    for port in peers:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((HOST, port))
            s.sendall(f"JOIN {my_port}".encode())
            response = s.recv(1024).decode()
            if response != "ALLOW":
                print(f"Join denied by peer {port}")
                return False
            approvals += 1
            known_peers.add((HOST, port))
        except ConnectionRefusedError:
            print(f"Peer {port} not reachable")
        finally:
            s.close()
    return True

# ---------------------------
# Discover peers via bootstrap
# ---------------------------
def discover_peers():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, BOOTSTRAP_PORT))
    s.sendall(f"REGISTER {my_port}".encode())
    data = s.recv(1024).decode()
    s.close()
    if data.strip() == "":
        return []
    return [int(p) for p in data.split(",")]

# ---------------------------
# Main
# ---------------------------
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, 0))  # OS picks a free port
my_port = server_socket.getsockname()[1]
server_socket.listen()

print(f"My peer is running on {my_port}")

threading.Thread(target=listen, args=(server_socket,), daemon=True).start()

# Discover existing peers
peers_to_contact = discover_peers()

if not peers_to_contact:
    print("Welcome to network")
else:
    if join_network(peers_to_contact):
        print("Welcome to network")
    else:
        print("Failed to join network")
        exit(1)

# Keep peer running
while True:
    time.sleep(1)
