# Security Scan Report - 2026-05-11

## Findings

A static application security testing (SAST) scan using Bandit was performed on the codebase. The scan identified the following security vulnerability:

### Bandit B310: Server Side Request Forgery (SSRF) / Path Traversal

*   **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
*   **Lines:** 27, 62
*   **Severity:** Medium
*   **Confidence:** High
*   **Issue:** Audit url open for permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected.

#### Details

The `urllib.request.urlopen` function is used to fetch data from Wikipedia API. While the URL is constructed to point to `en.wikipedia.org`, directly passing variables to `urlopen` without explicit scheme validation can lead to vulnerabilities if the URL is ever modified to accept user input or external configuration.

According to [DeepSource BAN-B310 documentation](https://deepsource.com/directory/python/issues/BAN-B310), `urllib` not only opens `http://` or `https://` URLs, but also `ftp://` and `file://`. This means that if an attacker could control the URL, they might be able to open local files on the executing machine (Path Traversal/Local File Inclusion) or force the server to make requests to internal network resources (Server Side Request Forgery - SSRF).

#### Recommended Code Changes

Although the current implementation is not immediately exploitable due to the hardcoded base URLs, it is a best practice to explicitly validate the URL scheme before making the request. In addition, as per project guidelines for false positives or verified static URLs, the warning should be suppressed using `# nosec B310`.

**Implementation details to address the vulnerability:**

1.  Validate that the URL starts with `http://` or `https://`.
2.  Append `# nosec B310` to the `urlopen` call to suppress the Bandit warning.

**Example Code Change for `populate.py` (Line 27 & 62):**

```python
<<<<<<< SEARCH
        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
=======
        while True:
            try:
                if not url.lower().startswith(('http://', 'https://')):
                    raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are permitted.")

                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
>>>>>>> REPLACE
```

*(Note: The exact same validation pattern should be applied to the second occurrence at line 62.)*
