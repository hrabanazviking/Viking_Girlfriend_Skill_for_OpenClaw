# Security Scan Report: Bandit SAST Findings
**Date:** 2026-05-20

## Summary
A static application security testing (SAST) scan was performed using Bandit (`bandit -r . -f json -q`). Several findings were identified:

1.  **Multiple B101 (assert_used) Warnings in Test Files:**
    *   `tests/test_vordur_trigger.py`
    *   `tests/test_wyrd_vitality_modulation.py`
    *   *Analysis:* Bandit flags the `assert` statement because Python removes assertions when compiling to optimized byte code (using `-O`). In test files, this is typically acceptable behavior (as `pytest` heavily relies on assertions). However, to adhere strictly to security best practices and avoid test bypasses in optimized environments, standard assertions can be replaced with `pytest` utilities or standard exception raising if needed outside of a test framework. Given these are specifically unit tests for `pytest`, they are generally low-risk.

2.  **Two B310 (urllib_urlopen) Warnings in `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**
    *   *Location:* Lines 27 and 62
    *   *Analysis:* The script uses `urllib.request.urlopen(req)` to fetch data from Wikipedia APIs. Bandit flags this because `urlopen` can potentially open `file://` or custom schemes if the URL is user-controlled, leading to Server-Side Request Forgery (SSRF) or Local File Inclusion (LFI).
    *   *Research Findings:* According to DeepSource and OWASP (CWE-918), `urllib` can open not only `http://` or `https://` URLs but also `ftp://` and `file://`. If a URL is manipulated by an external user, it can lead to Server Side Request Forgery (SSRF). Attackers might make requests on the internal network or access local files. The recommended mitigation is to explicitly validate the URL scheme (e.g., checking if it starts with `http://` or `https://`) before opening it with `urllib.request.urlopen()`.

## Recommended Code Changes

### Fix B310 in `populate.py`
To mitigate the B310 warning and prevent potential SSRF/LFI (CWE-918), we should explicitly validate that the URL uses the `https://` scheme before making the request.

**Modifications in `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**

1.  *Line 27 (inside `fetch_category_members`):*
    ```python
    <<<<<<< SEARCH
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
    =======
            try:
                if not url.startswith("https://"):
                    raise ValueError(f"Invalid URL scheme. Only HTTPS is allowed: {url}")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
    >>>>>>> REPLACE
    ```

2.  *Line 62 (inside `fetch_extracts_in_batches`):*
    ```python
    <<<<<<< SEARCH
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
    =======
        try:
            if not url.startswith("https://"):
                raise ValueError(f"Invalid URL scheme. Only HTTPS is allowed: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
    >>>>>>> REPLACE
    ```

*Note on B101:* Modifying test file assertions is generally unnecessary unless mandated by strict compliance policies, as the project uses `pytest`. No changes to test files are recommended at this time to avoid disruption to the test suite logic.
