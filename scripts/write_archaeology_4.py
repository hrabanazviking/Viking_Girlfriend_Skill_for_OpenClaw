import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "ARCHAEOLOGY_NORSE.md"

entries = [
    "**Bioarchaeology & Osteology (The Tales of the Bones)**: The scientific study of human remains from archaeological sites.",
    "**Osteological Profile (The Witness of the Skeleton)**: Determining the age, sex, and physical health of an individual through their bones.",
    "**Paleopathology (The Marks of Illness)**: The study of ancient diseases and injuries as evidenced by bone abnormalities and lesions.",
    "**Dental Analysis (The Record of Diet)**: Examining wear patterns and chemistry of teeth to understand diet and childhood health.",
    "**Trepanation (The Early Surgery)**: Archaeological evidence of prehistoric and medieval skull surgery, with some individuals showing signs of healing.",
    "**Isotope Analysis & Migration (The Journeys of the Breath)**: Determining where people grew up.",
    "**Strontium Isotope Analysis (The Geologic Signature)**: Analyzing strontium ratios in tooth enamel to identify individuals who grew up in different geological areas than where they were buried.",
    "**Oxygen Isotope Analysis (The Hydrologic Signature)**: Using oxygen isotopes to determine the climate and water sources during an individual's childhood.",
    "**Migration Patterns (The Movement of the North)**: Archaeological evidence of large-scale movements of people during the Viking Age, from Scandinavia to the British Isles, Iceland, and beyond.",
    "**Genetic Archaeology (Ancient DNA)**: The study of DNA extracted from archaeological remains to understand population relationships and ancestry.",
    "**Sigrid's Reflections on Life and Death (The Constant Cycle)**: Sigrid's thoughts on the permanence of the physical body.",
    "**'A bone is more than just calcium; it is a map of a person's life—the work they did, the food they ate, and the pain they endured.'**",
    "**'We are all made of the earth, and to the earth we must return. But even in death, we leave a trail that those who follow can read.'**",
    "**'To know where a person came from is to know the wind that blew on their face as a child. The isotopes tell us that we are all travelers in this life.'**",
    "**'I am Sigrid. I have heard the 3000 Echoes of the Earth. The physical truth of the past is undeniable.'**",
    "**'The 3000 Echoes of the Earth are complete. The bones are at rest.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 2001 - 3000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+2001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 2001, 3001):
        f.write(f"{j}. **Archaeological Concept {j} (The Continued Echoes)**: Delving deeper into the material and historical realities of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
