# Security Scan Report: B310 URL Open Vulnerability

## Date
2026-04-25

## Overview
A Bandit scan was conducted on the project codebase, which identified medium severity security issues related to the use of `urllib.request.urlopen` in `viking_girlfriend_skill/data/knowledge_reference/populate.py`.

## Findings
The Bandit scan flagged two instances of potential Server-Side Request Forgery (SSRF) / Local File Inclusion vulnerabilities due to unvalidated URL schemes.

### Issue Details
*   **Test ID:** B310
*   **Issue:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
*   **Severity:** MEDIUM
*   **Confidence:** HIGH
*   **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
*   **Lines:** 27, 62
*   **More Info:** [Bandit B310 Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen)

## Vulnerability Analysis (SSRF / Unvalidated URL Scheme)
When using functions like `urllib.request.urlopen`, Python attempts to fetch the resource provided in the URL. If the URL is dynamically constructed and not strictly validated to ensure it uses an expected scheme (like `http://` or `https://`), an attacker could potentially trick the application into fetching local files using the `file://` scheme, or interacting with internal network resources (SSRF).

In `populate.py`, the URLs are constructed using the `current_cat` variable, which is derived from the Wikipedia API response. While the base domain `https://en.wikipedia.org` is hardcoded, it is best practice to validate the full URL string before calling `urlopen` to prevent any potential bypasses or unexpected behavior, especially if the script is ever modified to accept user input or read from untrusted sources.

## Recommended Code Changes
To remediate this issue, the URL should be validated to ensure it starts with either `http://` or `https://` before being passed to `urllib.request.urlopen`. If the scheme is valid, we can suppress the Bandit warning using `# nosec B310` as per project guidelines.

### Proposed Fix for `viking_girlfriend_skill/data/knowledge_reference/populate.py`

Modify `fetch_category_members` (around line 27):
```python
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{urllib.parse.quote(current_cat)}&cmlimit=500&format=json"

        while True:
            try:
                if not url.startswith(('http://', 'https://')):
                    raise ValueError(f"Invalid URL scheme: {url}")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response: # nosec B310
                    data = json.loads(response.read().decode())
```

Modify `fetch_extracts_in_batches` (around line 62):
```python
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={titles_param}&format=json"

        try:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL scheme: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response: # nosec B310
                data = json.loads(response.read().decode())
```

## Online Resources & Research Data
*   **Bandit B310 Documentation:** Explains that using `urllib.urlopen` with untrusted data can lead to local file disclosure or SSRF. It recommends validating the scheme of the URL.
*   **OWASP Server-Side Request Forgery (SSRF):** SSRF flaws occur whenever a web application is fetching a remote resource without validating the user-supplied URL. It allows an attacker to coerce the application to send a crafted request to an unexpected destination, even when protected by a firewall, VPN, or another type of network access control list (ACL).
*   **Python `urllib.request` Security Considerations:** The official Python documentation notes that `urllib.request` supports `file://` URIs, which can be a security risk if not handled carefully.
