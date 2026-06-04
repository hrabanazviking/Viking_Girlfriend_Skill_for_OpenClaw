# Static Analysis and Bug Report (2026-06-04)

## Security Issues Identified (Bandit)

### CWE-22: B310 - Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line:** `27`
- **Severity:** `MEDIUM`
- **Confidence:** `HIGH`
- **Snippet:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen
- **Resolution/Recommended Change:**
  - Validate the URL scheme before calling `urlopen` to ensure it begins with `http://` or `https://`.
  - Specifically, in `viking_girlfriend_skill/data/knowledge_reference/populate.py`, verify `url.startswith('https://')` to prevent Server-Side Request Forgery (SSRF) and Local File Inclusion (LFI) via alternative schemes like `file://` or `ftp://`.
  - After validating the URL, you can append `# nosec B310` to the `urlopen` line to suppress the Bandit warning, per the system guidelines.
  - Example:
    ```python
    if not url.startswith('https://'):
        raise ValueError('Invalid URL scheme')
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response:  # nosec B310
        # ...
    ```

### CWE-22: B310 - Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line:** `62`
- **Severity:** `MEDIUM`
- **Confidence:** `HIGH`
- **Snippet:**
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen
- **Resolution/Recommended Change:**
  - Validate the URL scheme before calling `urlopen` to ensure it begins with `http://` or `https://`.
  - Specifically, in `viking_girlfriend_skill/data/knowledge_reference/populate.py`, verify `url.startswith('https://')` to prevent Server-Side Request Forgery (SSRF) and Local File Inclusion (LFI) via alternative schemes like `file://` or `ftp://`.
  - After validating the URL, you can append `# nosec B310` to the `urlopen` line to suppress the Bandit warning, per the system guidelines.
  - Example:
    ```python
    if not url.startswith('https://'):
        raise ValueError('Invalid URL scheme')
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response:  # nosec B310
        # ...
    ```

## Research Data

### CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
When applications pass user-controlled input directly to file-handling APIs (or URL openers capable of resolving local file URIs like `urllib.request.urlopen` in Python), an attacker can supply paths containing `../` or schemes like `file://` to access files outside the intended directory or interact with internal network resources (SSRF).

### Bandit B310
The `urllib.request.urlopen` function in Python is vulnerable to SSRF and LFI if the URL scheme is not strictly validated. It can open local files using the `file://` scheme, or interact with arbitrary protocols if custom handlers are registered.

## Linting and Code Quality (Flake8 & Pylint)

### Unused Imports
- `viking_girlfriend_skill/data/knowledge_reference/populate.py:5`: `sys` imported but unused.
- `viking_girlfriend_skill/scripts/bio_engine.py:27`: `dataclasses.field` imported but unused.
- `viking_girlfriend_skill/scripts/config_loader.py:20`: `dataclasses.field` imported but unused.
- `viking_girlfriend_skill/scripts/cove_pipeline.py:37`: `os` imported but unused.
- `viking_girlfriend_skill/scripts/cove_pipeline.py:39`: `time` imported but unused.
- `viking_girlfriend_skill/scripts/cove_pipeline.py:44`: `typing.Union` imported but unused.

### Formatting and Style Issues
- Multiple PEP 8 violations in `viking_girlfriend_skill/data/knowledge_reference/populate.py` (e.g., expected 2 blank lines, blank line contains whitespace, missing spaces before inline comments).
- `viking_girlfriend_skill/scripts/wyrd_matrix.py` has multiple issues: lines too long (>100 characters), too many lines in module (>1000), too many nested blocks, too many instance attributes, attributes not conforming to snake_case (`DECAY_PER_TURN`, etc.), and catching too general exceptions (`Exception`).
