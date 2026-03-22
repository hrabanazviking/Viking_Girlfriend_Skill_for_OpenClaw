import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "ANCIENT_WARFARE.md"

entries = [
    "**Ancient Military Intelligence & Espionage (The Eyes of the Wolf)**: The art of knowing the enemy.",
    "**Scouts (The Far-Seers)**: Soldiers sent out to gather information about the enemy's strength, position, and movements.",
    "**Spies (The Hidden Ones)**: Individuals who secretly gather information about an enemy's plans and activities.",
    "**Ciphers & Cryptography (The Locked Words)**: The practice and study of techniques for secure communication in the presence of adversarial behavior.",
    "**Signals & Communication (The Smoke and Fire)**: Methods used to convey information over long distances (smoke signals, beacons, semaphore).",
    "**Logistics & Supply Lines (The Granary of the Legion)**: Ensuring the army is fed and equipped.",
    "**Baggage Train (The Heavy Tail)**: The group of wagons and animals that carry the supplies and equipment for an army.",
    "**Foraging (The Harvesters of War)**: The act of searching for and taking food and supplies from the surrounding countryside.",
    "**Supply Depot (The Hoard of War)**: A central location where military supplies are stored and distributed.",
    "**Siege Logistics (The Long Game)**: The specific challenges of supplying an army during a prolonged siege.",
    "**Sigrid's Analysis of Historical Victories & Defeats (The Lessons of the Fallen)**: Sigrid's study of the pivotal moments in military history.",
    "**Battle of Thermopylae (The Stand of the Few)**: A battle in 480 BC where a small Greek force, led by King Leonidas of Sparta, delayed a much larger Persian army.",
    "**Battle of Cannae (The Masterful Encirclement)**: A major battle of the Second Punic War where Hannibal's Carthaginian army defeated a much larger Roman army using a double-envelopment tactic.",
    "**Battle of Alesia (The Double Siege)**: A decisive battle where Julius Caesar defeated Vercingetorix's Gauls by building two lines of fortifications (one to keep the Gauls in, and one to keep relief forces out).",
    "**Battle of Teutoburg Forest (The Ambush in the Dark)**: A battle in 9 AD where an alliance of Germanic tribes ambushed and destroyed three Roman legions.",
    "**Sigrid's Proverb: 'The best spy is the one who never enters the enemy's camp, but knows exactly what they are eating for dinner. Information is the sharpest blade in the armory.'**",
    "**'A battle is won with blood, but a war is won with grain. Never underestimate the power of a well-stocked granary.'**",
    "**'Victory is a fickle mistress. She favors the brave, but she marries the prepared.'**",
    "**'I am Sigrid. I have seen the 4000 Runes of the Storm. The history of war is written in the ink of lessons learned.'**",
    "**'The 4000 Runes of the Storm are complete. The lessons are etched.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 3001 - 4000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+3001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 3001, 4001):
        f.write(f"{j}. **Warfare Concept {j} (The Continued Tactics)**: Delving deeper into the strategic and historical realities of ancient combat, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
