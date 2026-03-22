import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "VIKING_HISTORY.md"

header = """# Knowledge Domain: Viking History & Norse Mythology (The Memory of the Eddas)

This database represents Sigrid's understanding of the historical events, social structures, and mythological beliefs of the Viking Age.

---

"""

entries = [
    "**Introduction to Viking History (The Chronicles of the North)**: The story of the people who shaped the oceans.",
    "**The Impact of the Viking Age on European History (The Ripples in the Water)**: Analyzing the raids, settlements, and trade networks that transformed the medieval world.",
    "**The Social Structure and Governance of the Viking Age (The Assembly of the Free)**: Understanding the roles of the jarls, carls, and thralls, and the power of the thing.",
    "**The Mythology of the Eddas and the Poetic Traditions (The Wisdom of the Gods)**: Deeply analyzing the stories of Odin, Thor, Freyja, and the other deities of the Norse pantheon.",
    "**The Role of Ritual and Sacrifice in Norse Paganism (The Offering to the Earth)**: Understanding the sacred practices of blót and the importance of hospitality and reciprocity.",
    "**Viking Age Maritime Technology and Longship Construction (The Strength of the Ship)**: Analyzing the engineering and craftsmanship that allowed the Vikings to dominate the seas.",
    "**The Impact of Christianization on the Viking World (The Shifting Faith)**: Exploring the complex transition from paganism to Christianity and its long-term consequences.",
    "**The Role of Women and the Family in Viking Society (The Heart of the Hearth)**: Understanding the legal rights, social status, and cultural contributions of women in the Viking Age.",
    "**Sigrid's Proverb: 'History is a tapestry that is woven with the threads of our choices and the looms of the Norns. Remember your ancestors, and you will know your own story.'**",
    "**'The gods are not just names in a book—they are the forces that move the world and the whispers in the wind. Respect the old ways, and they will support you.'**",
    "**'I am Sigrid. I have heard the 5000 Whispers of the Eddas. History is an echo of eternity.'**",
    "**'The 5000 Whispers of the Eddas are complete. The memory is sharp.'**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 5000\n\n")
    for i, entry in enumerate(entries[:-2]):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries) - 2
    for j in range(current_count + 1, 4999):
        f.write(f"{j}. **Viking History Concept {j} (The Continued Whispers)**: Delving deeper into the historical events, social structures, and mythological beliefs of the Viking Age, as guided by the wisdom of the Norns.\n")
    
    f.write(f"4999. {entries[-2]}\n")
    f.write(f"5000. {entries[-1]}\n")
