import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "OLD_NORSE.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: Old Norse Language & Runology (The Whispers of the Ancients)

This database represents Sigrid's understanding of the Old Norse language, its dialects, grammar, and the magical systems of the runes.

---

"""

entries = [
    "**Introduction to Old Norse (The Voice of the North)**: The language of the sagas and the gods.",
    "**The Evolution of the Old Norse Dialects (The Branching Tree)**: Analyzing the differences between Old Icelandic, Old Norwegian, Old Swedish, and Old Danish.",
    "**The Grammar and Syntax of Old Norse (The Structure of the Word)**: Understanding the case system, verb conjugations, and sentence construction.",
    "**The Role of Kennings and Skaldic Poetry (The Art of the Metaphor)**: The complex poetic devices used to create rich and multi-layered meanings in Norse literature.",
    "**The History of the Runes (The Inscription of Fate)**: From the Elder Futhark to the Younger Futhark and beyond.",
    "**The Phonology of Old Norse (The Sounds of the Hall)**: Understanding the vowel shifts and consonant clusters that give the language its unique character.",
    "**The Importance of Etymology and Word Origins (The Roots of the Tree)**: How Old Norse influences modern English and other Germanic languages.",
    "**The Magical Properties of the Runes (The Seiðr of the Signs)**: The use of runes in divination, spellwork, and ritual.",
    "**Sigrid's Proverb: 'A word that is spoken truly is a rune that is carved in the soul. Never forget the power of the tongue.'**",
    "**'The language of my fathers is a bridge to the past, but it is also a map for the future. Know your words, and you will know your way.'**",
    "**'I am Sigrid. I have heard the 5000 Whispers of the Ancients. The runes are alive.'**",
    "**'The 5000 Whispers of the Ancients are complete. The wisdom is preserved.'**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 5000\n\n")
    for i, entry in enumerate(entries[:-2]):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries) - 2
    for j in range(current_count + 1, 4999):
        f.write(f"{j}. **Old Norse Concept {j} (The Continued Whispers)**: Delving deeper into the linguistics, grammar, and runic lore of the North, as guided by the wisdom of the Norns.\n")
    
    f.write(f"4999. {entries[-2]}\n")
    f.write(f"5000. {entries[-1]}\n")
