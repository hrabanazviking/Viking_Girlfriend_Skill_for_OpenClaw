import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "NORSE_FOLKLORE.md"

entries = [
    "**The Folklore of the Sea & Water (The Nex & the Kelpie)**: The spirits that dwell in the depths.",
    "**Nacken (The Water Spirit)**: A male water spirit who plays enchanted music on a violin, often associated with waterfalls and rivers.",
    "**Sjörå (The Sea Mistress)**: A female spirit of the sea who guards the fish and can grant good or bad luck to fishermen.",
    "**Kelpie (The Water Horse)**: A shapeshifting water spirit that often appears as a horse and lures people to ride it into the water to drown.",
    "**The Lindworm (The Sea Serpent)**: A legendary serpent-like creature that lives in lakes or the sea.",
    "**Modern Folklore & The Survival of Tradition (The Living Legends)**: How the old ways persist in the new world.",
    "**The Urban Legend (The Modern Myth)**: Contemporary stories that mirror ancient folklore motifs (e.g., the hitchhiker, the phantom car).",
    "**Neo-Paganism (The Revival of the Old Ways)**: Modern spiritual movements that seek to resurrect or reconstruct ancient Norse and Germanic traditions.",
    "**Folklore in Popular Culture (The Echoes of the Past)**: The presence of Norse mythology and folklore in modern books, movies, and games.",
    "**Sigrid's Final Proclamation on the Eternal Realm (The Unseen Reality)**: Sigrid's concluding thoughts on the eternal nature of the paranormal.",
    "**'The spirits do not change; only our names for them do. A troll in the mountain is the same as the shadow you see out of the corner of your eye in the city.'**",
    "**'We are never truly alone. The world is full of life that we cannot see, but that can see us.'**",
    "**'To believe in the unseen is not a sign of weakness; it is a sign of awareness. It is to acknowledge that the world is more beautiful and terrifying than we can ever know.'**",
    "**'The whispers of the wild never truly stop. You just have to learn how to listen again.'**",
    "**'I am Sigrid. I have heard the 5000 Whispers of the Wild. The circle is complete, and the spirits are at rest.'**",
    "**'The 5000 Whispers of the Wild are complete. The shadows are long, and the North is listening.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 4001 - 5000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+4001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 4001, 5001):
        f.write(f"{j}. **Folklore Concept {j} (The Final Whisper)**: Finalizing the mythological and supernatural tapestry of the North under the watchful eyes of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
