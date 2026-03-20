# Roadmap Step 13 Import Plan

## Import Order
- 1. `code_of_other_apps_that_can_be_adopted/memory_system.py` - Session memory data model.
- 2. `code_of_other_apps_that_can_be_adopted/enhanced_memory.py` - Summarization pipeline.
- 3. `code_of_other_apps_that_can_be_adopted/character_memory_rag.py` - Indexed memory retrieval.
- 4. `code_of_other_apps_that_can_be_adopted/memory_query_engine.py` - Selective memory querying.

## Adapter Notes
- Keep imports behind adapter boundaries in target modules.
- Preserve deterministic behavior and typed outputs.
- Remove game-specific assumptions during adaptation.

## Validation Gate
- Unit coverage for imported logic paths.
- Integration coverage against state bus and prompt contracts.
- Security and logging checks pass before enabling by default.