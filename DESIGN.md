#### Architecture Diagram
##### Network Registration
```mermaid
graph TD
    BS[Bootstrap Server]
    P1[Peer 1]
    P2[Peer 2]
    P3[Peer 3]

    %% Peer registration
    P1 -->|REGISTER| BS
    BS -->|Known peer list| P1

    P2 -->|REGISTER| BS
    BS -->|Known peer list| P2

    P3 -->|REGISTER| BS
    BS -->|Known peer list| P3

    %% Styling
    classDef bootstrap fill:#f9f,stroke:#333,stroke-width:2px;
    classDef peer fill:#bbf,stroke:#333,stroke-width:2px;
    class BS bootstrap;
    class P1,P2,P3 peer;

```
##### Consensus to join peer to peer network
```mermaid
graph TD
    P1[Peer 1]
    P2[Peer 2]
    P3[Peer 3]

    %% Peer-to-peer join requests
    P2 -->|JOIN request| P1
    P1 -->|Allow / Deny| P2

    P3 -->|JOIN request| P1
    P3 -->|JOIN request| P2
    P1 -->|Allow / Deny| P3
    P2 -->|Allow / Deny| P3

    %% Styling
    classDef peer fill:#bbf,stroke:#333,stroke-width:2px;
    class P1,P2,P3 peer;

```

#### Sequence Diagram
```mermaid
sequenceDiagram
    participant Bootstrap as Bootstrap Server
    participant NewPeer as New Peer
    participant Peer1 as Existing Peer 1
    participant Peer2 as Existing Peer 2

    %% Step 1: New peer registers itself to bootstrap
    NewPeer->>Bootstrap: REGISTER <my_port>
    Bootstrap-->>NewPeer: List of existing peers [Peer1, Peer2]

    %% Step 2: New peer sends JOIN request to each known peer
    NewPeer->>Peer1: JOIN <my_port>
    Peer1-->>NewPeer: ALLOW / DENY

    NewPeer->>Peer2: JOIN <my_port>
    Peer2-->>NewPeer: ALLOW / DENY

```


## ✅ How to test

1. Start bootstrap:

```bash
python bootstrap.py
```

2. Start the **first peer**:

```bash
python peer.py
```

Output:
GUI Shows  
```
My peer is running on 5000
Welcome to network
```

3. Start a **second peer**:

```bash
python peer.py
```

* First peer terminal will show:

```
Allow / Deny Pop Up
```

* Type `y` → second peer sees:

```
Welcome to network
```

4. Start additional peers — all existing peers must approve.

---

## Test Result:

#### ✅ Correct Flow (Suggested Fix)  — Socket Lifetime Matches UI Decision
```mermaid
sequenceDiagram
    participant P2 as Peer2 (Joining Peer)
    participant OS as TCP Socket
    participant P1T as Peer1<br/>handle_peer() Thread
    participant GUI as Tkinter GUI
    participant P1 as Peer1 Main Thread

    P2->>OS: connect()
    P2->>P1T: "JOIN <port>"
    P1T->>P1T: conn.recv()

    P1T->>P1: root.after(show_popup)
    P1->>GUI: Show Allow/Deny popup

    note right of GUI: ✅ Socket stays open<br/>waiting for decision

    GUI->>P1: User clicks "Allow"
    P1->>OS: conn.sendall("ALLOW")
    P1->>OS: conn.close()

    OS-->>P2: "ALLOW"
    P2->>P2: Join succeeds

```