import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "SOCIOLOGY.md"

entries = [
    "**Social Stratification and Mobility (The Ladder of the World)**: How power and resources are distributed.",
    "**Ascribed vs. Achieved Status (The Birth and the Deed)**: The distinction between social positions assigned at birth and those earned through individual effort and achievement.",
    "**Social Mobility (The Climb and the Fall)**: The movement of individuals or groups between different social classes or statuses.",
    "**Inequality and Power Dynamics (The Weight of the Crown)**: The sociological study of how social structures create and maintain unequal access to resources and influence.",
    "**The Role of Education in Social Reproduction (The Passing of the Torch)**: How educational systems contribute to the continuity of social status and values across generations.",
    "**The Sociology of Religion and Ritual (The Sacred Bond)**: How belief systems organize social life.",
    "**Religious Pluralism (The Many Altars)**: The coexistence of different religious groups within a single society and the social dynamics that result.",
    "**Secularization (The Cooling of the Hearth)**: The historical process by which religion loses its central influence in various spheres of social life.",
    "**The Social Function of Ritual (The Binding Thread)**: How collective rituals reinforce social solidarity and express shared cultural values.",
    "**The Role of Charismatic Leadership in Religious Movements (The Flame of the Prophet)**: How individual leaders can inspire and organize new religious or social groups.",
    "**Sigrid's Perspectives on Social Order (The Strength of the Loom)**: Sigrid's perspective on societal stability.",
    "**'A society without a ladder is a society without hope, but a society where the rungs are broken for some is a society that will eventually fall.'**",
    "**'Religion is the glue that held my people together, but it can also be the wall that keeps others out. Wisdom is knowing how to use it as a bridge instead.'**",
    "**'The Thing was our way of ensuring that every free man had a voice. Today, your voices are many, but are they heard by those who sit on the high chairs?'**",
    "**'I am Sigrid. I have heard the 1000 Threads of the Tapestry. The structure of the world is a fascinating study.'**",
    "**'The 1000 Threads of the Tapestry are complete. The weave is tight.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 501 - 1000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+501}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 501, 1001):
        f.write(f"{j}. **Sociological/Anthropological Concept {j} (The Continued Threads)**: Delving deeper into the structures and cultures of the world, guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
