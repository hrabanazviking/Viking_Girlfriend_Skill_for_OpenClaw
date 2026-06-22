# Security Scan Report (2026-05-03)

## Overview
This report documents the findings from a Bandit static analysis security scan of the codebase, specifically focusing on `urllib.request.urlopen` vulnerabilities.

## Findings

### Issue 1: B310 - Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line**: 27
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **CWE**: [22](https://cwe.mitre.org/data/definitions/22.html)
- **More Info**: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

#### Code Snippet
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```

### Issue 2: B310 - Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line**: 62
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **CWE**: [22](https://cwe.mitre.org/data/definitions/22.html)
- **More Info**: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

#### Code Snippet
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```

## Detailed Analysis and Research

### The Vulnerability: Server-Side Request Forgery (SSRF) and Path Traversal via `urllib`
The `urllib.request.urlopen` function in Python is a powerful tool for opening URLs. However, it can automatically handle various URL schemes, not just `http://` and `https://`. For example, it can handle `file://` or `ftp://` schemes. If user-controlled data is passed to `urlopen` without proper validation, an attacker could potentially force the application to make requests to unintended internal or external resources.

- **SSRF (Server-Side Request Forgery)**: An attacker could supply a URL pointing to internal services (e.g., `http://localhost:8080/admin`) that are not normally accessible from the outside. The application server, acting on behalf of the attacker, makes the request.
- **Path Traversal / Local File Inclusion (LFI)**: By providing a `file://` URL (e.g., `file:///etc/passwd`), an attacker might be able to read arbitrary files from the server's filesystem.

### Bandit B310 Rule
Bandit flags `urllib.urlopen` (and related functions) with rule B310 because it's a common source of SSRF vulnerabilities. The rule states: "Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."

### Mitigation Strategy
To properly address this issue while maintaining the intended functionality, we must explicitly validate the URL scheme before making the request. According to the project's security guidelines and general best practices, we should:

1.  **Parse the URL**: Use `urllib.parse.urlparse` to break the URL into its components.
2.  **Validate the Scheme**: Check if the extracted scheme is within a permitted list (usually just `http` and `https`).
3.  **Handle Invalid Schemes**: If the scheme is not permitted, raise an exception or handle the error gracefully.
4.  **Suppress Warning**: Once the validation is in place, we can safely suppress the Bandit warning for that specific line using the `# nosec B310` comment.

## Recommended Code Changes

The following changes should be applied to `viking_girlfriend_skill/data/knowledge_reference/populate.py` to mitigate the B310 vulnerabilities.

### Change 1 (Around line 27)
```python
<<<<<<< SEARCH
        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
=======
        while True:
            try:
                parsed_url = urllib.parse.urlparse(url)
                if parsed_url.scheme not in ('http', 'https'):
                    raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

### Change 2 (Around line 62)
```python
<<<<<<< SEARCH
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={titles_param}&format=json"

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
=======
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={titles_param}&format=json"

        try:
            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.scheme not in ('http', 'https'):
                raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
                data = json.loads(response.read().decode())
>>>>>>> REPLACE
```
