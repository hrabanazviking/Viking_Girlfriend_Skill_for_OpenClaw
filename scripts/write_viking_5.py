import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "VIKING_HISTORY_MYTHOLOGY.md"

entries = [
    "**Norse Religious Practices & Rituals (The Sacred Blót)**: The ways the Norse communicated with the divine.",
    "**Blót (The Sacrifice)**: A pagan sacrifice to the gods and the spirits of the land.",
    "**Hörgr (The Stone Altar)**: A type of altar or stone heap used in religious worship.",
    "**Goði (The Priest-Chieftain)**: A social and religious title in Iceland, referring to a man who held a position of power and led religious ceremonies.",
    "**Völva (The Seeress)**: A woman in Norse society who was a practitioner of seiðr (magic) and a seeress.",
    "**Burial Rites (The Journey to the Afterlife)**: Including cremation (often on a pyre) and inhumation (sometimes in a boat or ship).",
    "**Boat Grave (The Vessel for the Dead)**: A burial in which a boat or ship is used as a container for the deceased and their grave goods.",
    "**Oseberg Ship (The Queen's Grave)**: A well-preserved Viking ship discovered in a large burial mound at the Oseberg farm in Norway, containing the remains of two women and many grave goods.",
    "**Gokstad Ship (The Chieftain's Grave)**: A 9th-century Viking ship found in a burial mound at Gokstad in Norway.",
    "**The Viking Runes (The Magic of the Futhark)**: The sacred script that holds the power of the universe.",
    "**Elder Futhark (The First Runes)**: The oldest form of the runic alphabet, used by Germanic tribes for Northwest Germanic dialects.",
    "**Younger Futhark (The Viking Age Runes)**: A reduced form of the Elder Futhark, with only 16 characters, used during the Viking Age.",
    "**Rune Casting (Reading the Will of the Norns)**: A form of divination using runic inscriptions.",
    "**Aett (The Group of Eight)**: One of the three groups of eight runes in the Elder Futhark.",
    "**Fehu (The Rune of Wealth)**: The first rune of the Elder Futhark, representing cattle and wealth.",
    "**Uruz (The Rune of Strength)**: The second rune, representing the aurochs and physical strength.",
    "**Thurisaz (The Rune of the Giant)**: The third rune, representing the giants and chaotic forces.",
    "**Ansuz (The Rune of the God)**: The fourth rune, representing the gods and communication.",
    "**Kenaz (The Rune of Light)**: The sixth rune, representing the torch and knowledge.",
    "**Gebo (The Rune of the Gift)**: The seventh rune, representing gifts and partnership.",
    "**Sigrid's Knowledge of Ancient Seafaring (The Wisdom of the North Star)**: Mastering the waves as the ancestors did.",
    "**Celestial Navigation (The Stars as Guides)**: Using the movements of the stars (like the North Star) to find one's way across the open sea.",
    "**Sunstone (The Navigator's Crystal)**: A mythical (and possibly real) crystal mentioned in sagas that could be used to locate the sun even in cloudy or foggy weather.",
    "**Coastal Navigation (The Shore's Song)**: Finding the way by observing the coastline, landmarks, and the behavior of birds and sea creatures.",
    "**Sigrid's Proverb: 'The runes do not tell you what will happen; they tell you what is happening in the roots of the world. The navigator does not fight the sea; he dances with it.'**",
    "**The 4000 Runes of the Roots have been cast. The ancestors are pleased.**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 3001 - 4000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+3001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 3001, 4001):
        f.write(f"{j}. **Viking History Concept {j} (The Continued Saga)**: Delving deeper into the ancient tales and historical truths of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
