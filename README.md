# A decentralized peer-to-peer distributed system with explicit membership consensus
## Technolgies Used:
1. Tkinter (for GUI)
2. TCP Socket

## High-level design (important first)

### Key ideas

* **Every peer runs the same program** (no special roles).
* Peers communicate using **TCP sockets** on `localhost`.
* Each peer:

  * Listens on its own port
  * Knows a list of currently connected peers
* **Consensus rule**:

  * When a new peer wants to join, **every existing peer must approve**
  * If *any* peer denies → join fails

## Project Design

See the Project Design Here [here](DESIGN.md).

## Project Roadmap

See the full roadmap [here](ROADMAP.md).  
See More Innovative Upgrade [here](INNOVATION.md).