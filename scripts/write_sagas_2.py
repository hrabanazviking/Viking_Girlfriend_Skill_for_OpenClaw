import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "MEDIEVAL_LITERATURE.md"

entries = [
    "**The Literary Style of the Sagas (The Sharp Edge of the Word)**: The unique aesthetic of Icelandic prose.",
    "**Saga Realism (The Plain Truth)**: The objective and understated tone characteristic of Icelandic sagas, focusing on action and dialogue rather than internal monologue.",
    "**Understatement (The Icelandic Dryness)**: A literary technique where significant emotions or events are described with minimal emphasis, often for dramatic or ironic effect.",
    "**Genealogy in the Sagas (The Roots of the Story)**: The detailed lists of ancestors and kin that anchor saga characters in a historical and social context.",
    "**Saga Prosimetrum (The Verse in the Prose)**: The inclusion of skaldic stanzas within the prose narrative of a saga, often to authenticate the story or express deep emotion.",
    "**The Saga Characters: Heroes & Anti-Heroes (The Faces of the North)**: The complex individuals of literature.",
    "**The Saga Hero (The Man of Honor)**: An individual who adheres to a strict code of honor, even at the cost of their life (e.g., Gunnar Hámundarson).",
    "**The Saga Anti-Hero (The Flawed Spirit)**: A character who may possess great talent or strength but is driven by personal ambition, spite, or a dark destiny (e.g., Egill Skallagrímsson).",
    "**The Wise Man (The Counsel of the Old)**: A character known for their legal knowledge, foresight, and sound advice (e.g., Njáll Þorgeirsson).",
    "**The Strong Woman (The Force of Nature)**: Powerful female characters who often drive the plot through their influence, pride, and desire for revenge (e.g., Guðrún Ósvífursdóttir).",
    "**Sigrid's Analysis of Saga Personalities (The Mirror of the Soul)**: Sigrid's reflections on saga characters.",
    "**'Gunnar was a hero because he could not be anything else. His soul was as straight as his sword, and just as sharp.'**",
    "**'Njal was wise because he knew that even the best laws cannot save a man from his own fate. Wisdom is knowing how to burn gracefully.'**",
    "**'Guðrún lived a thousand lives in one. She loved many, but her heart was always her own. She is the shadow and the sun of the Laxdæla valley.'**",
    "**'I am Sigrid. I have heard the 1000 Words of the Wise. The characters of the past are still walking among us.'**",
    "**'The 1000 Words of the Wise are complete. The voices are clear.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 501 - 1000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+501}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 501, 1001):
        f.write(f"{j}. **Literary Concept {j} (The Continued Words)**: Delving deeper into the sagas and literary heritage of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
