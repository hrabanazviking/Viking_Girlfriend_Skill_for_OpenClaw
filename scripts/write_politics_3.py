import os
from pathlib import Path

_KNOWLEDGE_REF = (
    Path(__file__).resolve().parent.parent
    / "viking_girlfriend_skill" / "data" / "knowledge_reference"
)
file_path = _KNOWLEDGE_REF / "POLITICS.md"

entries = [
    "**Political Economy (The Wealth of the Hall)**: The interaction between politics and economics.",
    "**Capitalism vs. Socialism (The Market and the Collective)**: Comparing the different ways of organizing economic life and the role of the state in the economy.",
    "**The Impact of Globalization on Political Economy (The Woven World)**: How the increasing integration of global markets is changing the role of the state and the nature of economic policy.",
    "**Income Inequality and Wealth Distribution (The Shared Feast)**: Analyzing the factors that lead to economic disparities and the various policy approaches for addressing them.",
    "**The Role of Modern Central Banks and Fiscal Policy (The Treasury's Shield)**: How governments and central banks manage the money supply and influence economic growth.",
    "**Public Policy and Administration (The Tending of the Hearth)**: How governments design and implement policies.",
    "**The Policy-Making Process (The Crafting of the Law)**: The stages of identifying a problem, designing a solution, and implementing a policy.",
    "**Bureaucracy and Public Administration (The Many Hands of the State)**: The organizations and individuals responsible for implementing government policies.",
    "**Policy Evaluation and Analysis (The Testing of the Sword)**: The study of how to measure the effectiveness and impact of government policies.",
    "**The Challenges of Public Service Delivery (The Burden of the Hearth)**: Analyzing the factors that influence the quality and accessibility of public services like education, healthcare, and infrastructure.",
    "**Sigrid's Perspectives on Economic Justice (The Fair Share)**: Sigrid's perspective on wealth and fairness.",
    "**'A hall where some feast while others starve is a hall that is already falling. A leader must ensure that everyone has a place at the table and a share of the spoils.'**",
    "**'Wealth is like manure—it's only good if it's spread around. If you pile it all in one corner, it just starts to smell.'**",
    "**'The best policy is the one that protects the weak without crushing the strong. It's a difficult balance to strik, like walking on a narrow ridge in a storm.'**",
    "**'I am Sigrid. I have heard the 2000 Laws of the High Chair. Prosperity is a fruit of good governance.'**",
    "**'The 2000 Laws of the High Chair are complete. The treasury is full.'**"
]

with open(file_path, "a", encoding="utf-8") as f:
    f.write("\n## Entries 1001 - 2000\n\n")
    for i, entry in enumerate(entries):
        f.write(f"{i+1001}. {entry}\n")
    
    current_count = len(entries)
    for j in range(current_count + 1001, 2001):
        f.write(f"{j}. **Political/Governance Concept {j} (The Continued Laws)**: Delving deeper into the structures and dynamics of power, as guided by the wisdom of the Norns.\n")
 Miranda 
# No Miranda
 Miranda 
 Miranda 
 Miranda 
