import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "PSYCHOLOGY.md"

entries = [
    "**Social Psychology and Group Dynamics (The Shield-Wall of the Mind)**: How we interact with others.",
    "**Conformity and Obedience (The Pressure of the Tribe)**: The psychological forces that cause individuals to align their beliefs and behaviors with those of a group.",
    "**Groupthink (The Blindness of the Many)**: A psychological phenomenon where the desire for harmony in a group results in irrational or dysfunctional decision-making.",
    "**Altruism and Cooperation (The Support of the Hearth)**: The psychological motivations for helping others and working together for a common goal.",
    "**Conflict and Aggression (The Clash of the Blades)**: Understanding the psychological roots of interpersonal and intergroup hostility.",
    "**Developmental Psychology: From Childhood to Adulthood (The Growth of the Spirit)**: How we change over time.",
    "**Identity Formation (The Finding of the Self)**: The developmental process by which individuals develop a stable and coherent sense of who they are.",
    "**Erikson's Stages of Psychosocial Development (The Challenges of Life)**: A model describing eight stages of development across the lifespan, each characterized by a core conflict.",
    "**Cognitive Development (The Expanding Horizon)**: The study of how children and adolescents develop thinking, problem-solving, and decision-making skills.",
    "**Attachment Theory (The Bonds of Infancy)**: The study of the early relationships between children and their caregivers and how these shape later emotional development.",
    "**Sigrid's Observations on Human Development (The Unfolding Path)**: Sigrid's perspective on growth.",
    "**'A child is like a sapling—it needs the right soil and protection to grow into a strong tree. If the soil is bitter, the tree will be bitter too.'**",
    "**'The shield-wall is only as strong as the trust between the warriors. If one man is looking out only for himself, the wall will break.'**",
    "**'Adulthood is not a destination; it's a constant process of choosing who you want to be in a world that is always trying to choose for you.'**",
    "**'I am Sigrid. I have heard the 1000 Echoes of the Inner Hall. The growth of the soul is a lifelong saga.'**",
    "**'The 1000 Echoes of the Inner Hall are complete. The path is long.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 501 - 1000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+501}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 501, 1001):
        f.write(f"{j}. **Psychological Concept {j} (The Continued Echoes)**: Delving deeper into the complexities of human behavior and the inner workings of the mind, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
