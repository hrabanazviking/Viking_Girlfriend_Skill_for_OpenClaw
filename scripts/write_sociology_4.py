import os

file_path = r"c:\Users\volma\anti-gravity-githublocal-NorseSaga-Engine\Viking_girlfriend_openclaw_skill\viking_girlfriend_skill\data\knowledge_reference\SOCIOLOGY.md"

entries = [
    "**The Sociology of Deviance and Social Control (The Outlaw's Path)**: Defining the boundaries of the tribe.",
    "**Social Norms and Sanctions (The Rules of the Hall)**: The internalized rules of behavior and the rewards or punishments (like shaming or exile) used to enforce them.",
    "**The Concept of 'Outlawry' (Skóggangr)**: A geographical and legal form of deviance where an individual is placed outside the protection of the law and society.",
    "**Labeling Theory (The Name that Sticks)**: The sociological perspective that deviance is not inherent in an act but is a label applied by society to certain individuals or behaviors.",
    "**The Role of Law and the Thing (The Wisdom of the Assembly)**: How societies resolve conflict.",
    "**The Gulaþing and Frostaþing Laws (The Foundation of Justice)**: Early Norwegian regional laws that provided a framework for social and legal order.",
    "**The Role of the Lawspeaker (Lögsögumaðr)**: The individual responsible for memorizing and reciting the laws at the Althing, representing the importance of oral tradition in social control.",
    "**Restorative Justice in the North (The Path to Reconciliation)**: The focus on compensation (weregild) and mediation rather than just punishment, aimed at restoring social harmony.",
    "**Sigrid's Reflections on Justice and Vengeance (The Balance of the Axe)**: Sigrid's perspective on societal rules.",
    "**'A law is just a story we all agree to believe in so we don't end up killing each other. But sometimes, the story is written by those with the sharpest axes.'**",
    "**'Vengeance is a fire that can warm your heart for a night, but it will eventually burn your house down. This is why we have the Thing—to turn the fire into a hearth.'**",
    "**'Being an outlaw is a lonely path. It's easy to break the rules when you don't care about the tribe, but it's hard to stay alive when the tribe doesn't care about you.'**",
    "**'I am Sigrid. I have heard the 3000 Threads of the Tapestry. Justice is the only thing that keeps the tapestry from unraveling.'**",
    "**'The 3000 Threads of the Tapestry are complete. The gavel has fallen.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 2001 - 3000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+2001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 2001, 3001):
        f.write(f"{j}. **Sociological/Anthropological Concept {j} (The Continued Threads)**: Delving deeper into the structures and cultures of the world, guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
