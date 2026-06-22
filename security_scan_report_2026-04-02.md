# Security Scan Report

**Date:** 2026-04-02
**Tool Used:** Bandit
**Codebase:** Viking Girlfriend Skill

## Executive Summary

A security scan of the codebase was performed using Bandit (`bandit -r . -f json -q`). The scan identified two medium-severity issues, both related to the use of `urllib.request.urlopen` without explicitly restricting the allowed URL schemes. These issues are flagged under Bandit's B310 test and relate to CWE-22 (Path Traversal / Audit url open for permitted schemes).

## Detailed Findings

### Issue 1: B310 (Audit url open for permitted schemes)
*   **Severity:** Medium
*   **Confidence:** High
*   **File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
*   **Lines:** 26-28
*   **Code Snippet:**
    ```python
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    ```
*   **Description:** The use of `urllib.request.urlopen` is potentially dangerous if the URL scheme is not strictly controlled or validated. If an attacker can manipulate the URL string to use the `file://` scheme or other custom schemes, it may result in path traversal or arbitrary file read vulnerabilities.

### Issue 2: B310 (Audit url open for permitted schemes)
*   **Severity:** Medium
*   **Confidence:** High
*   **File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
*   **Lines:** 61-63
*   **Code Snippet:**
    ```python
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    ```
*   **Description:** Similar to Issue 1, this instance involves using `urllib.request.urlopen` with a dynamically constructed URL.

## Vulnerability Research: CWE-22 (Path Traversal)

**Source:** [MITRE CWE-22](https://cwe.mitre.org/data/definitions/22.html)

**Description:**
The product uses external input to construct a pathname that is intended to identify a file or directory that is located underneath a restricted parent directory, but the product does not properly neutralize special elements within the pathname that can cause the pathname to resolve to a location that is outside of the restricted directory.

In the context of `urllib.request.urlopen`, the concern (often specifically highlighted by Bandit as an offshoot of this CWE or related to CWE-73/CWE-98 depending on exact usage) is that `urllib` natively supports multiple schemes, including `file://`. If the `url` variable is influenced by user input, an attacker could supply a URL like `file:///etc/passwd`, causing the application to read and potentially expose sensitive local files instead of making an external HTTP request.

**Common Consequences:**
*   **Confidentiality:** Attackers can read files or directories they are not authorized to access (e.g., password files, configuration files containing secrets).
*   **Integrity:** In scenarios involving write operations (not applicable to the `urlopen` read scenario here, but part of the broader CWE-22), attackers might modify or overwrite critical files.
*   **Availability:** Overwriting or deleting unexpected critical files can lead to Denial of Service (DoS).

**Mitigation Strategies:**
*   **Input Validation:** Assume all input is malicious. Use an "accept known good" (allowlist) input validation strategy.
*   **Scheme Validation:** When dealing with URLs, ensure that only permitted schemes (e.g., `http`, `https`) are allowed.
*   **Use Vetted Libraries:** Use higher-level, safer libraries that enforce stricter defaults regarding allowed protocols.

## Recommended Code Changes

To address the identified issues in `viking_girlfriend_skill/data/knowledge_reference/populate.py`, consider implementing one of the following recommendations:

### Recommendation 1: Validate URL Scheme (Preferred for minimal dependencies)

Before passing the `url` to `urllib.request.urlopen`, explicitly verify that it uses an allowed scheme (`http` or `https`). Since the URLs in `populate.py` are hardcoded to start with `https://en.wikipedia.org/`, the risk is currently theoretical based on static analysis, but adding a check ensures defense-in-depth if the URL construction logic ever changes.

```python
# Updated Code Example
if not url.startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme provided: {url}. Only HTTP/HTTPS are allowed.")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```
*Note: If the URL is considered strictly internal and safe, a `# nosec B310` comment can be added to suppress the Bandit warning, but explicit validation is safer.*

### Recommendation 2: Migrate to the `requests` Library

The `requests` library is widely considered more robust and user-friendly than `urllib`. More importantly, `requests` does not support the `file://` scheme out-of-the-box, inherently mitigating the specific risk highlighted by Bandit test B310.

```python
# Updated Code Example (requires 'requests' in requirements.txt)
import requests

response = requests.get(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
response.raise_for_status() # Raise an exception for bad status codes
data = response.json()
```
This approach requires adding `requests` to the project's dependencies but results in cleaner, safer code.