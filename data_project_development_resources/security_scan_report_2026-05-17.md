# Security Scan Report

**Date:** 2026-05-17

## Executive Summary
A static security scan of the codebase was conducted using Bandit. Several low-severity issues related to `assert` usage in tests were identified and ignored. However, two medium-severity vulnerabilities were identified in the knowledge reference builder script. These vulnerabilities relate to the use of `urllib.request.urlopen` which could theoretically be exploited if the URL structure allows arbitrary schemes, leading to Server-Side Request Forgery (SSRF) or Path Traversal (CWE-22).

## Identified Issues

### Bandit B310: Audit url open for permitted schemes
- **Severity:** Medium
- **CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory / Path Traversal)
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line Numbers:** 27, 62

**Description:**
Bandit has flagged the use of `urllib.request.urlopen` in the `populate.py` script. The vulnerability arises because `urlopen` supports opening local files (e.g., `file://`) and custom schemes in addition to standard `http`/`https` URLs. Although the URL strings are currently hardcoded to Wikipedia API endpoints, failing to explicitly validate the URL scheme before calling `urlopen` creates a risk of Path Traversal (CWE-22) and Server-Side Request Forgery (SSRF) if the URL generation logic is ever modified to incorporate unsanitized user input.

## Research Data

### Bandit B310 Reference
According to the Bandit documentation for [B310: urllib_urlopen](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen):
> Audit url open for permitted schemes. Allowing use of 'file:/' or custom schemes is often unexpected.

### CWE-22: Path Traversal
According to [MITRE CWE-22](https://cwe.mitre.org/data/definitions/22.html):
> The product uses external input to construct a pathname that is intended to identify a file or directory that is located underneath a restricted parent directory, but the product does not properly neutralize special elements within the pathname that can cause the pathname to resolve to a location that is outside of the restricted directory.
>
> When `urllib.request.urlopen` is used with a `file://` scheme, it can bypass intended access controls and read files from the local filesystem that it should not have access to, akin to a traditional Path Traversal attack.

## Recommended Code Changes

To comply with the project's security memory rules and remediate this finding, the URL scheme must be explicitly validated before it is opened, and then the Bandit warning can be suppressed safely.

**Recommended Change for `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**

```python
<<<<<<< SEARCH
        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
=======
        while True:
            try:
                if not url.startswith(('http://', 'https://')):
                    raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are permitted.")

                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
>>>>>>> REPLACE
```

```python
<<<<<<< SEARCH
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
=======
        try:
            if not url.startswith(('http://', 'https://')):
                raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are permitted.")

            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
>>>>>>> REPLACE
```

These changes ensure the URL relies only on authorized schemes, mitigating SSRF and CWE-22 issues associated with `urllib.request.urlopen`.
