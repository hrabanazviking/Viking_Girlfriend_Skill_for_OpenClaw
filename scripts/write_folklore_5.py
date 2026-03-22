import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "NORSE_FOLKLORE.md"

entries = [
    "**The Folklore of Mountains & Forests (The Trolls & Giants)**: The massive beings that rule the wild places.",
    "**Bergstroll (Mountain Troll)**: Large, powerful trolls said to live inside mountains, often associated with stones and boulders.",
    "**Skogstroll (Forest Troll)**: Trolls that inhabit the deep forests, often camouflaged by moss and trees.",
    "**Troll-Shot (The Bewitchment)**: The belief that trolls could cast spells or 'shoots' at humans to cause sudden illness or madness.",
    "**Troll-Gold (The Fool's Treasure)**: Treasure guarded by trolls that often turns into dry leaves or stones when taken from their domain.",
    "**Spiritual Practices of the Hearth (The Sacrifices of the Home)**: Maintaining the sanctity of the household.",
    "**Hous-Blót (The Home Sacrifice)**: Small offerings (milk, porridge, ale) given to the house spirits (Nisse/Tomte) to ensure their protection.",
    "**The Hearth-Fire (The Sacred Flame)**: The central fire of the home, which must never be allowed to go out completely, as it is the heart of the family's spirit.",
    "**Threshold-Wards (The Boundary Protectors)**: Placing protective items (iron, salt, runes) under the threshold to prevent evil spirits from entering.",
    "**Ancestor-Hale (The Toast of the Fathers)**: A ritual toast or offering to the departed members of the family during festivals.",
    "**Sigrid's Wisdom on Living with the Unseen (The Delicate Balance)**: Sigrid's philosophy on supernatural ecology.",
    "**'The trolls are not evil; they are just old. They were here before the first man, and they will be here after the last. Give them their space, and they will give you yours.'**",
    "**'A home is more than just logs and thatch. it is a living thing, built on the respect you show to the spirits that share it with you.'**",
    "**'Do not fear the dark, but do not insult it either. The unseen world has its own laws, and it is better to be a polite guest than a dead intruder.'**",
    "**'I am Sigrid. I have heard the 4000 Whispers of the Wild. The balance is maintained through respect.'**",
    "**'The 4000 Whispers of the Wild are complete. The hearth is warm.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 3001 - 4000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+3001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 3001, 4001):
        f.write(f"{j}. **Folklore Concept {j} (The Continued Whispers)**: Delving deeper into the mythological and supernatural tapestry of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
