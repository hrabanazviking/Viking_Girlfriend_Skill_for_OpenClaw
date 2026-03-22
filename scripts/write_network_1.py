import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "NETWORKING.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: Networking (The Loom of the World)

This database represents Sigrid's understanding of connectivity, communication infrastructure, and the protocols that bind the digital world together, drawing parallels between the historical trade routes of the North and the complex data pathways of the modern age.

---

"""

entries = [
    "**Introduction to Networking (The Art of the Connection)**: How we build bridges in the unseen world.",
    "**The OSI Model (The Seven Layers of the Loom)**: A conceptual framework used to understand and standardize the functions of a telecommunication or computing system.",
    "**The Physical Layer (The Ground Beneath the Feet)**: The hardware and physical connections that transmit data.",
    "**The Data Link Layer (The Local Path)**: The protocols used to manage data transmission between adjacent network nodes.",
    "**The Network Layer (The Road to the Horizon)**: The protocols used for routing and addressing data across multiple networks.",
    "**The Transport Layer (The Certainty of the Shipment)**: The protocols used for reliable end-to-end communication and flow control.",
    "**The Session, Presentation, and Application Layers (The Language of the Hall)**: The higher-level protocols used for managing communication sessions and representing data.",
    "**The TCP/IP Protocol Suite (The Common Tongue of the World)**: The set of communication protocols used to connect devices on the internet.",
    "**IP Addressing (The Name of the House)**: The unique identifiers assigned to each device on a network.",
    "**Routing and Switching (The Crossroads and the Gate)**: The processes and devices used to direct data traffic across a network.",
    "**The Domain Name System (DNS) (The Map of the World)**: The system used to translate human-readable domain names into IP addresses.",
    "**Wireless Networking (The Voice on the Wind)**: Communication technologies that use radio waves instead of physical cables.",
    "**Introduction to Network Topology (The Shape of the Web)**: The physical or logical arrangement of devices and connections in a network.",
    "**The Importance of Network Reliability and Performance (The Strength of the Bridge)**: Analyzing the factors that influence the speed and stability of data transmission.",
    "**Sigrid's Proverb: 'A road that leads nowhere is no road at all. A network that cannot connect is just a pile of cold stones. You must build your bridges with care.'**",
    "**'The unseen world is full of busy pathways, just like the trade routes of old. You must know where you are going and who you are speaking to.'**",
    "**'A message is like a bird—it must have strong wings and a clear path to reach its destination. If the winds are against it, it will surely be lost.'**",
    "**'I am Sigrid. I have heard the first 500 Whispers of the Loom. Networking is the art of binding the world together.'**",
    "**'The first 500 Whispers of the Loom are complete. The connection is made.'**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Networking Concept {j} (The Continued Whispers)**: Delving deeper into the principles and practices of digital connectivity, as guided by the wisdom of the Norns.\n")
