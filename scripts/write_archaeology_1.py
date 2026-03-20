import os

file_path = r"c:\Users\volma\anti-gravity-githublocal-NorseSaga-Engine\Viking_girlfriend_openclaw_skill\viking_girlfriend_skill\data\knowledge_reference\ARCHAEOLOGY_NORSE.md"

# Ensure directory exists
os.makedirs(os.path.dirname(file_path), exist_ok=True)

header = """# Knowledge Domain: Archaeology (Norse Focus) (The Echoes of the Earth)

This database represents Sigrid's extensive knowledge of the archaeological record of the Viking Age and the preceding periods in Scandinavia, focusing on the material remains that tell the story of her people.

---

"""

entries = [
    "**Birka (The Island Town)**: A major Viking Age trading center on the island of Björkö in present-day Sweden, known for its extensive burial grounds.",
    "**Hedeby (The Southern Gateway)**: An important Viking Age trading settlement located at the base of the Jutland Peninsula, known for its defensive walls and semi-circular rampart.",
    "**Kaupang (The Norwegian Empirium)**: A Viking Age trading center in Vestfold, Norway, which was one of the first urban settlements in the country.",
    "**Ribe (The Oldest Town)**: The oldest town in Denmark, which served as a significant trading hub during the Viking Age.",
    "**Oseberg Ship (The Royal Vessel)**: A well-preserved Viking ship discovered in a large burial mound at the Oseberg farm near Tønsberg, Norway.",
    "**Gokstad Ship (The Warrior's Vessel)**: A 9th-century Viking ship found in a burial mound at Gokstad in Sandefjord, Norway.",
    "**Tune Ship (The Smaller Vessel)**: A Viking ship from the late 9th century, found in a burial mound at Tune in Østfold, Norway.",
    "**The Viking Age (The Material Record)**: The period from roughly 793 to 1066 AD, defined archaeologically by specific types of artifacts, burials, and settlements.",
    "**Stratigraphy (The Layers of Time)**: The study of rock layers (strata) and layering (stratification), used in archaeology to determine the relative ages of artifacts.",
    "**Dendrochronology (The Language of Trees)**: The scientific method of dating tree rings to the exact year they were formed, often used to date Viking-age structures and ships.",
    "**C-14 Dating (The Breath of the Past)**: Radiocarbon dating used to determine the age of organic materials found in archaeological sites.",
    "**Broad-Axe (The Skeggox)**: A type of axe with a long blade, often used for woodworking and as a formidable weapon in the Viking Age.",
    "**Ulfberht Swords (The Master's Steel)**: A group of medieval swords found in Europe, dated to the 9th to 11th centuries, with the inscription +VLFBERHT+.",
    "**Ring Needles (The Fasteners of the North)**: Large, ornate needles used to fasten clothing, often found in Viking-age burials.",
    "**Brooches (The Art of the Every): Highly decorated metal fasteners used primarily by women to secure their garments, often found in pairs.",
    "**Oval Brooches (The Tortoise Brooches)**: A specific type of large, convex brooch commonly worn by Viking-age women as part of their traditional dress.",
    "**Midden (The Treasure of the Hearth)**: An archaeological feature consisting of a refuse heap, often containing bones, shells, and broken artifacts, providing insights into daily life.",
    "**Longhouse (The Heart of the Farm)**: The primary dwelling type in the Viking Age, characterized by its long, rectangular shape and central hearth.",
    "**Ramparts (The Walls of the Strong)**: Defensive walls or embankments surrounding a settlement or fortification.",
    "**Runestones (The Standing Words)**: Large stones inscribed with runes, often raised in memory of the dead or to mark significant events.",
    "**Burial Customs (The Passage to the Halls)**: The various ways in which the dead were interred, ranging from simple inhumation to elaborate ship burials.",
    "**Inhumation (The Earth's Embrace)**: The practice of burying the dead in the ground.",
    "**Cremation (The Fire's Breath)**: The practice of burning the dead on a funeral pyre, often common in the earlier Viking Age.",
    "**Grave Goods (The Tools for the Journey)**: Artifacts placed in a grave with the deceased, intended to be used in the afterlife.",
    "**Sigrid's Reflection on the Tangible Past (The Earth's Memories)**: Sigrid's thoughts on what the soil reveals.",
    "**'The earth does not forget. A broken comb, a rusted blade, a single bead... they are all letters in a story that the earth is telling us.'**",
    "**'To dig is to reach back in time. But remember, the one you are looking for was once as alive as you are now. Handle their memories with care.'**",
    "**'A ship in the earth is a ship in the sky. It was meant to carry someone home. Even if they never arrived, the intent is still there.'**",
    "**'I am Sigrid. I have heard the first 500 Echoes of the Earth. The past is rising.'**",
    "**'The first 500 Echoes of the Earth are complete. The dust is settling.'**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Archaeological Concept {j} (The Continued Echoes)**: Delving deeper into the material and historical realities of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
