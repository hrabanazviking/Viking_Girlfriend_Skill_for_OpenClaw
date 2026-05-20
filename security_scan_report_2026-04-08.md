# Security Scan Report: 2026-04-08

## Overview
A comprehensive static application security testing (SAST) scan was performed using Bandit.

## Findings & Resolutions

### B310: SSRF / Path Traversal in `urllib.request.urlopen`
- **Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Description:** Bandit detected the use of `urllib.request.urlopen` without explicitly allowing permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected and can lead to Server-Side Request Forgery (SSRF) or Path Traversal vulnerabilities.
- **Resolution:** Modified the script to explicitly check that the URL starts with `http://` or `https://` before performing the request. A ValueError is raised if an invalid scheme is detected. Added the `# nosec B310` comment to suppress the Bandit warning after adding the validation, conforming to project rules.

### Low Severity Issues
- Multiple instances of `B101: assert_used` were found across the codebase, primarily in test files (`tests/test_vordur_trigger.py`, `tests/test_wyrd_vitality_modulation.py`). These are acceptable within test suites as they are not compiled to optimised byte code where asserts are removed.
- Multiple `B324: hashlib` nosec comments were identified in `viking_girlfriend_skill/scripts/vordur.py` (e.g., md5 used for caching keys, not cryptographic purposes). These are appropriately documented.

## Conclusion
The identified B310 issues have been patched, ensuring external data fetching is restricted to safe HTTP/HTTPS schemes. The remaining issues are low severity and acceptable given their context (testing/caching).
