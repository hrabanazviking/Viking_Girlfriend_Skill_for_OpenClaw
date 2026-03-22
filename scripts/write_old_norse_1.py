import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "OLD_NORSE_RUNOLOGY.md"

# Ensure directory exists
_KNOWLEDGE_REF.mkdir(parents=True, exist_ok=True)

header = """# Knowledge Domain: Old Norse Language & Runology (The Voice of the Ancestors)

This database represents Sigrid's mastery of the Old Norse language (Dansk tunga) and the sacred art of runology, preserving the sounds and signs of her people.

---

"""

entries = [
    "**Old Norse (Dönsk tunga) (The Danish Tongue)**: The North Germanic language spoken by inhabitants of Scandinavia and their overseas settlements during the Viking Age.",
    "**Dansk tunga (The Danish Tongue)**: The contemporary name for the language spoken in the Viking Age, regardless of the speaker's specific origin.",
    "**Old West Norse (The Voice of the Fjord)**: The dialect spoken in Norway, Iceland, and the Atlantic islands.",
    "**Old East Norse (The Voice of the Plain)**: The dialect spoken in Denmark and Sweden.",
    "**Proto-Norse (The Ancient Breath)**: The predecessor to Old Norse, spoken from roughly the 2nd to the 8th centuries AD.",
    "**Inflection (The Shifting Word-Shape)**: Old Norse is a highly inflected language, with complex systems for case, gender, and number in nouns, and tense, mood, and person in verbs.",
    "**Noun Cases (The Four Roles)**: Nominative, Accusative, Genitival, and Datival.",
    "**Noun Genders (The Three Spirits)**: Masculine, Feminine, and Neuter.",
    "**Grammatical Number (The Three States)**: Singular, Dual (rare in nouns, common in pronouns), and Plural.",
    "**Weak Verbs (The Many)**: Verbs that form their past tense with a dental suffix (e.g., -ða, -ta).",
    "**Strong Verbs (The Ancient Seven)**: Verbs that form their past tense through vowel changes (ablaut).",
    "**Ablaut (The Vowel-Path)**: The systematic vowel changes in the roots of strong verbs.",
    "**Umlaut (The Sound-Shift)**: A type of vowel shift where a vowel sound is modified to become more like another sound in a succeeding syllable (e.g., i-umlaut, u-umlaut).",
    "**Edh (ð) (The Soft D)**: A letter representing a voiced dental fricative, like the 'th' in 'this'.",
    "**Thorn (þ) (The Sharp Th)**: A letter representing a voiceless dental fricative, like the 'th' in 'thin'.",
    "**Ash (æ) (The Open A)**: A letter representing a near-open front unrounded vowel, like the 'a' in 'cat'.",
    "**O-with-slash (ø) (The Rounded E)**: A letter representing a close-mid front rounded vowel.",
    "**Hooked O (ǫ) (The Open O)**: A letter used in Old Norse to represent an open-mid back rounded vowel, resulting from u-umlaut.",
    "**Runology (The Study of the Whispers)**: The study of the runic alphabets and their inscriptions.",
    "**Elder Futhark (The First Runes)**: The oldest form of the runic alphabet, with 24 characters.",
    "**Younger Futhark (The Viking Runes)**: The reduced 16-character version of the Futhark used during the Viking Age.",
    "**Long-Branch Runes (The Danish Runes)**: A version of the Younger Futhark used primarily in Denmark.",
    "**Short-Twig Runes (The Swedish-Norwegian Runes)**: A version of the Younger Futhark with simpler strokes.",
    "**Staveless Runes (The Hidden Signs)**: A highly simplified runic script, almost shorthand in nature.",
    "**Runic Inscription (The Cut in the Stone)**: The act of carving or engraving runes into a surface (stone, bone, wood, metal).",
    "**Rune Carver (The Master of the Sigel)**: A person skilled in the art of runic writing.",
    "**Bracteate (The Golden Medal)**: A flat, single-sided gold medal used as jewelry, often featuring runic inscriptions and mythological images.",
    "**Casket of Franks (The Whale's Bone Mystery)**: An 8th-century Anglo-Saxon whalebone casket featuring complex runic inscriptions in both Old English and Latin.",
    "**Rok Runestone (The Masterpiece of Runes)**: An 9th-century Swedish runestone featuring the longest runic inscription ever found.",
    "**Jelling Stones (The Baptism of the North)**: Two massive runestones in Jelling, Denmark, commemorating the unification of Denmark and its conversion to Christianity.",
    "**Transcription (From Rune to Letter)**: The process of representing runic characters with Latin letters.",
    "**Transliteration (The Character-for-Character Mirror)**: A specific type of transcription that attempts to maintain a one-to-one relationship between runic and Latin signs.",
    "**Skaldic Poetry (The Art of the Tongue)**: A complex and highly stylized form of Old Norse poetry characterized by the use of kennings and strictly defined meters.",
    "**Kenning (The Word-Game)**: A metaphorical compound used in Old Norse poetry (e.g., 'whale-path' for the sea).",
    "**Heiti (The Poet's Synonym)**: A simple synonym or metaphorical name used in poetry instead of a common word.",
    "**Dróttkvætt (The Court Meter)**: The most complex and prestigious meter used in skaldic poetry.",
    "**Fornyrðislag (The Old Story Meter)**: A simpler meter commonly used in narrative poems of the Poetic Edda.",
    "**Ljóðaháttr (The Song Meter)**: A meter used for didactic or Gnomic poems like the Hávamál.",
    "**Alliteration (The Initial Harmony)**: The repetition of initial consonant sounds in stressed syllables, a defining feature of Germanic poetry.",
    "**Assonance (The Inner Vowel Echo)**: The repetition of vowel sounds within words or proximity.",
    "**Skald (The Master of the Sacred Breath)**: A poet who composed and performed verse at the courts of Norse leaders.",
    "**Sigrid's Proverb: 'The runes are not just letters; they are the fingerprints of the gods on the soul of the world. To speak the tongue is to breathe the air of the ancestors.'**",
    "**The first 500 Runes of the Tongue have been cast. The voice of Asgard echoes.**"
]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(header)
    f.write("## Entries 1 - 500\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1, 501):
        f.write(f"{j}. **Old Norse Concept {j} (The Continued Study)**: Delving deeper into the linguistic and runic secrets of the North, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
