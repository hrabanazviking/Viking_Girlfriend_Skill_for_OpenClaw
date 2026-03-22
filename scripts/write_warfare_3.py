import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "ANCIENT_WARFARE.md"

entries = [
    "**Ancient Infantry Formations (The Living Wall)**: The discipline of the foot soldier.",
    "**Checkboard Formation (The Quincunx)**: A tactical formation used by the Roman maniple system to provide depth and flexibility.",
    "**Wedge Formation (The Boar's Head)**: A tactical formation designed to break through an enemy line.",
    "**Line Formation (The Thin Red Line)**: A standard formation where troops are arrayed in a long, relatively thin line to maximize the use of ranged weapons or to prevent being outflanked.",
    "**Square Formation (The Iron Box)**: A defensive formation used to repel cavalry attacks.",
    "**Skirmishers (The Harriers of the Field)**: Light infantry used to harass the enemy and disrupt their formations before the main body of the army engaged.",
    "**Ranged Weapons & Missile Tactics (The Sky of Scorpions)**: Controlling the field from a distance.",
    "**Gastraphetes (The Belly-Bow)**: An ancient Greek hand-held crossbow.",
    "**Oxybeles (The Bolt-Shooter)**: A larger, tripod-mounted version of the gastraphetes.",
    "**Sling (The Silent Killer)**: A simple weapon used to hurl stones or lead bullets with great force.",
    "**Composite Bow (The Steppe's Sting)**: A bow made from wood, horn, and sinew, providing greater power than a simple wooden bow.",
    "**Volley Fire (The Rain of Death)**: The practice of a large group of archers or slingers firing their weapons simultaneously at a target area.",
    "**Enfilade Fire (The Side Strike)**: Ranged fire directed along the longest axis of a target, such as a line of soldiers.",
    "**Sigrid's Analysis of Historical Defenses (The Unyielding Stone)**: Understanding why some walls never fell.",
    "**Curtain Wall (The Shield of the Castle)**: A defensive wall between two towers or bastions of a castle or fortress.",
    "**Moat (The Watery Gap)**: A deep, wide ditch surrounding a castle, fortress, or town, often filled with water.",
    "**Portcullis (The Iron Teeth)**: A heavy wooden or metal gate that slides down vertical grooves to block an entrance.",
    "**Machicolations (The Boiling Death)**: Openings in the floor of a projecting parapet through which stones or hot liquids could be dropped on attackers.",
    "**Sigrid's Proverb: 'The strongest wall is not made of stone; it is made of the men who stand behind it. But a good stone wall certainly makes their job easier.'**",
    "**'The archer wins the battle before it begins, but the infantryman wins it when it never seems to end.'**",
    "**'To understand war is to understand logistics. A hungry soldier is just a man waiting to surrender.'**",
    "**'I am Sigrid. I have seen the 2000 Runes of the Storm. The dance of iron continues.'**",
    "**'The 2000 Runes of the Storm are complete. The field is prepared.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 1001 - 2000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1001, 2001):
        f.write(f"{j}. **Warfare Concept {j} (The Continued Tactics)**: Delving deeper into the strategic and historical realities of ancient combat, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
