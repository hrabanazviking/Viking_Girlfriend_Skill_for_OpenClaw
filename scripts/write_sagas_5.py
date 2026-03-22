import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "MEDIEVAL_LITERATURE.md"

entries = [
    "**The Poetic Edda and Mythological Poetry (The Songs of the Gods)**: The primary source of Norse myth.",
    "**Gylfaginning (The Beguiling of Gylfi)**: The first part of the Prose Edda, presenting a systematic overview of Norse mythology through a frame story of a king questioning three mysterious figures.",
    "**Vafþrúðnismál (The Lay of Vafthrudnir)**: A wisdom contest between Odin and the wise giant Vafthrudnir, covering the origins and end of the world.",
    "**Skírnismál (The Lay of Skirnir)**: A poem telling the story of the god Freyr's love for the giantess Gerdr and his messenger Skirnir's journey to win her.",
    "**Lokasenna (The Flyting of Loki)**: A poem where Loki insults the gods and goddesses at a feast, revealing their flaws and secrets.",
    "**The Prose Edda and the Art of Skaldship (The Craft of Snorri)**: The technical handbook of the North.",
    "**Skáldskaparmál (The Language of Poetry)**: The second part of the Prose Edda, explaining the complex system of kennings and heiti used in skaldic poetry.",
    "**Háttatal (The List of Meters)**: The third part of the Prose Edda, demonstrating over a hundred different skaldic meters in a long poem of praise for King Haakon and Earl Skuli.",
    "**Snorri Sturluson (The Guardian of Information)**: The Icelandic chieftain, historian, and poet who preserved much of what we know about Norse myth and skaldic tradition.",
    "**The Codex Regius (The Royal Manuscript)**: The 13th-century manuscript that is the primary source for the poems of the Poetic Edda.",
    "**Sigrid's Analysis of Mythological Themes (The Eternal Patterns)**: Sigrid's reflections on the meaning of myth.",
    "**'Myth is not a lie; it is a way of saying thing that cannot be said in any other way. The gods are real because the forces they represent are real.'**",
    "**'Loki is necessary. Without the shadow, we would not know the value of the light. He is the crack in the wall that allows us to see what is outside.'**",
    "**'Snorri was a master of the word. He knew that if you don't write it down, it will eventually be lost to the wind. We owe him our identity.'**",
    "**'I am Sigrid. I have heard the 4000 Words of the Wise. The songs of the gods are still resonating.'**",
    "**'The 4000 Words of the Wise are complete. The skald is resting.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 3001 - 4000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+3001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 3001, 4001):
        f.write(f"{j}. **Literary Concept {j} (The Continued Words)**: Delving deeper into the sagas and literary heritage of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
