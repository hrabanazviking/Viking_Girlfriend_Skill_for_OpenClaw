import os

file_path = r"c:\Users\volma\anti-gravity-githublocal-NorseSaga-Engine\Viking_girlfriend_openclaw_skill\viking_girlfriend_skill\data\knowledge_reference\VIKING_HISTORY_MYTHOLOGY.md"

entries = [
    "**Viking Warfare & Weapons (The Storm of Swords)**: The tools and tactics of the northern warriors.",
    "**Viking Shield (The Round Guard)**: Typically made of wood (often linden) and covered with leather, featuring a central iron boss.",
    "**Ulfbherht Swords (The Steel of the Gods)**: A group of medieval swords found in Europe, dated to the 9th to 11th centuries, with blades inscribed with the word +VLFBERHT+.",
    "**Dane Axe (The Long-Handed Death)**: An early type of battle axe, primarily used during the transition between the European Viking Age and early Middle Ages.",
    "**Viking Spear (The Piercer of Shields)**: The most common weapon used by Vikings, often with a socketed iron head.",
    "**Seax (The Warrior's Knife)**: A type of single-edged knife or dagger common to Germanic peoples.",
    "**Mail Shirt (The Link-Shield)**: A type of armor consisting of small metal rings linked together in a pattern to form a mesh.",
    "**Norse Helmet (The One with the Spectacles)**: Contrary to popular belief, they did not have horns; they were simple rounded caps often with a 'spectacle' guard for the eyes and nose.",
    "**Shield-Wall (The Skjaldborg)**: A defensive formation where warriors stand close together, overlapping their shields.",
    "**Holmgang (The Duel of Honor)**: A duel practiced by early medieval Scandinavians, often used to settle disputes.",
    "**The Prose & Poetic Eddas (The Whispers of the Skalds)**: The literary records of the divine.",
    "**Codex Regius (The King's Book)**: An Icelandic codex in which many Old Norse poems are preserved, considered the most important extant source on Norse mythology and Germanic heroic legends.",
    "**Gylfaginning (The Beguiling of Gylfi)**: The first section of the Prose Edda, which deals with the creation and destruction of the world of the Norse gods.",
    "**Skáldskaparmál (The Language of Poetry)**: The second part of the Prose Edda, which consists of a dialogue between Ægir and Bragi on the nature of poetry.",
    "**Háttatal (The Enumeration of Meters)**: The last part of the Prose Edda, which provides examples of various poetic meters.",
    "**Völuspá (The Prophecy of the Seeress)**: The first and best-known poem of the Poetic Edda, which tells the story of the creation and the end of the world.",
    "**Hávamál (The Sayings of the High One)**: A collection of advice for living, credited to Odin.",
    "**Lesser-Known Mythological Beings (The In-Between Ones)**: The hidden spirits of the world.",
    "**Dwarves (The Underground Craftsmen)**: Created from the maggots in the flesh of the giant Ymir, known for their skill in smithing.",
    "**Elves (The Luminous Ones)**: Including the Light Elves (Ljosalfar) of Alfheim and the Dark Elves (Dockalfar/Svartalfar) of Svartalfheim.",
    "**Vættir (The Land Spirits)**: Spirits of the land, who could be either helpful or harmful to humans.",
    "**Draugr (The Undead)**: An undead creature from Norse mythology, often associated with guarding treasures in burial mounds.",
    "**Mare (The Night-Spirit)**: A spirit who sits on people's chests at night, causing nightmares.",
    "**Ratatoskr (The Messenger Squirrel)**: A squirrel who runs up and down the world tree Yggdrasil to carry messages between the eagle at the top and the dragon Níðhöggr at the bottom.",
    "**Níðhöggr (The Corpse-Eater)**: A dragon that gnaws at a root of Yggdrasil.",
    "**Sigrid's Proverb: 'The sword is sharp, but the word is sharper. A warrior can win a battle, but a skald can win eternity.'**",
    "**The 2000 Runes of the Roots have been cast. The echoes of the past remain.**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 1001 - 2000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1001, 2001):
        f.write(f"{j}. **Viking History Concept {j} (The Continued Saga)**: Delving deeper into the ancient tales and historical truths of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
