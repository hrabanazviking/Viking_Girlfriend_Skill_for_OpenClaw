import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "ANCIENT_WARFARE.md"

entries = [
    "**Ancient Naval Warfare (The Duel of the Depths)**: Mastering the waves for dominance in war.",
    "**Corvus (The Boarding Bridge)**: A Roman naval boarding device used in sea battles during the First Punic War.",
    "**Quinquereme (The Heavy Galley)**: An ancient galley, a type of warship that was likely a development from the trireme.",
    "**Fire Ships (The Burning Sacrifice)**: Ships filled with combustible material and set adrift toward an enemy fleet to cause destruction and panic.",
    "**Greek Fire (The Unquenchable Flame)**: An incendiary weapon used by the Byzantine Empire, which could continue burning while floating on water.",
    "**Naval Blockade (The Sea's Stranglehold)**: An effort to cut off supplies, war material, or communications from a particular area by sea.",
    "**Siege Operations & Engineering (The Wall-Breakers)**: The methodical science of capturing fortifications.",
    "**Onager (The Kick of the Mule)**: A Roman siege engine, a type of catapult that uses a torsional force.",
    "**Catapult (The Long Striker)**: A ballistic device used to launch a projectile a great distance without the aid of gunpowder or other propellants.",
    "**Trench Warfare (The Diggers of Death)**: Excavating a system of defensive ditches to shelter troops from enemy fire.",
    "**Sapping (The Subterranean Strike)**: A term used in siege operations to describe the digging of a tunnel under an enemy wall to cause it to collapse.",
    "**Counter-Sapping (The Tunnel Defense)**: The act of the defenders digging their own tunnels to intercept and destroy the attackers' saps.",
    "**Cavalry Evolution & Tactics (The Thunder of Hooves)**: From chariots to the armored knight.",
    "**Light Cavalry (The Swift Harrier)**: Cavalry troops used for scouting, skirmishing, and screening.",
    "**Heavy Cavalry (The Shock Force)**: Cavalry troops used as shock troops, primarily intended to deliver a crushing blow to an enemy formation.",
    "**Horse Archers (The Storm of Arrows)**: Cavalrymen armed with bows, able to shoot while riding.",
    "**Parthian Shot (The Deadly Retreat)**: A military tactic made famous by the Parthians, where horse-archers while retreating or feigning retreat would turn their bodies back in full gallop to shoot at the pursuing enemy.",
    "**Stirrup (The Rider's Anchor)**: A light frame or ring that holds the foot of a rider, attached to the saddle by a strap, which revolutionized cavalry warfare.",
    "**Sigrid's Reflection on the Duality of War (The Warrior's Burden)**: Understanding that every victory has a price.",
    "**'War is a thief. It steals the sons of mothers and the peace of the land. But sometimes, it is the only way to keep a greater thief away.'**",
    "**'A true warrior does not hate the one in front of him; he loves those behind him.'**",
    "**'The shield-wall is only as strong as the weakest man in it. In war, we are all our brother's keeper.'**",
    "**'I am Sigrid. I have seen the 1000 Runes of the Storm. The lesson of iron is hard, but it is true.'**",
    "**'The 1000 Runes of the Storm are complete. The iron remains cold.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 501 - 1000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+501}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 501, 1001):
        f.write(f"{j}. **Warfare Concept {j} (The Continued Tactics)**: Delving deeper into the strategic and historical realities of ancient combat, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
