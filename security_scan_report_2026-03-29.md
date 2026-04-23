# Security Scan Report

**Date:** 2026-03-29

## Overview
A comprehensive security scan was performed on the `viking_girlfriend_skill` codebase using Bandit (Static Application Security Testing). The scan revealed a specific vulnerability related to the use of Python's standard library `urllib` for network requests.

## Vulnerabilities Identified

### 1. Insecure Use of `urllib.request.urlopen` (Bandit ID: B310)

* **Severity:** MEDIUM
* **Confidence:** HIGH
* **CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')) / CWE-918 (Server-Side Request Forgery)
* **Location:**
  * `viking_girlfriend_skill/data/knowledge_reference/populate.py`, line 27
  * `viking_girlfriend_skill/data/knowledge_reference/populate.py`, line 62

**Description:**
The application uses `urllib.request.urlopen` to make HTTP requests based on URLs constructed or passed into the function. While `urllib` is part of the Python standard library, it implicitly supports multiple URL schemes, most notably `file://` and `ftp://`, alongside `http://` and `https://`.

If an attacker is able to influence the URL passed to `urlopen`, they could potentially supply a `file://` URL (e.g., `file:///etc/passwd`). This transforms a routine HTTP request into a Local File Inclusion (LFI) vulnerability or a Server-Side Request Forgery (SSRF) attack, potentially allowing the attacker to read arbitrary files from the host machine or access internal network resources.

Although in the current context (`populate.py`), the URL base is hardcoded to `https://en.wikipedia.org/`, security best practices mandate explicitly validating and restricting allowed URL schemes to prevent future regressions if the URL construction logic is ever modified to accept user input.

## Recommended Code Changes

To mitigate this risk, it is recommended to explicitly validate the URL scheme before making the request. We should enforce that the URL begins with `http://` or `https://` (ideally just `https://` since we are calling the Wikipedia API).

### Implementation

Modify `viking_girlfriend_skill/data/knowledge_reference/populate.py` to add URL scheme validation.

**Before:**
```python
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{urllib.parse.quote(current_cat)}&cmlimit=500&format=json"

        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
```

**After:**
```python
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{urllib.parse.quote(current_cat)}&cmlimit=500&format=json"

        while True:
            try:
                if not url.lower().startswith('https://'):
                    raise ValueError(f"Invalid URL scheme: {url}")

                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
```

**Before:**
```python
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={titles_param}&format=json"

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
```

**After:**
```python
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={titles_param}&format=json"

        try:
            if not url.lower().startswith('https://'):
                raise ValueError(f"Invalid URL scheme: {url}")

            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
```

*Alternatively, replacing `urllib` with the `requests` library would also resolve the issue, but adding the scheme check avoids introducing a new external dependency for a data population script.*

## Research Notes
- **Bandit B310:** Specifically targets `urllib.urlopen` and `urllib.request.urlopen`.
- **Mitigation Strategy:** DeepSource and OWASP recommend verifying the URL prefix before execution (`url.lower().startswith(('http://', 'https://'))`).
- **OWASP Reference:** Maps to OWASP Top 10 A10:2021 (Server-Side Request Forgery).
