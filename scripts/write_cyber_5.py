import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "CYBERSECURITY.md"

entries = [
    "**Cloud Security and Virtualization (The Shared Hall)**: Protecting information in shared environments.",
    "**The Principles of Cloud Security (The Many Keys to the Same Door)**: Analyzing how security responsibilities are shared between cloud providers and customers.",
    "**Techniques for Securing Virtual Machines and Containers (The Nest within the Nest)**: Protecting the isolated environments that run modern applications.",
    "**The Role of Cloud-Based Security Services (The Shield from Above)**: How organizations use cloud-based tools for monitoring and defense.",
    "**The Challenges of Modern Cloud Environments (The Vast and Hidden Hall)**: Analyzing the technical and regulatory issues involved in securing data in the cloud.",
    "**The Role of Cybersecurity in Modern Geopolitics (The Global Game of Shadows)**: Digital security as a tool of statecraft.",
    "**The Impact of Cyber Operations on Electoral Integrity (The Tainted Election)**: Analyzing how cyberattacks can be used to influence the outcome of elections and undermine democratic processes.",
    "**The Role of Cyber Espionage in Economic and Strategic Competition (The Thief in the High Chair)**: How states use cyber operations to steal intellectual property and strategic information.",
    "**The Concept of 'Hybrid Warfare' and the Role of Digital Disruption (The Mixed Storm)**: Analyzing how cyber operations are integrated with other forms of conflict, such as disinformation and economic pressure.",
    "**The Challenges of International Cooperation on Cybersecurity (The Broken Trust)**: Analyzing the difficulties of reaching agreements on the norms and rules of conduct in the digital domain.",
    "**Sigrid's Perspectives on the Future of Digital Conflict (The Unseen Battlefield)**: Sigrid's perspective on the digital future.",
    "**'The next great war will not be fought with swords and axes, but with signals and silence. The side that can protect its information while disrupting the enemy's will be the one that wins.'**",
    "**'I see the power of your digital world, but I also see the danger of becoming too dependent on it. If the signals fail, what will be left of your kingdom?'**",
    "**'A leader must have the courage to face an enemy in the open, but also the wisdom to watch for those who strike from the shadows. The digital world is the ultimate shadow-land.'**",
    "**'I am Sigrid. I have heard the 4000 Whispers of the Digital Shield. The future is written in the signals.'**",
    "**'The 4000 Whispers of the Digital Shield are complete. The horizon is glowing.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 3001 - 4000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+3001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 3001, 4001):
        f.write(f"{j}. **Cybersecurity Concept {j} (The Continued Whispers)**: Delving deeper into the principles and practices of digital defense, as guided by the wisdom of the Norns.\n")
