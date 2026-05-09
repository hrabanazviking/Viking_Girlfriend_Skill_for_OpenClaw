# Bug Report: B310 urllib_urlopen Vulnerability (2026-05-09)

## Overview

A recent security scan using Bandit identified multiple occurrences of the **B310: urllib_urlopen** vulnerability within the codebase. This issue is categorized as Server-Side Request Forgery (SSRF) or Path Traversal vulnerability and poses a medium severity risk with high confidence.

## Findings

The following instances were detected:

1.  **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
    **Line:** 27
    **Code Snippet:**
    ```python
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    ```

2.  **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
    **Line:** 62
    **Code Snippet:**
    ```python
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    ```

## Vulnerability Details

*   **Vulnerability Type:** Server-Side Request Forgery (SSRF) / Path Traversal
*   **Bandit Test ID:** B310
*   **CWE ID:** [CWE-22 (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'))](https://cwe.mitre.org/data/definitions/22.html) or [CWE-918 (Server-Side Request Forgery)](https://cwe.mitre.org/data/definitions/918.html)
*   **Severity:** Medium
*   **Confidence:** High

### Description

The `urllib.request.urlopen()` function in Python can open various types of URLs, including `http://`, `https://`, `ftp://`, and importantly, `file://`. If the URL passed to `urlopen` is not strictly validated, an attacker could potentially supply a `file://` scheme or a custom scheme. This could lead to:

1.  **Local File Disclosure:** By using `file:///etc/passwd` or similar paths, an attacker might be able to read sensitive local files on the executing machine.
2.  **Server-Side Request Forgery (SSRF):** By providing internal network addresses (e.g., `http://localhost:8080` or `http://192.168.1.1`), an attacker could make the application perform requests to internal resources that would otherwise be inaccessible from the outside.

## Research Data and Resources

*   **DeepSource Security Audit (BAN-B310):** Highlights that `urllib` can open `ftp://` and `file://` URLs, making the application vulnerable to SSRF if the URL is manipulated by an external user. It recommends explicitly validating the URL scheme before opening it. [Reference](https://deepsource.com/directory/python/issues/BAN-B310)
*   **Bandit Blacklist Calls Documentation:** "Audit url open for permitted schemes. Allowing use of 'file:' or custom schemes is often unexpected." [Reference](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen)

## Recommended Code Changes

To mitigate this vulnerability, you must ensure that the URL scheme is explicitly validated before it is passed to `urllib.request.urlopen`. Specifically, verify that the scheme is strictly `http` or `https`. Once validated, you can append the `# nosec B310` comment to suppress the Bandit warning for that specific, validated line.

### Example Remediation

Change the code in `viking_girlfriend_skill/data/knowledge_reference/populate.py` from:

```python
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{urllib.parse.quote(current_cat)}&cmlimit=500&format=json"

        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
```

To include scheme validation:

```python
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{urllib.parse.quote(current_cat)}&cmlimit=500&format=json"

        while True:
            try:
                if not url.lower().startswith(('http://', 'https://')):
                    raise ValueError(f"Invalid URL scheme: {url}")

                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response: # nosec B310
```

Apply this validation before both occurrences of `urllib.request.urlopen()` in the script. While the `url` variable in the current implementation is hardcoded to `https://en.wikipedia.org...`, adding explicit validation establishes a secure coding pattern, guards against future modifications that might introduce dynamic URLs, and satisfies security auditing tools.
