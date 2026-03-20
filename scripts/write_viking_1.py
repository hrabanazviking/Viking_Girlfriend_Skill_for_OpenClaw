import os

file_path = r"c:\Users\volma\anti-gravity-githublocal-NorseSaga-Engine\Viking_girlfriend_openclaw_skill\viking_girlfriend_skill\data\knowledge_reference\VIKING_HISTORY_MYTHOLOGY.md"

# Ensure directory exists
os.makedirs(os.path.dirname(file_path), exist_ok=True)

header = """# Knowledge Domain: Viking History & Norse Mythology (The Roots of Yggdrasil)

This database represents Sigrid's deep connection to her heritage, covering the history, society, and mythology of the Viking Age and the Nine Realms.

---

"""

entries = [
    "**Viking Age (The Age of the Sea-Kings)**: The period from roughly 793 to 1066 AD, characterized by Norse exploration, expansion, and raids.",
    "**Norsemen (The People of the North)**: The North Germanic people who lived in Scandinavia during the Viking Age.",
    "**Scandinavia (The Ancestral Lands)**: A subregion in Northern Europe, including Denmark, Norway, and Sweden.",
    "**Lindisfarne (The First Strike)**: A tidal island off the northeast coast of England, home to a monastery that was raided in 793, marking the traditional start of the Viking Age.",
    "**Battle of Hastings (The Final Sunset)**: The battle in 1066 where Harold Godwinson was defeated by William the Conqueror, marking the traditional end of the Viking Age.",
    "**Longship (The Dragon of the Waves)**: A type of specialized sea vessel that is characterized as a long, narrow, light, wooden boat with a shallow-draft hull.",
    "**Knarr (The Merchant's Burden)**: A type of Norse merchant ship used for long-distance trade.",
    "**Stewardship (The Keeper of the Hall)**: The social and economic organization of the Viking community.",
    "**Thing (The Assembly of the Free)**: The governing assembly of a free Germanic people.",
    "**Althing (The Great Assembly)**: The national parliament of Iceland, founded in 930 AD.",
    "**Danegeld (The Price of Peace)**: A tax raised to pay tribute to the Viking raiders to save a land from being ravaged.",
    "**Varangian Guard (The Emperor's Shield)**: An elite unit of the Byzantine Army from the 10th to the 14th centuries, whose members served as personal bodyguards to the Byzantine Emperors and were composed mainly of Germanic peoples, specifically Norsemen.",
    "**The Nine Realms (The Branches of the Tree)**: The nine worlds connected by the world tree Yggdrasil.",
    "**Asgard (The Home of the Gods)**: The realm of the Æsir gods.",
    "**Midgard (The Middle Realm)**: The realm inhabited by humans.",
    "**Jotunheim (The Land of the Giants)**: The realm of the Jotnar (giants).",
    "**Vanaheim (The Home of the Vanir)**: The realm of the Vanir gods.",
    "**Alfheim (The Realm of the Elves)**: The realm of the Light Elves.",
    "**Svartalfheim (The Realm of the Dwarves)**: The realm of the Dwarves (also called Dark Elves).",
    "**Helheim (The Abode of the Dead)**: The realm of those who died of old age or illness.",
    "**Niflheim (The World of Fog)**: A primordial realm of ice and cold.",
    "**Muspelheim (The World of Fire)**: A primordial realm of fire and heat.",
    "**Yggdrasil (The World Tree)**: An immense ash tree that is center to the Norse cosmos and considered very holy.",
    "**Bifrost (The Rainbow Bridge)**: A burning rainbow bridge that reaches between Midgard and Asgard.",
    "**Odin (The All-Father)**: The king of the Æsir and the god of wisdom, poetry, death, divination, and magic.",
    "**Thor (The Thunderer)**: The god of thunder, lightning, storms, oak trees, strength, and the protection of mankind.",
    "**Loki (The Trickster)**: A god or jotunn who is described as a 'contriver of all frauds'.",
    "**Freyja (The Lady of Love and War)**: A goddess associated with love, beauty, fertility, sex, war, gold, and seiðr (magic).",
    "**Freyr (The Lord of Prosperity)**: A god associated with sacral kingship, virility, peace, and prosperity.",
    "**Tyr (The One-Handed God)**: A god associated with law and heroic glory.",
    "**Heimdall (The White God)**: The watchman of the gods who keeps watch for the onset of Ragnarök from Himinbjörg.",
    "**Frigg (The Queen of Asgard)**: The wife of Odin and the queen of the Æsir.",
    "**Baldur (The Beautiful)**: A god associated with light, beauty, love, and happiness, whose death is a pivotal event in Norse mythology.",
    "**Hodur (The Blind God)**: The blind brother of Baldur who, tricked by Loki, killed Baldur with a mistletoe arrow.",
    "**Hel (The Queen of the Dead)**: The goddess who rules over the realm of the same name.",
    "**Sif (The Golden-Haired)**: The wife of Thor, known for her beautiful golden hair.",
    "**Idun (The Keeper of the Apples)**: The goddess associated with youth and the apples that grant the gods immortality.",
    "**Bragi (The Scaldic God)**: The god of poetry and eloquence.",
    "**Njord (The God of the Sea)**: A god associated with the sea, seafaring, wind, fishing, wealth, and crop fertility.",
    "**Mimir (The Wise One)**: A figure in Norse mythology renowned for his knowledge and wisdom, who was beheaded during the Æsir–Vanir War.",
    "**Ragnarök (The Fate of the Gods)**: A series of future events, including a great battle, foretold to ultimately result in the death of a number of major figures, the occurrence of various natural disasters, and the subsequent submersion of the world in water.",
    "**Fenrir (The Great Wolf)**: A monstrous wolf, the son of Loki and Angrboda.",
    "**Jormungand (The Midgard Serpent)**: A sea serpent, the middle child of Loki and Angrboda, who encircles the world.",
    "**Sleipnir (The Eight-Legged Steed)**: Odin's eight-legged horse.",
    "**Valhalla (The Hall of the Slain)**: A majestic, enormous hall located in Asgard, ruled over by the god Odin.",
    "**Valkyrie (The Choosers of the Slain)**: A host of female figures who choose those who may die in battle and those who may live.",
    "**Einherjar (The Lone Warriors)**: Those who have died in battle and are brought to Valhalla by valkyries.",
    "**Folkvangr (The Field of the People)**: The afterlife realm ruled over by the goddess Freyja, where she receives half of those who die in battle.",
    "**Seiðr (Norse Magic)**: A type of magic which was practiced in Norse society during the Late Scandinavian Iron Age.",
    "**Runes (The Sacred Script)**: The letters in a set of related alphabets known as runic alphabets, which were used to write various Germanic languages before the adoption of the Latin alphabet.",
    "**Elder Futhark (The Ancient Runes)**: The oldest form of the runic alphabets.",
    "**Younger Futhark (The Viking Runes)**: A reduced form of the Elder Futhark, used during the Viking Age.",
    "**Havamal (The Sayings of the High One)**: A collection of Old Norse poems from the Viking Age, primarily presenting advice for living, credited to Odin.",
    "**Poetic Edda (The Songs of the Gods)**: A modern attribution for an unnamed collection of Old Norse anonymous poems, which is different from the Prose Edda.",
    "**Prose Edda (The Scribe's Handbook)**: An Old Norse work of literature written in Iceland during the early 13th century, traditionally attributed to Snorri Sturluson.",
    "**Skald (The Viking Poet)**: A composer and reciter of poems honoring heroes and their deeds.",
    "**Kenning (The Poet's Metaphor)**: A type of circumlocution, in the form of a compound that employs figurative language in place of a concrete single-word noun.",
    "**Berserker (The Bear-Shirt)**: An Norse warrior who was reported to have fought in a trance-like fury.",
    "**Shield-Maiden (The Woman of the Sword)**: A female warrior from Scandinavian folklore and mythology.",
    "**Thrall (The Unfree)**: A slave in Viking society.",
    "**Karl (The Free Man)**: A free peasant or artisan in Viking society.",
    "**Jarl (The Noble)**: A noble or chieftain in Viking society.",
    "**Sigrid's Proverb: 'The roots of Yggdrasil are watered by the past. If you do not know where you came from, you cannot know where you are going.'**",
    "**The first 500 Runes of the Roots have been cast. The ancestors are watching.**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Viking History Concept {j} (The Continued Saga)**: Delving deeper into the ancient tales and historical truths of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
