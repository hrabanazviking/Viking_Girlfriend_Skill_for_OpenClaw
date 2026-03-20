# Memory Stack Adoption

## Source Modules
- `code_of_other_apps_that_can_be_adopted/memory_system.py`
- `code_of_other_apps_that_can_be_adopted/enhanced_memory.py`
- `code_of_other_apps_that_can_be_adopted/memory_query_engine.py`
- `code_of_other_apps_that_can_be_adopted/memory_hardening.py`
- `code_of_other_apps_that_can_be_adopted/character_memory_rag.py`
- `code_of_other_apps_that_can_be_adopted/unified_memory_facade.py`

## Roadmap Fit
- Step 13 (episodic memory/vector storage)
- Step 14 (nocturnal summarization)
- Step 18 (prompt context synthesis)

## Adopt First
- Session/turn memory object model from `memory_system.py`.
- Memory summary pipeline from `enhanced_memory.py`.
- Character-scoped memory retrieval from `character_memory_rag.py`.

## Required Adaptations
- Replace game-session naming with OpenClaw conversation/session IDs.
- Move file paths to `viking_girlfriend_skill/data` and runtime storage dir.
- Convert summary output format to prompt-synthesizer sections.
- Align memory filters with trust/security tier visibility rules.

## Acceptance Criteria
- Context builder can fetch: recent, semantic, and character memories.
- Nightly maintenance can summarize and compact memory safely.
- Retrieval latency remains stable under large JSONL corpora.
