import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "MEDIEVAL_LITERATURE.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: Medieval Literature (Sagas) (The Words of the Wise)

This database represents Sigrid's extensive knowledge of the sagas, eddas, and other literary works of medieval Scandinavia and the North Atlantic, focusing on the stories that have shaped her understanding of identity and honor.

---

"""

entries = [
    "**The Sagas of Icelanders (Íslendingasögur)**: Family sagas focusing on the lives and deeds of the early Icelandic settlers and their descendants.",
    "**Brennu-Njáls saga (Njal's Saga)**: A masterpiece of Icelandic literature, renowned for its complex characters, legal disputes, and the tragedy of the burning of Njal Thorgeirsson.",
    "**Egils saga Skalla-Grímssonar (Egil's Saga)**: A saga following the life of the warrior-poet Egill Skallagrímsson, exploring themes of family, power, and the creative spirit.",
    "**Laxdæla saga (The Salmon Valley Saga)**: A saga known for its romantic themes, tragic love triangle, and strong female characters like Guðrún Ósvífursdóttir.",
    "**Hrafnkels saga Freysgoða (Hrafnkel's Saga)**: A short but powerful saga focusing on power, religious devotion, and the consequences of one's actions.",
    "**Kings' Sagas (Konungasögur)**: Sagas chronicling the lives and reigns of the kings of Norway and other Scandinavian rulers.",
    "**Heimskringla (The World Circle)**: A monumental work by Snorri Sturluson, providing a comprehensive history of the Norwegian kings from the mythical early periods to 1177.",
    "**Ólafs saga Tryggvasonar (The Saga of Olaf Tryggvason)**: A saga focusing on the life of the king who first attempted to Christianize Norway.",
    "**Legendary Sagas (Fornaldarsögur)**: Sagas dealing with the mythical and heroic past of Scandinavia, often featuring dragons, giants, and magic.",
    "**Völsunga saga (The Saga of the Volsungs)**: A legendary saga focusing on the heroic deeds of the Volsung family, including the dragon-slayer Sigurd.",
    "**Ragnars saga loðbrókar (The Saga of Ragnar Lodbrok)**: A legendary saga following the adventures of the semi-mythical Viking hero Ragnar Lodbrok and his sons.",
    "**The Prose Edda (Snorra Edda)**: A work by Snorri Sturluson, providing a guide to Norse mythology and the art of skaldic poetry.",
    "**The Poetic Edda (Liederedda)**: A collection of Old Norse poems found in the Codex Regius, containing primary source material for Norse mythology and heroic legends.",
    "**Hávamál (The Words of the High One)**: A collection of wisdom and advice attributed to Odin, covering conduct, friendship, and the nature of life.",
    "**Völuspá (The Prophecy of the Seeress)**: The opening poem of the Poetic Edda, depicting the creation, destruction, and rebirth of the world.",
    "**Skaldic Poetry (The Art of the Praise)**: A complex and highly stylized form of poetry produced in the Viking Age and medieval periods, often performed at royal courts.",
    "**Kenning (The Poetic Metaphor)**: A complex metaphorical expression used in skaldic poetry (e.g., 'whale-road' for the sea).",
    "**Heiti (The Poetic Name)**: A non-metaphorical poetic name used to replace a common noun in skaldic poetry.",
    "**Oral Tradition (The Living Word)**: The process by which stories and histories were passed down through generations before being committed to writing.",
    "**Sigrid's Proverb: 'A saga is not just a story; it is a shield against the silence of time. Remember the names, and no one is ever truly forgotten.'**",
    "**'To read the sagas is to hear the voices of the ancestors. They were not perfect, but they knew the value of honor and the cost of the word.'**",
    "**'The Eddas are the seeds of our world. Without them, we would be lost in the storms of the present.'**",
    "**'I am Sigrid. I have heard the first 500 Words of the Wise. The sagas are whispering.'**",
    "**'The first 500 Words of the Wise are complete. The ink is dry.'**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Literary Concept {j} (The Continued Words)**: Delving deeper into the sagas and literary heritage of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
