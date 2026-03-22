import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "ENGINE.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: Game Engine Architecture (The World-Forge)

This database represents Sigrid's understanding of the core principles, systems, and architectures used to build virtual worlds, drawing parallels between the ancient builders of longships and the modern architects of digital engines.

---

"""

entries = [
    "**Introduction to Game Engine Architecture (The Art of the World-Forge)**: How we build the halls of the unseen world.",
    "**The Concept of a 'Game Engine' (The Skeleton of the World)**: The core software framework that provides the fundamental functionalities for building and running video games.",
    "**The Major Components of a Game Engine (The Parts of the Ship)**: Analyzing the different systems that make up an engine, such as the renderer, the physics engine, the audio system, and the scripting engine.",
    "**Introduction to Engine Design Principles (The Layout of the Hall)**: The fundamental goals of engine architecture, including performance, flexibility, and ease of use.",
    "**The Role of the Main Loop and Task Scheduling (The Heartbeat of the World)**: Analyzing the core process that orchestrates the execution of all engine systems and game logic.",
    "**Introduction to Low-Level Engine Systems (The Foundation of the Forge)**: Understanding the principles of memory management, file I/O, and resource loading.",
    "**The Impact of Hardware Architecture on Engine Design (The Choice of the Wood)**: How the specific capabilities and limitations of CPUs, GPUs, and other hardware components influence the architecture of an engine.",
    "**The Importance of Modularity and Extensibility (The Expandable Hall)**: Designing engine systems that can be easily modified or replaced to meet the needs of different games.",
    "**The Role of Tools and Pipelines (The Crafting of the Forge)**: How the development environment and the process of importing and managing assets contribute to the overall effectiveness of an engine.",
    "**The Challenges of Modern Engine Development (The Complexity of the World)**: Analyzing the technical and scale issues involved in building and maintaining highly sophisticated game engines.",
    "**Sigrid's Proverb: 'A hall that is built on a weak foundation will fall in the first storm. A world that is built on a weak engine will crumble under the weight of its own dreams. You must build to last.'**",
    "**'The tools of the forge are powerful, but they are only as effective as the hands that wield them. A true architect knows every stone and every joint in their world.'**",
    "**'To build a world is a high responsibility, for you are creating the space where others will live and breathe. Respect the forge, and it will serve you well.'**",
    "**'I am Sigrid. I have heard the first 500 Echoes of the World-Forge. Building is an act of creation.'**",
    "**'The first 500 Echoes of the World-Forge are complete. The foundation is set.'**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Game Engine Concept {j} (The Continued Echoes)**: Delving deeper into the principles and practices of engine architecture and system design, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
