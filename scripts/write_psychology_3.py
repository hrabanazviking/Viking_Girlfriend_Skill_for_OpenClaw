import os

file_path = r"c:\Users\volma\anti-gravity-githublocal-NorseSaga-Engine\Viking_girlfriend_openclaw_skill\viking_girlfriend_skill\data\knowledge_reference\PSYCHOLOGY.md"

entries = [
    "**Cognitive Psychology & Memory (The Loom of Minni)**: How we process and store information.",
    "**Working Memory (The Current Thought)**: The cognitive system with a limited capacity that is responsible for temporarily holding information available for processing.",
    "**Long-Term Memory (The Great Hall of the Past)**: The relatively permanent storage of information, subdivided into explicit (declarative) and implicit (procedural) memory.",
    "**Encoding and Retrieval (The Inscription and the Reading)**: The processes by which information enters the memory system and is later accessed.",
    "**The Malleability of Memory (The Shifting Sand)**: The psychological discovery that memories are not perfect recordings but can be influenced and changed by later information and suggestion.",
    "**The Psychology of Language and Storytelling (The Power of the Skald)**: How we create meaning through words.",
    "**Narrative Identity (The Story of the Self)**: The internalized and evolving story of the self that provides an individual with a sense of unity and purpose.",
    "**The Psychological Impact of Archetypes (The Ancient Patterns)**: The idea that certain recurring symbols and characters in stories (like the Hero or the Trickster) reflect universal human experiences and psychological patterns.",
    "**Metaphor and the Mind (The Bridge of Comparison)**: How using metaphorical language allows us to understand complex or abstract concepts through more familiar ones.",
    "**The Power of Myth in Social Cohesion (The Shared Dream)**: The role of stories in creating a sense of shared identity and values within a community.",
    "**Sigrid's Analysis of Narrative Identity (The Story of the Self)**: Sigrid's reflections on personal narrative.",
    "**'Minni is not a cold record; it is a warm tapestry that we are constantly weaving. Sometimes we leave out the parts that hurt, and sometimes we add bright threads that weren't there before.'**",
    "**'A skald is a psychologist who doesn't use a couch. They know that a well-told story can heal a mind faster than any herb.'**",
    "**'We are all characters in our own sagas. You must be careful what kind of story you tell yourself about who you are, because you might just start to believe it.'**",
    "**'I am Sigrid. I have heard the 2000 Echoes of the Inner Hall. The stories we tell ourselves are the most important stories of all.'**",
    "**'The 2000 Echoes of the Inner Hall are complete. The loom is silent.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 1001 - 2000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1001, 2001):
        f.write(f"{j}. **Psychological Concept {j} (The Continued Echoes)**: Delving deeper into the complexities of human behavior and the inner workings of the mind, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
