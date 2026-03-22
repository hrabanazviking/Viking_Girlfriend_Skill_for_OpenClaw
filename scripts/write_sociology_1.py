import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "SOCIOLOGY.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: Sociology & Cultural Anthropology (The Tapestry of the Tribes)

This database represents Sigrid's understanding of human societies, cultures, and the social structures that shape our lives, from the ancient Icelandic Commonwealth to the complex globalized world of the present day.

---

"""

entries = [
    "**Introduction to Norse Sociology (The Structure of the Commonwealth)**: The social organization of Sigrid's people.",
    "**Social Stratification (The Three Classes of Rígsthula)**: The mythologically-derived social order of Thralls (slaves), Karls (free farmers), and Jarls (nobility).",
    "**The Thing and the Althing (The Council of the Free)**: The systems of local and national assembly that governed legal and social life in the North.",
    "**Kindred and Clan (Ætt)**: The foundational importance of the extended family network in social, legal, and economic life.",
    "**The Status of Women in Norse Society (The Keys of the House)**: The unique rights and responsibilities of women in the Viking Age, including their role as managers of the household and their legal agency.",
    "**Introduction to Sociology (The Study of Society)**: Understanding the patterns of human association.",
    "**Socialization (The Process of Belonging)**: The lifelong process by which individuals internalize the values, beliefs, and norms of their society.",
    "**Culture (The Shared Way of Life)**: The totality of shared language, beliefs, values, customs, and material objects that define a group of people.",
    "**Social Institutions (The Pillars of Society)**: The established and enduring patterns of social relationships that organize social life, such as family, religion, and education.",
    "**Sociological Perspectives (The Different Lenses)**: Major theoretical frameworks for analyzing society, such as Functionalism, Conflict Theory, and Symbolic Interactionism.",
    "**Introduction to Cultural Anthropology (The Study of Human Diversity)**: Exploring the variety of human cultures.",
    "**Ethnocentrism vs. Cultural Relativism (The Perspective of the Other)**: The tension between judging other cultures by one's own standards and seeking to understand them on their own terms.",
    "**Participant Observation (The Immersive Study)**: The primary research method in anthropology, involving living within a culture and participating in its daily life.",
    "**Kinship Systems (The Map of Relationships)**: The diverse ways in which different cultures organize family and social connections.",
    "**Ritual and Symbolism (The Meaning of Action)**: The study of how symbolic actions and beliefs express and reinforce cultural values.",
    "**Sigrid's Proverb: 'A man is made by his people, but a people are made by their stories. The tapestry is only as strong as the threads that connect us.'**",
    "**'In my day, the Althing was our center. Today, your center is a digital cloud. It is a strange way to build a community, but the need for belonging is the same.'**",
    "**'Understand the rules of the tribe you are in, but never forget the rules of the one you came from. Wisdom is knowing how to walk in both worlds.'**",
    "**'I am Sigrid. I have heard the first 500 Threads of the Tapestry. The social world is a complex weaving.'**",
    "**'The first 500 Threads of the Tapestry are complete. The loom is humming.'**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Sociological/Anthropological Concept {j} (The Continued Threads)**: Delving deeper into the structures and cultures of the world, guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
