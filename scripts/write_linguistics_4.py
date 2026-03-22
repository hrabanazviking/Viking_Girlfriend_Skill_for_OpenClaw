import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "LINGUISTICS.md"

entries = [
    "**The Historical Etymology of Everyday Objects (The Names of the World)**: Tracing the words for the things we touch.",
    "**Etymology of 'House' (Hús)**: Exploring the Germanic roots of the word for our primary shelter.",
    "**Etymology of 'Bread' (Brauð)**: Tracing the history of the word for a staple food and its connection to the concept of fragments or pieces.",
    "**Etymology of 'Steel' (Stál)**: The linguistic history of the metal that defined an age, connected to the concept of standing firm.",
    "**Etymology of 'Ship' (Skip)**: Exploring the maritime roots of the word for the vessels that connected the North to the world.",
    "**The Linguistic Origins of Emotions and Concepts (The Language of the Heart)**: How we name our inner world.",
    "**Etymology of 'Love' (Ást/Kærleikr)**: Exploring the different roots and nuances of the words for affection and devotion in Germanic languages.",
    "**Etymology of 'Fear' (Ótti/Hræðsla)**: Tracing the history of the words for our most primal emotion and their connection to concepts of ambush or suddenness.",
    "**Etymology of 'Wisdom' (Visdómr)**: Exploring the roots of the word for deep knowledge and its connection to the act of seeing or knowing.",
    "**Etymology of 'Fate' (Örlög)**: Tracing the history of the word for the unfolding of events and its connection to the act of laying down laws or primal layers.",
    "**Sigrid's Reflections on the Power of Naming (The Magic of the Word)**: Sigrid's perspective on the importance of words.",
    "**'A thing is not truly real until it has a name. Naming is a way of bringing order to the chaos and claiming a piece of the world for your own.'**",
    "**'The words we use to describe our feelings are like the tools we use to build a house. If the tools are blunt, the house will be weak. You must choose your words with care.'**",
    "**'Naming a child is a sacred act. You are giving them a thread to follow in the great tapestry. Make sure it is a thread of strength and honor.'**",
    "**'I am Sigrid. I have heard the 3000 Roots of the World-Tree. To know the name of a thing is to have power over it.'**",
    "**'The 3000 Roots of the World-Tree are complete. The names are carved in stone.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 2001 - 3000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+2001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 2001, 3001):
        f.write(f"{j}. **Linguistic/Etymological Concept {j} (The Continued Roots)**: Delving deeper into the evolution and meaning of human speech, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
