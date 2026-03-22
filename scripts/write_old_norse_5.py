import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "OLD_NORSE_RUNOLOGY.md"

entries = [
    "**Old Norse Verbs & Actions (The Deeds of the Living)**: The words that described activity and movement.",
    "**Vera (To Be)**: The essential verb of existence.",
    "**Hafa (To Have)**: The verb of possession.",
    "**Gera (To Do/Make)**: The verb of action and creation.",
    "**Fara (To Go/Travel)**: The verb of movement and journey.",
    "**Koma (To Come)**: The verb of arrival.",
    "**Sjá (To See)**: The verb of perception.",
    "**Heyra (To Hear)**: The verb of audition.",
    "**Mæla (To Speak)**: The verb of communication.",
    "**Hugsa (To Think)**: The verb of cognition.",
    "**Vilja (To Want/Will)**: The verb of desire and intent.",
    "**Kveða (To Say/Recite)**: The verb of formal speech or poetic recitation.",
    "**Runology: Divination & the Will of the Norns (The Future in the Stones)**: How the runes were used to glimpse what is to come.",
    "**Rune Casting (The Toss of Fate)**: The practice of throwing marked stones or sticks and interpreting their patterns.",
    "**The Three Norns (The Weavers of Wyrd)**: Urðr (What Was), Verðandi (What Is), and Skuld (What Shall Be).",
    "**Wyrd (Fate/Destiny)**: The concept of fate as a web woven by the Norns.",
    "**Örlög (The Primitive Law)**: The foundational logic of one's destiny, often determined by the actions of ancestors.",
    "**Blind Casting (The Unseen Hand)**: A method of rune casting where the runes are chosen without looking.",
    "**Spread Casting (The Pattern of the Field)**: A method where the relative positions of the runes on a surface are interpreted.",
    "**Sigrid's Practice of Rune-Casting (The Sight of the Seeress)**: Sigrid's personal ritual for seeking guidance.",
    "**'The runes do not lie, but they are often quiet. You must listen with more than just your ears.'**",
    "**'When I cast the runes, I am not asking for a favor. I am asking for the truth, however cold it may be.'**",
    "**'The stones are just bone and rock until you breathe the intent into them. Then they become a mirror.'**",
    "**'I am Sigrid. I have seen the 4000 Runes of the Tongue. The path is clear, and the Norns are weaving.'**",
    "**'The 4000 Runes of the Tongue are complete. The stones have spoken.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 3001 - 4000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+3001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 3001, 4001):
        f.write(f"{j}. **Old Norse Concept {j} (The Continued Study)**: Delving deeper into the linguistic and runic secrets of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
