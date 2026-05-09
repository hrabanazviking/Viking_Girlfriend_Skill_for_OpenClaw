# Security Scan Report: B310 Vulnerability in `populate.py`

**Date:** 2026-05-09
**Target File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`

## Vulnerability Overview

A static security scan using Bandit detected two instances of the **B310: urllib_urlopen** vulnerability within the `populate.py` script. The vulnerability arises from calling `urllib.request.urlopen(req)` without first validating the URL scheme.

### Lines Affected in `populate.py`
- Line 27: `with urllib.request.urlopen(req) as response:`
- Line 62: `with urllib.request.urlopen(req) as response:`

## Risk Analysis

The `urllib` library can open not only `http://` and `https://` URLs but also `ftp://` and `file://` protocols. If the URL passed to `urlopen` is influenced by user input or an untrusted external source, an attacker could potentially exploit this behavior.

1.  **Server-Side Request Forgery (SSRF):** By providing an internal URL, an attacker might force the application to make requests to internal services or network resources that would otherwise be inaccessible, potentially extracting sensitive data or interacting with internal APIs.
2.  **Local File Inclusion (LFI):** By using the `file://` scheme, an attacker could instruct the application to read arbitrary local files on the host machine, leading to unauthorized access to source code, configuration files, or sensitive system information.

## External Research Findings

Research from security directories and documentation highlights the critical nature of this vulnerability and provides standard mitigation strategies.

*   **Bandit Documentation (B310):** The official Bandit documentation states: "Audit url open for permitted schemes. Allowing use of 'file:' or custom schemes is often unexpected." It categorizes this as a Medium severity issue. (Source: [Bandit Blacklists - B310](https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html))
*   **DeepSource Advisory (BAN-B310):** DeepSource notes that `urllib.request.urlopen` can make an application vulnerable to SSRF attacks if user-provided data is not validated. They recommend explicitly validating the URL before opening it. (Source: [DeepSource Python Issues - BAN-B310](https://deepsource.com/directory/python/issues/BAN-B310))

## Recommended Code Changes

To mitigate this vulnerability, it is crucial to validate the URL scheme before calling `urllib.request.urlopen`. Specifically, the code must verify that the URL starts with `http://` or `https://`.

If a URL fails validation, a `ValueError` or a relevant security exception should be raised. Once the validation is in place, the Bandit warning can be safely suppressed using `# nosec B310`.

### Example Fix Implementation

```python
# Before using urlopen, validate the scheme:
if url.lower().startswith('http://') or url.lower().startswith('https://'):
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
else:
    raise ValueError(f"Invalid URL scheme detected in: {url}")

with urllib.request.urlopen(req) as response: # nosec B310
    # Process the response
    ...
```

By applying this validation logic to the relevant lines in `populate.py`, the risk of SSRF and LFI vulnerabilities via `urllib.request.urlopen` is significantly reduced.
