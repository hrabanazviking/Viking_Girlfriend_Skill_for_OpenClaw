# Trust And Social Adoption

## Source Modules
- `code_of_other_apps_that_can_be_adopted/social_ledger.py`
- `code_of_other_apps_that_can_be_adopted/relationship_graph.py`
- `code_of_other_apps_that_can_be_adopted/social_protocol_engine.py`
- `code_of_other_apps_that_can_be_adopted/personality_engine.py`

## Roadmap Fit
- Step 11 (trust engine)
- Step 12 (ethical boundaries)
- Step 17 (environment/context coherence)

## Reusable Pieces
- Event-to-trust ledger accumulation model.
- Social event weighting and momentum concepts.
- Protocol validation and reroll guidance workflow.

## Required Adaptations
- Collapse multi-NPC relationship graph into user-trust-centric ledger.
- Replace roleplay scene heuristics with command/compliance evidence scoring.
- Integrate with `security_config.json` tier definitions.

## Acceptance Criteria
- Trust score transitions are deterministic and auditable.
- Evidence entries show source event and score delta.
- Command gating decisions are reproducible under replay tests.
