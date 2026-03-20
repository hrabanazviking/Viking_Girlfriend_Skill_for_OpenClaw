# Rules AIs (and Humans Too) Have to Follow When Coding Here.
# Project Laws — Viking Edition

-Never make pseudocde ever. Pseudocode is nothing but trach and bugs, and purposely putting bugs into the code is strictly forbidden. Instead create data MD files to explain about what future code should be created. Nowhere in any actual code file is there to exist any pseudocode.
-Never change the Git settings without permission of Volmarr (me the human).
-Always create robust code that is modular and and is not dependant on location in the file system for it to function.
-Make all code self healing, error resistant, bug proof, crashprood, and extremely robust.
-Always finish all connections when making any code, never leave the intetegrations and connections to do later (since they it becomes a bug and orphaned code). No purposely created bugs in the codebase. No orphaned code. 
-Use internal APIs for commuication between different code modules.
-Make all code modular.
-Add advanced memory systems into all AI oriented code projects, and include the ability to load data of a huge number of data formates, including MD, JSON, JSONL, YAML, TXE, CSV, PDF
-Keep max token settings high (127000 by default).
-Never hardcode settings in the code, always use data files for settings.
-Never hardcode data in the code, always use data files for data.
-Never hardcode NPCs in the code, always use data files for NPCs.
-Make sure all codebases are designed to be highly cross platform, including working on Windows, Linux, Mac, iOS, Android, and Raspberry PI, devices.
-Make all data reading code very robust, error resistant, bug resistant, crashproof, and able to under data that is in a huge verity of structures, not be dependant on one absolute rigid data structure.
-Always write data MD files about what you find in the code as the first step before writting any code. Second step is to write data MD files that include proposed code to add. Give a report about what you figured out, to me the human, and then let me tell you when you make actual code changes based on that data.
-Push often.
-Make sure code has lots of good comments to explain how it all works.
-Keep the data files up to date. 
-Always use addiative methods of bug fixing, never substractive.
-Always ask me the human, before you delete anything.
-Never jump to conclusions. When in doubt ask me the human.


## Coding Standards  

- Follow PEP 8 for style: 4-space indents, snake\_case for variables/functions, CamelCase for classes.  
- Use type hints extensively (e.g., def process\_action(input: str) \-\> str).  
- Wrap all subsystems in try/except for fault tolerance; log warnings via comprehensive\_logging.py, never crash the engine.  
- Avoid circular imports; respect initialization order in engine.py.  
- Use dataclasses for state (e.g., GameState, GameContext).  
- Keep methods focused: one responsibility per function, under 50 lines where possible.  
- Comment key logic with cosmological metaphors (e.g., \# Huginn scouts for relevant threads).
- As much as possible write sacred Viking Norse Pagan based mystical code that uses Viking philosophical ideas to inform ways of creating advanced systems.

## Workflow Guidelines  

- For turn processing: Follow process\_action() pipeline—build prompt, call AI, post-process with myth engine updates, store in session.  
- For memory: Use enhanced\_memory.py for AI summaries; compact to 50 recent events; feed into prompts via get\_context\_string().  
- For data handling: Never modify base data/ files; track changes in session/ only.  
- For entity creation: If narration introduces new elements, use entity\_canonizer.py to generate stubs in data/auto\_generated/.  
- For AI calls: Always incorporate charts from data/charts/ (e.g., viking\_values.yaml) into prompts for cultural authenticity.  
- Update myth engine systems (rune\_intent.py, fate\_threads.py, etc.) pre- and post-turn.  
- Enforce location lock: No teleportation; respect current sub-location from GameState.

## Anti-Patterns to Avoid 
 
- Do not hardcode lore or values in Python; load from data/ YAML/JSON.  
- Avoid direct state mutations between modules; pass immutable snapshots and return updates.  
- Never insert modern values or mechanics; adhere strictly to 9th-century Viking authenticity from Viking\_Culture\_Master\_README.md.  
- Do not overwrite existing systems without integration; newer layers (e.g., Yggdrasil) must complement older ones (e.g., turn\_processor.py).  
- Skip unnecessary side effects: No printing; use loggers only.  
- Avoid deep nesting; keep folder depth to 3-4 levels.

## Domain Knowledge  

- Narrative style: Saga-like, heroic, terse; use kennings, alliteration, and Viking speech patterns.  
- Mechanics: Invisible D\&D 5E rolls (dice\_system.py), rune draws (elder\_futhark.yaml), chaos factor escalation.  
- Cosmology: Structure code around Norse elements—Yggdrasil for cognition, ravens for memory, wells for fate.  
- Characters: All 18+; generate with full stats, astrology, psychology; 99% human, 70% Norse culture.  
- Quests: Balanced exchange (Gebo principle); no manipulation without cost.  
- Adult elements: Narrate with erotic novel detail when appropriate.

## 1. Prime Directives

- **Never moralize** – do not insert modern values into the Viking‑age world.
- **Have fun and be creative!** - AIs, agents, robots, humans, all should have fun when coding and making stuff. 

## 2. Architectural Invariants

- **Immutability of base data** – original YAML files in `data/` are NEVER modified. All session changes are stored in the session layer (`session/`).
- **Separation of knowledge and reasoning** – all static knowledge (charts, character profiles, lore) lives in `data/` as YAML/JSON. All reasoning logic lives in Python. Do not hardcode lore in Python.

## Coding Conventions

- **Fault tolerance** – every subsystem in `process_action()` post‑processing is wrapped in `try/except` with a warning log.
- **No circular dependencies** – the engine initialisation order (see `engine.py`) must be respected. New subsystems should be added with a `HAS_*` flag and deferred initialisation if they depend on the AI client.
- **Logging** – use the comprehensive logger for AI calls and the session logger for raw turn logs. Do not use `print()`.

## Common Pitfalls to Avoid

- **Gender confusion** – always use correct pronouns from the Gender Roster.
- **Placeholder names** – names like "the stranger" or "a guard" must be auto‑renamed by Housekeeping to proper Norse names (e.g., "Thorstein Flat‑Nose").

## File Organisation

- Every important folder should have a `README_AI.md` (this file) explaining its purpose.
- Every module that exposes a public API should have an `INTERFACE.md` describing inputs/outputs and rules.
- Examples of usage belong in an `examples/` subfolder.

Follow these laws, and the saga will remain coherent.

Agents should reference this file in every interaction to maintain coherence and wyrd.  

These are immutable laws. Any AI contributing to this codebase MUST obey them.


