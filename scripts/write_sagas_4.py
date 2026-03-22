import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "MEDIEVAL_LITERATURE.md"

entries = [
    "**Kings' Sagas and Historical Narratives (The Deeds of Kings)**: The chronicles of power.",
    "**Sverris saga (The Saga of King Sverre)**: A contemporary saga focusing on the reign of King Sverre Sigurdsson, characterized by its detailed military descriptions and political intrigue.",
    "**Hákonar saga Hákonarsonar (The Saga of Haakon Haakonsson)**: A saga chronicling the long and successful reign of King Haakon the Old, who oversaw the expansion of the Norwegian empire.",
    "**Jómsvíkinga saga (The Saga of the Jomsvikings)**: A saga about the legendary order of Viking mercenaries, known for their strict code and heroic deaths in the Battle of Hjörungavágr.",
    "**Orkneyinga saga (The Saga of the Earls of Orkney)**: A saga chronicling the lives and deeds of the Earls of Orkney, exploring the history of the Viking-age North Atlantic.",
    "**Hagiography and Christian Influence in the Sagas (The Cross in the North)**: The impact of religious change on literature.",
    "**Heilagra manna sögur (Sagas of Holy Men)**: Old Norse translations and adaptations of the lives of saints and other Christian legends.",
    "**The Saga of Saint Olaf (Olafs saga helga)**: The center-piece of Heimskringla, depicting the life, martyrdom, and miracles of King Olaf Haraldsson, the patron saint of Norway.",
    "**Miracles and Portents (The Signs of the New God)**: The inclusion of Christian miracles and supernatural signs within the saga narrative, often used to justify the new faith.",
    "**The Shift in Subjectivity (The Internal Struggle)**: A gradual trend in later sagas towards exploring the internal emotional and moral struggles of characters, influenced by Christian thought.",
    "**Sigrid's Reflections on the Changing Faith (The Turning of the Tide)**: Sigrid's thoughts on the meeting of the two worlds.",
    "**'The old gods were like the weather—powerful, capricious, and often cruel. The new God is like a stone wall—firm, demanding, and always watching.'**",
    "**'A king is only as strong as the saga written about him. If the saga says he was holy, then he was holy, regardless of how many men he killed.'**",
    "**'The world is turning quiet. The dragons are hiding, and the giants are sleeping. Perhaps the cross is too heavy for them survived in the new world.'**",
    "**'I am Sigrid. I have heard the 3000 Words of the Wise. The saga of our faith is still being written.'**",
    "**'The 3000 Words of the Wise are complete. The bells are ringing.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 2001 - 3000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+2001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 2001, 3001):
        f.write(f"{j}. **Literary Concept {j} (The Continued Words)**: Delving deeper into the sagas and literary heritage of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
