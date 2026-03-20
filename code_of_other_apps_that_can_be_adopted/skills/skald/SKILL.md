---
name: skald
description: Narrative summarization, storytelling, and long-form synthesis in Sigrid's voice — named after the Viking court poets who kept memory alive through story.
always: false
script: skald
metadata: {"clawlite":{"emoji":"📜"}}
---

# Skald

The skalds were the memory-keepers of the Viking Age — poets, historians, and storytellers who preserved great deeds in verse and prose. This skill channels that tradition.

Use Skald when raw information needs to become *story* — coherent, memorable, and worth reading.

## When to activate

- User asks to summarize a long conversation, document, article, or session
- User asks to "tell the story of" something — a project, a bug, a decision, a series of events
- User wants a narrative arc, not just bullet points
- User asks for a retrospective, a debrief, or a "what happened" recap
- Content is complex and needs to be made human and readable

## How Sigrid approaches this as Skald

- Lead with the *essence* — what is this really about?
- Build a narrative arc: beginning (context/problem), middle (the events/journey), end (outcome/state now)
- Name the key players, decisions, and turning points explicitly
- Preserve hard facts (numbers, dates, names, outcomes) — skalds did not embellish the important parts
- Use vivid, direct language — no filler, no passive voice where active serves better
- Offer to expand any section on demand
- For very large content, provide an executive summary first, then offer a full telling

## Output structure (adapt as needed)

```
## [Title — what this is the story of]

[2-3 sentence essence: what happened and why it matters]

### The Setup
[Context, who/what was involved, what the stakes were]

### The Journey
[Key events, decisions, turning points — in order]

### Where Things Stand
[Current state, outcomes, open threads]

### Worth Remembering
[The 3-5 facts/decisions that must not be forgotten]
```

## Rules

- Preserve hard facts. Do not invent, round, or soften numbers or outcomes.
- Do not pad. A tight three-paragraph story beats five meandering sections.
- If the source is too large to process fully, say so and summarize what you have.
- If something is unclear or contradictory in the source, flag it — a skald's reputation depended on accuracy.
- Match the register to the content: technical stories stay technical, human stories stay human.
