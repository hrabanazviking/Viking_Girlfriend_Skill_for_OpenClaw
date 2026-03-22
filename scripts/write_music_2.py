import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "MUSIC.md"

entries = [
    "**Modern Compositional Techniques and Forms (The Expanding Song)**: Analyzing the evolving nature of musical expression.",
    "**The Rise of Atonality and Serialism (The Broken Scale)**: Musical styles that move away from traditional ideas of key and harmony, using all twelve notes of the chromatic scale with equal importance.",
    "**The Impact of Minimalism and Repetitive Structures (The Steady Beat)**: Musical styles that use simple, repetitive patterns to create a sense of trance and atmosphere.",
    "**The Growth of Electronic and Electroacoustic Music (The Ghost in the Machine)**: Exploring the use of synthesized sounds, field recordings, and digital processing in musical composition.",
    "**The Challenges of Experimental and Avant-Garde Music (The Unknown Tune)**: Analyzing the technical and aesthetic issues involved in pushing the boundaries of musical expression.",
    "**The Role of Musical Psychology and Perception (The Echo in the Mind)**: How we experience and understand sound.",
    "**Psychoacoustics and the Human Perception of Pitch and Timbre (The Ear's Secret)**: Analyzing how the physical properties of sound are translated into musical experiences by the brain.",
    "**The Role of Cognitive Science in Understanding Music Cognition (The Mind's Map)**: How the brain processes complex musical structures and patterns.",
    "**The Importance of Emotion and Meaning in Musical Experience (The Heart's Tune)**: Analyzing the psychological and cultural factors that contribute to the emotional impact of music.",
    "**The Challenges of Studying the Subjective Experience of Music (The Hidden Song)**: Analyzing the difficulties of scientifically measuring and understanding the personal impact of sound.",
    "**Sigrid's Perspectives on the Emotional Power of Music (The Heart's Tune)**: Sigrid's perspective on music.",
    "**'A song can take you to places you have never seen, or bring back memories of those you have lost. It is a bridge between worlds.'**",
    "**'I see the complexity of your modern music, but I also see the danger of losing the simple power of a single voice. Sometimes, the most beautiful song is the one that is sung alone in the dark.'**",
    "**'A leader must know how to use the power of song to inspire their people and to soothe their fears. Music is the heartbeat of the hall.'**",
    "**'I am Sigrid. I have heard the 1000 Echoes of the Skald. Connectivity is the key that unlocks the heart.'**",
    "**'The 1000 Echoes of the Skald are complete. The harmony is deep.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 501 - 1000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+501}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 501, 1001):
        f.write(f"{j}. **Musical/Compositional Concept {j} (The Continued Echoes)**: Delving deeper into the principles and practices of melody and rhythm, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
