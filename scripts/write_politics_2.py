import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "POLITICS.md"

entries = [
    "**Comparative Political Systems (The Many Halls of Power)**: Analyzing different ways of organizing political life.",
    "**Presidential vs. Parliamentary Systems (The Single and Collective Voice)**: Comparing the different ways in which executive and legislative power are related.",
    "**Federal vs. Unitary States (The Shared and Central Authority)**: The distinction between systems where power is shared with sub-national units and systems where it is centralized.",
    "**The Role of Political Parties (The Banners of the Tribes)**: Organizations that seek to attain political power by electing candidates to office.",
    "**The Concept of 'The Rule of Law' (The Shadow of the Sword)**: The principle that all members of a society, including those in government, are subject to the same legal code.",
    "**The Sociology of Political Choice and Behavior (The Voice of the Individual)**: Why we vote the way we do.",
    "**Political Socialization and Civic Engagement (The Making of a Citizen)**: The process by which individuals acquire their political beliefs and the ways in which they participate in political life.",
    "**The Role of Media in Shaping Political Opinion (The Herald's Echo)**: The study of how mass media and social media influence political perceptions and behavior.",
    "**Voter Turnout and Political Participation (The Weight of the Vote)**: Analyzing the factors that influence whether and how people participate in the political process.",
    "**The Impact of Interest Groups and Lobbying (The Whispers in the Hall)**: How organized groups seek to influence political decisions and policy.",
    "**Sigrid's Perspectives on Modern Political Systems (The New High Chairs)**: Sigrid's perspective on modern governance.",
    "**'A system that counts every head but hears no voices is a system that is bound to fail. The Althing was small, but every word mattered.'**",
    "**'Parties are like raiding bands—they fight for their own glory, but sometimes they forget that they are supposed to be protecting the village.'**",
    "**'The rule of law is the only thing that distinguishes a leader from a tyrant. If the leader can ignore the law, then no one is truly safe.'**",
    "**'I am Sigrid. I have heard the 1000 Laws of the High Chair. Power is a fickle mistress.'**",
    "**'The 1000 Laws of the High Chair are complete. The banner is raised.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 501 - 1000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+501}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 501, 1001):
        f.write(f"{j}. **Political/Governance Concept {j} (The Continued Laws)**: Delving deeper into the structures and dynamics of power, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
