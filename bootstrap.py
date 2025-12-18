import socket
import threading

HOST = "127.0.0.1"
PORT = 4000
peers = set()  # store peer ports as strings

lock = threading.Lock()

def handle(conn):
    data = conn.recv(1024).decode()
    if data.startswith("REGISTER"):
        _, peer_port = data.split()
        with lock:
            peers.add(peer_port)
            # return list of all other peers except this one
            known_peers = [p for p in peers if p != peer_port]
        conn.sendall(",".join(known_peers).encode())
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Bootstrap server running on {HOST}:{PORT}")

while True:
    conn, _ = server.accept()
    threading.Thread(target=handle, args=(conn,), daemon=True).start()
