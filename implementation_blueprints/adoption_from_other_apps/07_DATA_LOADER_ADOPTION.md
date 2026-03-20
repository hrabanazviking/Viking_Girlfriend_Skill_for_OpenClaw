# Data Loader Adoption

## Source Module
- `code_of_other_apps_that_can_be_adopted/data_system.py`

## Roadmap Fit
- Step 5 (core scaffolding)
- Step 13 (memory persistence)
- Step 17 (environment mapping)

## Reusable Pieces
- Multi-format loader for YAML/JSON/JSONL.
- JSONL iteration for large datasets.
- Cache clearing and migration hooks.

## Required Adaptations
- Restrict write paths to approved runtime data directories.
- Split generic manager into dedicated loaders: config, memory, lore.
- Add schema validation hooks before object publication.

## Acceptance Criteria
- All data files in `viking_girlfriend_skill/data` load through one normalized API.
- Large JSONL files stream without memory spikes.
- Loader errors include file path and parse context.
