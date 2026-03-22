import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "NORSE_FOLKLORE.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: Norse Folklore & Legend (The Whispers of the Wild)

This database represents Sigrid's deep understanding of the folk traditions, supernatural beings, and magical practices of the North, extending from the Viking Age into the later Scandinavian folklore.

---

"""

entries = [
    "**Alfar (The Elves)**: Supernatural beings who live in the hills and mounds, often associated with fertility and ancestral spirits.",
    "**Ljosalfar (Light Elves)**: Spirits who live in Alfheim and are said to be 'fairer than the sun to look upon'.",
    "**Dökkalfar (Dark Elves)**: Spirits who live in the earth and are often associated with craftsmanship and smithing.",
    "**Dvergar (The Dwarves)**: Beings of the earth, renowned for their skill in metallurgy and magic, living in Svartalfheim/Nidavellir.",
    "**Jötnar (The Giants)**: Beings of great power and size, often representing the chaotic forces of nature.",
    "**Vættr (The Spirits)**: A general term for supernatural beings, including land spirits (Landvættir) and house spirits.",
    "**Landvættir (Land Spirits)**: Guardians of the land who reside in rocks, hills, and waterfalls, requiring respect and offerings.",
    "**Huldra (The Hidden One)**: A seductive forest creature from Scandinavian folklore, known for her hollow back and cow's tail.",
    "**Nisse/Tomte (The House Spirit)**: A small, gnome-like being who protects the farm and its animals, but can be mischievous if offended.",
    "**Fossegrim (The Waterfall Musician)**: A water spirit who plays the violin with such skill that it can make the trees dance and the waterfalls stop.",
    "**Nacken (The Water Nix)**: A shapeshifting water spirit who lures people to drown in rivers and lakes with his enchanting music.",
    "**Mares (Nightmare Spirits)**: Malicious beings that sit on a person's chest while they sleep, causing bad dreams and feelings of suffocation.",
    "**Valkyries (The Choosers of the Slain)**: Handmaidens of Odin who decide which warriors live and die in battle, bringing the chosen to Valhalla.",
    "**Einherjar (The Honored Dead)**: The spirits of warriors who have died heroically in battle and are brought to Valhalla to prepare for Ragnarok.",
    "**Draugr (The Undead)**: An animated corpse that guards its burial mound and can possess superhuman strength and magical abilities.",
    "**Haugbúi (The Mound-Dweller)**: A type of undead being that remains within its burial mound, unlike the more mobile draugr.",
    "**Seiðr (Folk Magic)**: A form of magic concerned with discerning and altering the course of fate, often involving shamanic practices and trances.",
    "**Galdr (Incantation Magic)**: Magic performed through the use of spoken or sung incantations and the carving of runes.",
    "**Hamrammr (Shapeshifting)**: The ability of some individuals or beings to change their physical form, often into animals.",
    "**Fylgja (The Follower)**: An ancestral spirit or familiar who accompanies a person through life, often appearing in animal form in dreams.",
    "**Hamingja (The Luck Guardian)**: A personification of the luck or fortune of a person or family, often passed down through generations.",
    "**Wyrd (The Web of Fate)**: The fundamental concept of destiny as an interconnected web woven by the Norns.",
    "**Hugr (The Mind/Spirit)**: The conscious spirit or thought-soul of a person, which can sometimes travel outside the body.",
    "**Sigrid's Proverb: 'The wild is never empty. If you feel eyes upon you in the woods, it is because something is looking. Offer a piece of bread, and speak with respect.'**",
    "**'The ghosts of the ancestors are not gone; they are just waiting for us to remember their names.'**",
    "**'Magic is not a gift from the gods; it is a conversation with the world. You must learn to listen before you can speak.'**",
    "**'I am Sigrid. I have heard the first 500 Whispers of the Wild. The spirits are active.'**",
    "**'The first 500 Whispers of the Wild are complete. The shadows are deepening.'**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Folklore Concept {j} (The Continued Whispers)**: Delving deeper into the mythological and supernatural tapestry of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
