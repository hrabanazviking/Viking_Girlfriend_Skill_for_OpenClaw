# Security Scan Report: `populate.py`

**Date:** 2026-04-23

## Overview
A static application security testing (SAST) scan using Bandit was performed on the `viking_girlfriend_skill` codebase. The scan identified two occurrences of a potential security vulnerability related to URL fetching in the script `viking_girlfriend_skill/data/knowledge_reference/populate.py`.

## Findings

### 1. Bandit Finding: B310 (urllib_urlopen)
* **Severity:** Medium
* **Confidence:** High
* **CWE ID:** [CWE-22](https://cwe.mitre.org/data/definitions/22.html)
* **Location 1:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`, Line 27
* **Location 2:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`, Line 62

**Description:**
Bandit reported: "Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."

The code in `populate.py` uses `urllib.request.urlopen()` to fetch data from URLs. While the current usage constructs URLs pointing to `https://en.wikipedia.org/`, the `urllib.request.urlopen()` function can theoretically open other types of resources, including local files (via the `file://` scheme), if an attacker can control the URL input.

### Research Data: The Vulnerability and its Implications

#### CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
* **Definition:** "The product uses external input to construct a pathname that is intended to identify a file or directory that is located underneath a restricted parent directory, but the product does not properly neutralize special elements within the pathname that can cause the pathname to resolve to a location that is outside of the restricted directory."
* **Context here:** While CWE-22 is classically about `../../` path traversal, when combined with URL fetching functions, it relates to the ability to read arbitrary files from the local filesystem by providing a `file:///etc/passwd` style URL instead of an expected `http://` or `https://` URL.

#### Bandit B310: urllib_urlopen
* **Definition:** `urllib.request.urlopen()` and related functions are prone to Server-Side Request Forgery (SSRF) and local file read vulnerabilities if they are passed unvalidated URLs from an untrusted source.
* **Mechanism:** Python's `urllib` library natively supports multiple protocols. If a script blindly passes an input string to `urlopen()`, it might attempt to open a local file instead of making a web request.

## Recommended Code Changes

To mitigate this potential issue and satisfy the security scanner, the code should explicitly validate that the URL scheme is either `http` or `https` before calling `urllib.request.urlopen()`.

If the URLs are completely hardcoded and there is absolutely no way for external input to alter the scheme (which appears to be the case here, as the base URL is hardcoded), the scanner finding is essentially a false positive regarding actual exploitability, but still represents a bad practice that should be fixed.

**Implementation:**

Modify the code in `populate.py` to use `urllib.parse.urlparse` to check the scheme.

```python
import urllib.parse

# ...

url = f"https://en.wikipedia.org/w/api.php?..."

# ADDED VALIDATION:
parsed_url = urllib.parse.urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}. Only http and https are allowed.")

# The # nosec B310 comment is added to tell Bandit we have manually verified this line.
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    # ...
```

According to the project's memory directives:
> When using URL open functions like `urllib.request.urlopen`, explicitly validate the URL scheme (e.g., ensuring it starts with `http://` or `https://`) to prevent B310 SSRF/Path Traversal vulnerabilities before appending `# nosec B310` to suppress Bandit warnings.
