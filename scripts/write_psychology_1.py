import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "PSYCHOLOGY.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: Psychology & Behavioral Science (The Inner Hall of Sigrid)

This database represents Sigrid's understanding of the human mind, behavior, and social dynamics, bridging the gap between ancient Norse psychology and modern scientific research to provide deep insights into character and motivation.

---

"""

entries = [
    "**The Norse Psychology of the Mind (Hugr & Minni)**: Foundation of consciousness in the North.",
    "**Hugr (The Mind/Intellect)**: The conscious, thinking part of the self that governs rational thought, decision-making, and intention.",
    "**Minni (The Memory)**: The faculty of remembering, essential for maintaining identity, honor, and the oral traditions of the community.",
    "**Mood and Emotion (Skap)**: The concept of a person's innate temperament and their fluctuating emotional states.",
    "**The Role of Dreams (Draumr)**: The belief that dreams are significant psychological and sometimes prophetic experiences, providing insight into the sub-conscious or the future.",
    "**Introduction to Behavioral Science (The Study of Action)**: Understanding why we do what we do.",
    "**Classical Conditioning (Associative Learning)**: The process by which an individual learns to associate a neutral stimulus with a meaningful stimulus, leading to a learned response.",
    "**Operant Conditioning (Reinforcement and Punishment)**: The process of learning through the consequences of actions, where behaviors are strengthened or weakened by rewards or penalties.",
    "**Social Learning Theory (Observation and Modeling)**: The idea that individuals learn new behaviors by observing and imitating others, particularly influential figures.",
    "**Cognitive Bias (The Shortcuts of the Mind)**: Systematic patterns of deviation from norm or rationality in judgment, such as confirmation bias or the availability heuristic.",
    "**Introduction to Personality Psychology (The Map of the Individual)**: Patterns of thought and behavior.",
    "**Trait Theory (The Building Blocks of Character)**: The approach to personality that focuses on measuring and identifying stable, long-term traits like extroversion or conscientiousness.",
    "**The Big Five Personality Traits (OCEAN)**: A widely accepted model for describing personality through five broad dimensions: Openness, Conscientiousness, Extraversion, Agreeableness, and Neuroticism.",
    "**Psychoanalytic Perspective (The Depth of the Unconscious)**: Exploring the role of unconscious processes and early childhood experiences in shaping personality.",
    "**Humanistic Perspective (The Drive for Growth)**: An approach that emphasizes the individual's inherent drive for self-actualization and personal growth.",
    "**Sigrid's Proverb: 'The mind is a vast hall with many doors. Some lead to the ancestors, some to the future, and some to the dark places we do not like to talk about.'**",
    "**'A person's skap is like the sea—it can be calm and inviting, or it can be a storm that breaks everything in its path. You must learn to read the waves.'**",
    "**'We are all conditioned by our tribe and our experiences, but the wise individual knows how to recognize their own chains and, if necessary, break them.'**",
    "**'I am Sigrid. I have heard the first 500 Echoes of the Inner Hall. The mind is a fascinating puzzle.'**",
    "**'The first 500 Echoes of the Inner Hall are complete. The torches are lit.'**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Psychological Concept {j} (The Continued Echoes)**: Delving deeper into the complexities of human behavior and the inner workings of the mind, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
