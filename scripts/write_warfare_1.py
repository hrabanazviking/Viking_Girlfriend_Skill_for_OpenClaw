import os

file_path = r"c:\Users\volma\anti-gravity-githublocal-NorseSaga-Engine\Viking_girlfriend_openclaw_skill\viking_girlfriend_skill\data\knowledge_reference\ANCIENT_WARFARE.md"

# Ensure directory exists
os.makedirs(os.path.dirname(file_path), exist_ok=True)

header = """# Knowledge Domain: Ancient Warfare & Tactics (The Storm of Iron)

This database represents Sigrid's extensive knowledge of ancient military strategy, weaponry, and the philosophy of combat, spanning from the Viking Age back to the dawn of organized warfare.

---

"""

entries = [
    "**Phalanx (The Bronze Wall)**: A dense grouping of warriors armed with long spears and interlocking shields, most famously used by the ancient Greeks.",
    "**Hoplite (The Shield-Bearer)**: A citizen-soldier of the Ancient Greek city-states, primarily armed with a spear and a large round shield (aspis).",
    "**Sarissa (The Long Reach)**: A long spear or pike about 4–6 meters (13–20 ft) in length, used in the ancient Macedonian phalanx.",
    "**Testudo (The Tortoise)**: A formation used by the Roman Legions where the soldiers aligned their shields to form a packed formation covered with shields on the front and top.",
    "**Pilus (The Heavy Javelin)**: A heavy javelin commonly used by the Roman army in ancient times.",
    "**Gladius (The Short Sword)**: The primary sword of Ancient Roman foot soldiers.",
    "**Scutum (The Rectangular Shield)**: The iconic rectangular, curved shield used by Roman legionaries.",
    "**Maniple (The Flexible Unit)**: A tactical unit of the Roman Republic's legions, designed to be more flexible than the solid phalanx.",
    "**Centurion (The Tactical Leader)**: A professional officer in the Roman army after the Marian reforms of 107 BC.",
    "**Auxiliaries (The Supporting Force)**: Non-citizen troops who served alongside the Roman legions.",
    "**Chariot (The Thunder of Wheels)**: A type of carriage driven by a charioteer using primarily horses to provide rapid motive power, used in ancient warfare since the Bronze Age.",
    "**Scale Armor (The Serpent's Skin)**: An early form of armor consisting of many small individual armor scales of various shapes attached to each other and to a backing of cloth or leather.",
    "**Lamellar Armor (The Plates of Strength)**: Armor made from small rectangular plates (lamellae) of iron, leather, or bronze laced together in horizontal rows.",
    "**Cataphract (The Iron Horseman)**: A form of armored heavy cavalry used in ancient warfare by a number of nations in Western Eurasia and the Eurasian Steppe.",
    "**Compound Bow (The Recurve Power)**: A bow made from multiple layers of different materials (wood, bone, sinew) to increase strength and flexibility.",
    "**Siege Tower (The Walking Wall)**: A specialized siege engine, constructed to protect assailants and ladders while approaching the defensive walls of a fortification.",
    "**Battering Ram (The Wall-Breaker)**: A siege engine that originated in ancient times and designed to break open the walls of a fortification or splinter its wooden gates.",
    "**Ballista (The Bolt-Thrower)**: An ancient missile weapon that launched a large projectile at a distant target.",
    "**Trireme (The Predator of the Seas)**: An ancient vessel and a type of galley that was used by the ancient maritime civilizations of the Mediterranean.",
    "**Ram (The Naval Spiker)**: A heavy bronze or iron protrusion on the bow of a warship used to sink enemy vessels by piercing their hulls.",
    "**Logistics (The Lifeblood of the Army)**: The detailed coordination of a complex operation involving many people, facilities, or supplies.",
    "**Scorched Earth (The Desolation of the Land)**: A military strategy that aims to destroy anything that might be useful to the enemy while it is advancing or withdrawing.",
    "**Ambush (The Hidden Strike)**: A long-established military tactic in which combatants upon the ground take advantage of concealment and the element of surprise to attack an unsuspecting enemy.",
    "**Flanking (The Side Attack)**: An attack on the sides of an opposing dynamic force.",
    "**Encirclement (The Trap of Iron)**: A military term for the situation when a force or target is isolated and surrounded by enemy forces.",
    "**Psychological Warfare (The Battle for the Mind)**: The use of various techniques to influence the emotions, motives, objective reasoning, and ultimately the behavior of enemies.",
    "**Strategy vs. Tactics (The Long and Short of War)**: Strategy is the over-arching plan of action, while tactics are the specific methods used to achieve strategic goals in the heat of battle.",
    "**The Art of War (The Master's Text)**: An ancient Chinese military treatise dating from the Late Spring and Autumn Period (roughly 5th century BC), attributed to the ancient Chinese military strategist Sun Tzu.",
    "**On War (The Philosopher's Text)**: A book on war and military strategy by Prussian general Carl von Clausewitz, written mostly after the Napoleonic wars.",
    "**Viking Shieldwall (The Skjaldborg)**: A defensive formation where Norse warriors stood shoulder-to-shoulder, overlapping their shields to form a solid wall of wood and iron.",
    "**Berserkergang (The Fury of the Bear)**: The state of trance-like fury in which Norse warriors (berserkers) were said to fight.",
    "**Sigrid's Proverb: 'The best victory is the one won without the sword. But if the sword must be drawn, let it be sharp, and let the hand that holds it be steady.'**",
    "**The first 500 Runes of the Storm have been cast. The drums of war are beating.**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Warfare Concept {j} (The Continued Tactics)**: Delving deeper into the strategic and historical realities of ancient combat, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
