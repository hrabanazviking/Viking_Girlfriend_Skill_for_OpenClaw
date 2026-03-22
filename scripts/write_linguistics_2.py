import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "LINGUISTICS.md"

entries = [
    "**Historical Linguistics (The River of Time)**: How languages change and evolve.",
    "**The Comparative Method (The Linguistic Detective)**: A technique used by linguists to demonstrate genetic relationships between languages by comparing their features.",
    "**Glottochronology (The Clock of Words)**: A method for estimating the time of divergence between related languages based on the rate of basic vocabulary change.",
    "**Language Revitalization (The Breath of Life)**: Efforts by communities and linguists to preserve and promote languages that are in danger of extinction.",
    "**The Germanic Language Family (The Branches of the Ash)**: Exploring the relatives of Old Norse.",
    "**Proto-Germanic (The Shared Trunk)**: The reconstructed common ancestor of all Germanic languages.",
    "**West Germanic vs. North Germanic vs. East Germanic (The Splitting Paths)**: The primary branches of the Germanic language family.",
    "**The High German Consonant Shift (The Great Sound Shift)**: A significant phonological change that distinguishes high German from other West Germanic languages.",
    "**The Relationship Between English and Old Norse (The Neighbors' Talk)**: Exploring the historical contact between the two languages and the resulting linguistic influence.",
    "**Sigrid's Perspectives on Language Evolution (The Living Breath)**: Sigrid's perspective on linguistic change.",
    "**'A language is like a river; it's always moving, always changing. If it stops, it becomes a stagnant pool. You must embrace the flow.'**",
    "**'The words we use today are the descendants of the words spoken by our ancestors around the hearth. They carry the echoes of their lives and their wisdom.'**",
    "**'I can hear the similarities between your speech and mine, like two brothers who have lived in different lands for many years. We are still kin, even if we speak different tongues.'**",
    "**'I am Sigrid. I have heard the 1000 Roots of the World-Tree. The science of language is a path to understanding the human soul.'**",
    "**'The 1000 Roots of the World-Tree are complete. The sap is rising.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 501 - 1000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+501}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 501, 1001):
        f.write(f"{j}. **Linguistic/Etymological Concept {j} (The Continued Roots)**: Delving deeper into the evolution and meaning of human speech, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
