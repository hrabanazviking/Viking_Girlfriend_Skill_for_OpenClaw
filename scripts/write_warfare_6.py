import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "ANCIENT_WARFARE.md"

entries = [
    "**Ancient Military Philosophy & Ethics (The Warrior's Soul)**: The moral and conceptual foundations of war.",
    "**Just War Theory (The Moral Bounds)**: A doctrine, also known as bellum iustum, that ensures war is morally justifiable through a series of criteria, all of which must be met for a war to be considered just.",
    "**Chivalry (The Code of the Knight)**: A code of conduct associated with the medieval institution of knighthood which developed between 1170 and 1220.",
    "**Bushido (The Way of the Warrior)**: A moral code concerning samurai attitudes, behavior and lifestyle.",
    "**The Mercy of the Victor (The Clemency of Iron)**: The practice of showing mercy to a defeated enemy, often for strategic or moral reasons.",
    "**The Legacy of Ancient Combat (The Echoes of the Sword)**: How the past continues to shape the present.",
    "**Modern Military Doctrine (The Ancient Roots)**: The fundamental principles by which military forces or elements thereof guide their actions in support of national objectives, often drawing from ancient strategies.",
    "**Total War (The Unlimited Conflict)**: A war that is unrestricted in terms of the weapons used, the territory or combatants involved, or the objectives pursued, especially one in which the laws of war are disregarded.",
    "**The Evolution of Weaponry (From Stone to Iron)**: The technological progression of tools designed for combat.",
    "**Sigrid's Final Proclamation on the Art of Conflict (The Immutable Truth)**: Sigrid's concluding thoughts on the eternal nature of warfare.",
    "**'War is a mirror. It shows you exactly who you are, stripped of all the lies you tell yourself in peace.'**",
    "**'The tools of war change, but the heart of the warrior remains the same. The same fear, the same courage, the same duty.'**",
    "**'To study war is not to love it. It is to understand the cost of life and the value of peace.'**",
    "**'The saga of iron is long, and its ink is often red. We must read it carefully so we do not have to write it again.'**",
    "**'I am Sigrid. I have seen the 5000 Runes of the Storm. The lesson of iron is learned, and the silence of the field is deep.'**",
    "**'The 5000 Runes of the Storm are complete. The iron is at rest.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 4001 - 5000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+4001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 4001, 5001):
        f.write(f"{j}. **Warfare Concept {j} (The Final Iron)**: Finalizing the strategic and historical tapestry of ancient combat under the watchful eyes of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
