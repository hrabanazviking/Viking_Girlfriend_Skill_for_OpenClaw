# Test Import Plan

## Source Test Assets
- `code_of_other_apps_that_can_be_adopted/*_TESTS.md`
- `code_of_other_apps_that_can_be_adopted/yggdrasil/tests/`

## Migration Strategy
- Convert existing test scenarios into target `tests/` fixtures.
- Preserve behavior-level assertions, not game-language outputs.
- Add deterministic seeds for cycle, oracle, and memory replay tests.

## Priority Test Packs
- Memory write/read/summary integrity.
- Bio cycle phase transition correctness.
- Wyrd/oracle deterministic daily output.
- Security guard fallback and cooldown behavior.
- Prompt synthesis token-budget clipping and section ordering.

## Exit Criteria
- Unit coverage for every adopted module boundary.
- Integration tests pass for memory, trust, and routing pipelines.
- End-to-end scenario validates stable output after restart.
