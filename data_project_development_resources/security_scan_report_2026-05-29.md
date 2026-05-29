# Security Scan Report: 2026-05-29

## Overview
A static application security testing (SAST) scan using Bandit was performed on the `viking_girlfriend_skill` codebase.
The scan revealed security vulnerabilities related to Server-Side Request Forgery (SSRF) and Path Traversal in the script used to populate the knowledge reference files.

## Vulnerability Details

### 1. B310: Audit url open for permitted schemes
**Severity:** Medium
**Confidence:** High
**Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27 and 62)

**Description:**
The Bandit SAST scanner flagged the use of `urllib.request.urlopen` (B310). According to [Bandit documentation](https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html#b310-urllib-urlopen), auditing url open for permitted schemes is crucial because allowing the use of `file:/` or custom schemes is often unexpected and can lead to Local File Inclusion (LFI) or Server-Side Request Forgery (SSRF).

### 2. CVE-2025-0938: Python URL Parser Differential Parsing Flaw
**Severity:** Medium
**CVSS Score:** 6.3

**Description:**
While reviewing the use of `urllib`, research revealed an information disclosure vulnerability in Python's `urllib.parse` module (CVE-2025-0938). The `urllib.parse.urlsplit` and `urllib.parse.urlparse` functions incorrectly accept domain names containing square brackets outside of the IPv6 literal context. This violates RFC 3986 specifications and causes differential parsing. An attacker can craft a malicious URL that Python interprets differently than other security components, potentially enabling security bypasses, SSRF attacks, open redirects, or request routing manipulation.

**Sources:**
- Bandit B310: [Bandit Documentation](https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html#b310-urllib-urlopen)
- CVE-2025-0938: [SentinelOne Vulnerability Database](https://www.sentinelone.com/vulnerability-database/cve-2025-0938/)

## Recommended Code Changes

To mitigate these vulnerabilities, the following code changes are recommended for `viking_girlfriend_skill/data/knowledge_reference/populate.py`:

### 1. Validate URL Schemes (Bandit B310 Mitigation)
Explicitly validate the URL scheme before calling `urlopen` to ensure it only permits `http://` or `https://` requests, thereby preventing `file://` or custom scheme abuse. After adding the validation, append `# nosec B310` to suppress the Bandit warning.

```python
import urllib.parse

def fetch_safe(url, headers):
    # Validate the scheme
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}. Only http and https are allowed.")

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:  # nosec B310
        return response.read().decode()
```

### 2. Implement Custom URL Validation (CVE-2025-0938 Mitigation)
Wrap `urllib.parse` functions with custom validation logic to reject hostnames containing square brackets unless they match the IPv6 literal pattern, effectively blocking the differential parsing attack vector.

```python
import urllib.parse
import re

def validate_and_parse_url(url):
    """Parse URL with additional validation for RFC 3986 compliance."""
    parsed = urllib.parse.urlsplit(url)

    # Check for square brackets outside IPv6 literal context
    if parsed.hostname and '[' in parsed.hostname:
        # Only allow if it matches IPv6 literal pattern
        if not re.match(r'^\[[\da-fA-F:]+\]$', parsed.hostname):
            raise ValueError("Invalid hostname: square brackets not permitted outside IPv6 literals")

    # Validate scheme as part of the overall check
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

    return parsed
```
These changes ensure that the knowledge base population script remains secure against both local file inclusion attempts and advanced URL parsing vulnerabilities.
