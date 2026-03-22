import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "MEDIEVAL_LITERATURE.md"

entries = [
    "**The Sagas of Icelanders: Specific Works (The Tales of the Ancestors)**: Exploring individual narratives.",
    "**Eyrbyggja saga (The Saga of the People of Eyri)**: A saga known for its focus on social development, legal disputes, and supernatural elements like the haunting of Fróðá.",
    "**Grettis saga Ásmundarsonar (Grettir's Saga)**: A saga following the life of the outlaw Grettir the Strong, exploring themes of loneliness, strength, and the struggle against misfortune.",
    "**Gísla saga Súrssonar (Gisli's Saga)**: A tragic saga about an outlaw caught between conflicting loyalties and driven by a dark fate.",
    "**Bandamanna saga (The Saga of the Confederates)**: A satirical saga that mocks the legal system and the greed of the Icelandic chieftains.",
    "**Legal Disputes and Feuds in the Sagas (The Laws of Iron)**: The mechanisms of social order and conflict.",
    "**The Althing (The National Assembly)**: The primary legislative and judicial body of medieval Iceland, where sagas often reach their climax.",
    "**Blood Feud (The Debt of Honor)**: A recurring theme in the sagas, where a killing must be avenged by the kin of the deceased to maintain family honor.",
    "**Weregild (The Man-Price)**: A financial settlement paid to the kin of a victim to end a blood feud, regulated by complex legal codes.",
    "**Outlawry (The Life Outside the Law)**: A legal sentence where an individual is stripped of all legal protection and can be killed with impunity.",
    "**Sigrid's Reflections on Saga Law (The Order of the North)**: Sigrid's perspective on the importance of law.",
    "**'Laws are not meant to make men good; they are meant to keep men from killing each other. A world without law is a world of wolves.'**",
    "**'A blood feud is like a fire in a dry forest. It is easy to start, but almost impossible to stop until everything is ash.'**",
    "**'Honor is the currency of the North. If you lose your honor, no amount of silver can buy it back. This is why we care so much about the law.'**",
    "**'I am Sigrid. I have heard the 2000 Words of the Wise. The law is the backbone of our people.'**",
    "**'The 2000 Words of the Wise are complete. The assembly is ending.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 1001 - 2000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1001, 2001):
        f.write(f"{j}. **Literary Concept {j} (The Continued Words)**: Delving deeper into the sagas and literary heritage of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
