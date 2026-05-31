# Security Scan Report: 2026-05-31

## Executive Summary
A static application security testing (SAST) scan using Bandit was performed on the `viking_girlfriend_skill` codebase. The scan identified a High Confidence, Medium Severity vulnerability related to Server-Side Request Forgery (SSRF) and Local File Inclusion (LFI) risks in `viking_girlfriend_skill/data/knowledge_reference/populate.py`.

## Vulnerability Details
* **Vulnerability ID:** Bandit B310
* **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
* **Lines:** 27, 62
* **Description:** Audit url open for permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected.
* **CWE:** [CWE-918: Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html) / [CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html)

### Affected Code Snippets
**Line 27:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```

**Line 62:**
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```

## Research Findings
Research on SSRF and `urllib.request.urlopen` vulnerabilities indicates that when input URLs are not strictly validated, an attacker can manipulate the URL scheme to access restricted resources.

1.  **Datadog Security Documentation** (https://docs.datadoghq.com/security/code_security/static_analysis/static_analysis_rules/python-flask/avoid-ssrf/) highlights that SSRF attacks manipulate the server to make HTTP requests to an arbitrary domain of the attacker's choosing. This can lead to unauthorized actions or access to data within the server, potentially exposing sensitive information. Good coding practices include validating and sanitizing user inputs, specifically verifying that the URL scheme is limited to `http` or `https`.
2.  **Strike Security Blog** (https://strike.sh/blog/introduction-to-server-side-attack-server-side-request-forgery-ssrf) further details that if `urllib.request.urlopen` directly takes a URL without validation, it allows for malicious URLs that could target internal services or local files (e.g., using the `file://` scheme), leading to Data Breach Risks, Internal Network Mapping, Executing Remote Code, and Service Disruption.

## Recommended Code Changes
To mitigate this risk, the URL scheme must be explicitly validated before it is processed by `urllib.request.urlopen`. While the `url` variables in `populate.py` are currently constructed using hardcoded base URLs (e.g., `https://en.wikipedia.org/...`), it is a best practice to enforce scheme validation to prevent future vulnerabilities and resolve the Bandit warning.

**Proposed Fix for `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**

Update the code around lines 27 and 62 to include a validation check using `urllib.parse.urlparse` to ensure the scheme is `https`, and then suppress the Bandit warning with `# nosec B310`.

```python
<<<<<<< SEARCH
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{urllib.parse.quote(current_cat)}&cmlimit=500&format=json"

        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
=======
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{urllib.parse.quote(current_cat)}&cmlimit=500&format=json"

        while True:
            try:
                parsed_url = urllib.parse.urlparse(url)
                if parsed_url.scheme not in ["http", "https"]:
                    raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")

                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

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
            if parsed_url.scheme not in ["http", "https"]:
                raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")

            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
                data = json.loads(response.read().decode())
>>>>>>> REPLACE
```
