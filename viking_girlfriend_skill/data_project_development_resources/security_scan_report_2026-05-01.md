# Security Scan Report
**Date**: 2026-05-01

## Discovered Issues

A static security scan using Bandit was performed on the codebase. The following issues were discovered:

### Issue 1: B310: urllib_urlopen
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line Number**: 27
- **Confidence**: HIGH
- **Severity**: MEDIUM
- **CWE**: 22 (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'))
- **Description**: "Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."
- **Code Snippet**:
  ```python
  26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  27                 with urllib.request.urlopen(req) as response:
  28                     data = json.loads(response.read().decode())
  ```

### Issue 2: B310: urllib_urlopen
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line Number**: 62
- **Confidence**: HIGH
- **Severity**: MEDIUM
- **CWE**: 22 (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'))
- **Description**: "Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."
- **Code Snippet**:
  ```python
  61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  62             with urllib.request.urlopen(req) as response:
  63                 data = json.loads(response.read().decode())
  ```

## Research & Analysis
`urllib.urlopen` can open `file://` schemes in addition to `http://` and `https://`. This allows an attacker to access local files if the URL parameter can be manipulated. While the script currently hardcodes `https://en.wikipedia.org/...` for the root URL, manipulating the `current_cat` or `titles` parameters theoretically could lead to arbitrary URL opening if validation is bypassed.

**Bandit documentation for B310**: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

**Stack Overflow discussion**: https://stackoverflow.com/questions/48779202/audit-url-open-for-permitted-schemes-allowing-use-of-file-or-custom-schemes

## Recommendations
To mitigate this warning and improve the security of the application, it is recommended to explicitly validate the URL scheme before calling `urllib.request.urlopen`.

Example Fix:
```python
if not url.lower().startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response: # nosec B310
    data = json.loads(response.read().decode())
```

Adding `# nosec B310` to the line with `urllib.request.urlopen` suppresses the Bandit warning after the URL has been properly validated.
