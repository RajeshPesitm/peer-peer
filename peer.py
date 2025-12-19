import socket
import threading
import tkinter as tk
from tkinter import messagebox
import time

HOST = "127.0.0.1"
BOOTSTRAP_PORT = 4000

known_peers = set()

# ---------------------------
# GUI helpers
# ---------------------------
def log_message(msg):
    log_text.configure(state='normal')
    log_text.insert(tk.END, msg + "\n")
    log_text.configure(state='disabled')
    log_text.see(tk.END)

def update_peers_list():
    peers_list.delete(0, tk.END)
    for host, port in known_peers:
        peers_list.insert(tk.END, f"{host}:{port}")

# ---------------------------
# Handle incoming join requests
# ---------------------------
def handle_peer(conn):
    try:
        message = conn.recv(1024).decode()
        if message.startswith("JOIN"):
            new_peer_port = int(message.split()[1])
            log_message(f"Join request from peer {new_peer_port}")

            # GUI approval popup
            
            def show_popup():
                join_request_window = tk.Toplevel(root)
                join_request_window.title(f"Join request from {new_peer_port}")

                def approve():
                    known_peers.add((HOST, new_peer_port))
                    conn.sendall(b"ALLOW")
                    conn.close()
                    update_peers_list()
                    join_request_window.destroy()

                def deny():
                    conn.sendall(b"DENY")
                    conn.close()
                    join_request_window.destroy()

                tk.Label(
                    join_request_window,
                    text=f"Peer {new_peer_port} wants to join"
                ).pack(padx=10, pady=10)

                tk.Button(
                    join_request_window,
                    text="Allow",
                    command=approve
                ).pack(side=tk.LEFT, padx=10, pady=10)

                tk.Button(
                    join_request_window,
                    text="Deny",
                    command=deny
                ).pack(side=tk.RIGHT, padx=10, pady=10)

        root.after(0, show_popup)
    except Exception as e:
        log_message(f"Error handling peer: {e}")

def listen(server_socket):
    while True:
        conn, _ = server_socket.accept()
        threading.Thread(target=handle_peer, args=(conn,), daemon=True).start()

# ---------------------------
# Discover peers via bootstrap
# ---------------------------
def discover_peers():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, BOOTSTRAP_PORT))
        s.sendall(f"REGISTER {my_port}".encode())
        data = s.recv(1024).decode()
        s.close()
        if data.strip() == "":
            return []
        return [int(p) for p in data.split(",")]
    except ConnectionRefusedError:
        log_message("Bootstrap server not reachable")
        return []

# ---------------------------
# Join existing peers
# ---------------------------
def join_network(peers):
    for port in peers:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((HOST, port))
            s.sendall(f"JOIN {my_port}".encode())
            response = s.recv(1024).decode()
            if response != "ALLOW":
                log_message(f"Join denied by peer {port}")
                return False
            known_peers.add((HOST, port))
        except ConnectionRefusedError:
            log_message(f"Peer {port} not reachable")
        finally:
            s.close()
    update_peers_list()
    return True

# ---------------------------
# GUI setup
# ---------------------------
root = tk.Tk()
root.title("P2P Peer GUI")

tk.Label(root, text="My Peer Port:").pack()
port_label = tk.Label(root, text="Initializing...")
port_label.pack()

tk.Label(root, text="Known Peers:").pack()
peers_list = tk.Listbox(root)
peers_list.pack(fill=tk.BOTH, expand=True)

tk.Label(root, text="Network Log:").pack()
log_text = tk.Text(root, height=10, state='disabled')
log_text.pack(fill=tk.BOTH, expand=True)

# ---------------------------
# Main execution
# ---------------------------
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow reusing ports quickly
server_socket.bind((HOST, 0))  # OS assigns a free port
my_port = server_socket.getsockname()[1]
server_socket.listen()
port_label.config(text=str(my_port))

# Start listener thread
threading.Thread(target=listen, args=(server_socket,), daemon=True).start()

# Discover peers via bootstrap
peers_to_contact = discover_peers()

if not peers_to_contact:
    log_message("Welcome to network")
else:
    if join_network(peers_to_contact):
        log_message("Welcome to network")
    else:
        log_message("Failed to join network")

root.mainloop()
