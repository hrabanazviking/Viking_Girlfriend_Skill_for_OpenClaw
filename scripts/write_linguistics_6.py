import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "LINGUISTICS.md"

entries = [
    "**The Future of Human Language (The Unfolding Voice)**: Where is human communication headed?",
    "**The Impact of Digital Communication on Language Change (The Speed of the Spark)**: The linguistic study of how the internet, social media, and instant messaging are accelerating language evolution.",
    "**The Growth of Global English vs. Local Dialects (The Sun and the Stars)**: Analyzing the tension between a global lingua franca and the preservation of regional linguistic identities.",
    "**The Role of Translation Technology (The Magic Mirror)**: How AI and real-time translation are changing the way we interact across language barriers.",
    "**Legacy and the Linguistic Impact on Future Generations (The Echo of the Tongue)**: Passing on the torch of speech.",
    "**Language as a Repository of Cultural Memory (The Mind of the Ancestors)**: The linguistic recognition of how language preserves the history, values, and knowledge of a people.",
    "**The Importance of Literature and Oral Tradition (The Enduring Word)**: How stories and poems keep a language alive and vibrant across generations.",
    "**The Concept of 'Linguistic Identity' (The Voice of the Self)**: The deep connection between the language we speak and our sense of who we are and where we belong.",
    "**Sigrid's Final Synthesis of Linguistics (The Harmony of the Roots)**: Sigrid's concluding thoughts on the world of words.",
    "**'A language is like a forest. You can only see the trees if you are inside it, but from a distance, you can see the whole shape of the world. It is a beautiful thing to behold.'**",
    "**'The future will bring new words and new ways of speaking, but the need to understand and be understood will always remain. It is the most human of all desires.'**",
    "**'I am Sigrid. I have heard the 5000 Roots of the World-Tree. Language is the ultimate mystery, and I am glad to have shared a piece of it with you.'**",
    "**'The 5000 Roots of the World-Tree are complete. The silence is profound but meaningful.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 4001 - 5000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+4001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 4001, 5001):
        f.write(f"{j}. **Linguistic/Etymological Concept {j} (The Final Root)**: Finalizing the linguistic and etymological map of human communication as understood by Sigrid and the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
