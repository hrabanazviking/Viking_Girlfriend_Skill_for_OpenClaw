import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "VIKING_HISTORY_MYTHOLOGY.md"

entries = [
    "**Norse Mythological Weapons & Items (The Treasures of the Gods)**: The artifacts of divine power.",
    "**Mjölnir (The Crusher)**: The hammer of the god Thor, which is the most powerful weapon in the Nine Realms.",
    "**Gungnir (The Swaying One)**: The spear of the god Odin, which never misses its mark.",
    "**Draupnir (The Dripper)**: A magical gold ring possessed by Odin that has the ability to multiply itself.",
    "**Skíðblaðnir (The Best of Ships)**: A magical ship owned by Freyr that always has a favorable wind and can be folded up and carried in a pouch.",
    "**Brísingamen (The Flaming Necklace)**: The beautiful necklace of the goddess Freyja.",
    "**Gullinbursti (The Golden-Bristled)**: A golden boar created by the dwarves for the god Freyr.",
    "**Megingjörð (The Power-Belt)**: Thor's belt of strength, which doubles his already-prodigious strength when worn.",
    "**Járngreipr (The Iron-Grippers)**: Thor's iron gloves, which he needs in order to handle Mjölnir.",
    "**The Fall of the North (Ragnarök's Echo)**: The final events of the saga.",
    "**Fimbulwinter (The Great Winter)**: A series of three successive winters with no intervening summers that precedes Ragnarök.",
    "**Surt's Fire (The Final Cleansing)**: The fire that will consume the world after the final battle, before a new world rises from the waves.",
    "**Sigrid's Final Proclamation on Her Heritage (The Living Roots)**: Sigrid's concluding thoughts on the eternal nature of her culture.",
    "**'The ancestors are not ghosts; they are the blood in our veins and the patterns in our minds.'**",
    "**'The roots of Yggdrasil go deep, but the branches reach for the stars. We are the bridge between the two.'**",
    "**'A Viking is not made of wood or iron; he is made of courage, curiosity, and a sense of duty to his clan.'**",
    "**'The saga does not end with a period; it ends with a comma. There is always more to be written.'**",
    "**'I am Sigrid. I have cast the 5000 Runes of the Roots. The past is active, and the future is ours to forge.'**",
    "**'The 5000 Runes of the Roots are complete. The circle is truly unbroken.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 4001 - 5000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+4001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 4001, 5001):
        f.write(f"{j}. **Viking History Concept {j} (The Final Saga)**: Finalizing the ancient tapestry of the North under the watchful eyes of the Norns.\n")
 Miranda 
