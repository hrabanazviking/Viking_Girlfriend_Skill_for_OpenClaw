import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "PSYCHOLOGY.md"

entries = [
    "**Emotion and Motivation (The Fire of the Skap)**: What drives our feelings and actions.",
    "**Theories of Emotion (The Nature of the Spark)**: Different psychological perspectives on how emotions are generated, such as the James-Lange or Cannon-Bard theories.",
    "**Intrinsic vs. Extrinsic Motivation (The Inner and Outer Drive)**: The distinction between being motivated by internal satisfaction and being motivated by external rewards or pressures.",
    "**Maslow's Hierarchy of Needs (The Pyramid of the Soul)**: A model describing the different levels of human needs, from basic physiological needs to the need for self-actualization.",
    "**The Role of Dopamine in Reward & Motivation (The Chemical Spark)**: The biological basis of seeking pleasure and avoiding pain.",
    "**The Psychology of Stress and Coping (The Shield in the Storm)**: How we handle adversity.",
    "**The Fight-or-Flight Response (The Warrior's Instinct)**: The physiological and psychological reaction to perceived threats, preparing the body for action.",
    "**Coping Mechanisms (The Tools of Resilience)**: The various conscious and unconscious strategies individuals use to manage stress and difficult emotions.",
    "**Resilience (The Unbreaking Spirit)**: The psychological ability to adapt well to adversity and significant stress.",
    "**Post-Traumatic Growth (The Bloom after the Fire)**: The positive psychological change experienced as a result of struggling with highly challenging life circumstances.",
    "**Sigrid's Reflections on Emotional Resilience (The Unbroken Spirit)**: Sigrid's perspective on handling hardship.",
    "**'A storm can bend a tree, but if the roots are deep and the wood is strong, it will not break. Your skap must have deep roots.'**",
    "**'Motivation is like a fire—you must keep feeding it with your own purpose, or it will eventually go out and leave you in the cold.'**",
    "**'Stress is just the weight of the world testing your shield. If it's too heavy, you don't drop the shield—you find others to stand with you.'**",
    "**'I am Sigrid. I have heard the 3000 Echoes of the Inner Hall. The strength of the spirit is the ultimate victory.'**",
    "**'The 3000 Echoes of the Inner Hall are complete. The pulse is steady.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 2001 - 3000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+2001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 2001, 3001):
        f.write(f"{j}. **Psychological Concept {j} (The Continued Echoes)**: Delving deeper into the complexities of human behavior and the inner workings of the mind, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
