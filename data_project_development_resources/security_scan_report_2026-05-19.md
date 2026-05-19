# Security Scan Report: 2026-05-19

## Overview
A static application security testing (SAST) scan was performed on the codebase using Bandit. The scan identified potential security vulnerabilities related to the usage of `urllib.request.urlopen`.

## Findings

### 1. Bandit B310: Insecure usage of `urllib.request.urlopen`
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Lines:** 27, 62
- **Severity:** Medium
- **Confidence:** High
- **CWE:** CWE-918 (Server-Side Request Forgery - SSRF), CWE-22 (Improper Limitation of a Pathname to a Restricted Directory - Path Traversal)

#### Description
The Bandit scan flagged the use of `urllib.request.urlopen` at lines 27 and 62 in `populate.py`.

`urllib.request.urlopen` is capable of opening not only `http://` and `https://` URLs, but also `ftp://` and `file://` schemas. If the URL passed to this function is not explicitly validated and can be influenced by external input, it can lead to severe security vulnerabilities:
- **Server-Side Request Forgery (SSRF) (CWE-918):** An attacker could manipulate the URL to make the application send unauthorized requests to internal systems or external services, potentially leading to information disclosure, port scanning, or interacting with internal APIs.
- **Local File Inclusion (LFI) / Path Traversal (CWE-22):** By using the `file://` schema, an attacker could force the application to read local files on the server (e.g., `/etc/passwd` or configuration files with sensitive credentials).

While `populate.py` currently constructs URLs using hardcoded base domains (`https://en.wikipedia.org/w/api.php...`), the `urllib.request` calls are not inherently protected against schema manipulation if the URL construction logic ever changes or incorporates external inputs. It is a security best practice to explicitly validate the URL scheme before invoking `urlopen`.

#### Research & Resources
- **DeepSource BAN-B310:** [Audit required: Use of an insecure method from `urllib` detected](https://deepsource.com/directory/python/issues/BAN-B310)
- **OWASP Top 10 (A10:2021) - Server-Side Request Forgery (SSRF):** [https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/](https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/)
- **MITRE CWE-918:** [Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html)
- **MITRE CWE-22:** [Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html)
- **Bandit B310 Documentation:** [https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen)

### Recommended Code Changes

To address this issue and adhere to secure coding guidelines, explicitly validate the URL scheme before making the request. After implementing the validation, append the `# nosec B310` comment to the `urlopen` line to suppress the Bandit warning.

**Changes required in `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**

#### Modification 1 (Around Line 27):
```python
<<<<<<< SEARCH
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
=======
                if not url.startswith('http://') and not url.startswith('https://'):
                    raise ValueError(f"Invalid URL scheme detected: {url}")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

#### Modification 2 (Around Line 62):
```python
<<<<<<< SEARCH
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                pages = data['query']['pages']
=======
        try:
            if not url.startswith('http://') and not url.startswith('https://'):
                raise ValueError(f"Invalid URL scheme detected: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
                data = json.loads(response.read().decode())
                pages = data['query']['pages']
>>>>>>> REPLACE
```

Implementing these validations ensures that the application only opens URLs with allowed schemes, effectively mitigating the risk of SSRF and Local File Inclusion vulnerabilities associated with `urllib.request.urlopen`.
