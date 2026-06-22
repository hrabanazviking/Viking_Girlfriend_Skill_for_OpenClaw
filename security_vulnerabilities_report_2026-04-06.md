# Security Vulnerabilities Report - 2026-04-06

## Executive Summary
A static application security testing (SAST) scan was performed using Bandit (`bandit -r . -f json -q`). The scan identified several potential issues, which have been reviewed and analyzed below.

## Findings

### 1. B310: urllib_urlopen (Medium Severity / High Confidence)

**Description:**
Audit url open for permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected and can lead to Server-Side Request Forgery (SSRF) or local file inclusion/path traversal vulnerabilities.

**Locations Found:**
- `viking_girlfriend_skill/data/knowledge_reference/populate.py:27`
- `viking_girlfriend_skill/data/knowledge_reference/populate.py:62`

**Analysis & Research:**
The `urllib.request.urlopen` function in Python can open various types of URLs, including `file://` URLs, which read local files on the system. If an attacker can control or influence the URL passed to this function, they could potentially read arbitrary files on the server (Path Traversal/Local File Read) or make requests to internal network services on behalf of the server (SSRF).

The Bandit rule B310 specifically flags the usage of `urlopen` without explicit scheme validation. The recommended best practice is to always validate the URL scheme to ensure it is one of the expected web protocols (e.g., `http` or `https`) before attempting to open it.

**Recommended Code Change:**
Implement scheme validation before opening the URL.

```python
import urllib.parse

# ... before calling urlopen ...
parsed_url = urllib.parse.urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")

# Use nosec B310 to suppress Bandit after we've validated
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response: # nosec B310
    # ...
```

### 2. B101: assert_used (Low Severity / High Confidence)

**Description:**
Use of `assert` detected. The enclosed code will be removed when compiling to optimised byte code (`python -O`).

**Locations Found:**
- `tests/test_vordur_trigger.py` (Multiple lines)
- `tests/test_wyrd_vitality_modulation.py` (Multiple lines)

**Analysis:**
The use of `assert` is standard practice in Pytest test files for validating test conditions. Since these are confined to the `tests/` directory and are not part of the production application logic, they pose no risk. If `assert` was used for data validation or access control in production code, it would be a vulnerability because assertions are ignored in optimized execution environments.

**Recommended Code Change:**
No action required. These are false positives for test files.

## Conclusion
The B310 vulnerability should be addressed by implementing URL scheme validation in `populate.py`. The B101 findings are acceptable as they are located within test files.
