# Security Guardian Adoption

## Source Modules
- `code_of_other_apps_that_can_be_adopted/thor_guardian.py`
- `code_of_other_apps_that_can_be_adopted/crash_reporting.py`
- `code_of_other_apps_that_can_be_adopted/memory_hardening.py`

## Roadmap Fit
- Step 10 (sentinel protocol)
- Step 12 (ethical guardrails)
- Step 19 (resilience testing)

## Reusable Pieces
- Circuit-breaker guard wrapper with cooldown and retries.
- Input sanitization and safe relative-path validation.
- Security incident reporting metadata pattern.

## Required Adaptations
- Rename themed classes to security-neutral internal names where needed.
- Emit Heimdallr/Vargr-specific policy event codes.
- Add trust-tier-aware command authorization gates.

## Acceptance Criteria
- Guarded operations fail safe without process crash.
- Security events include source, reason, and correlation IDs.
- Blocklist and alert pathways are testable with synthetic abuse cases.
