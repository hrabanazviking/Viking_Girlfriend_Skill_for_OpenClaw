# Security Scan Report (2026-06-02)

## Identified Vulnerabilities

### B310 - blacklist
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py:27`
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **Description**: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **Research Findings**: The `urllib.request.urlopen` function can open `file://` or custom scheme URLs if not validated. This can lead to Server Side Request Forgery (SSRF) and Path Traversal vulnerabilities, where an attacker could access local files or make requests on internal networks if the URL is user-controlled.
- **Recommended Action**: Before calling `urlopen`, explicitly validate that the URL starts with an expected scheme (e.g., `http://` or `https://`). If it passes validation, you can append `# nosec B310` to the `urlopen` line to suppress the Bandit warning. For example:
  ```python
  if not url.startswith(('http://', 'https://')):
      raise ValueError('Invalid URL scheme')
  with urllib.request.urlopen(req) as response:  # nosec B310
  ```

---

### B310 - blacklist
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py:62`
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **Description**: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **Research Findings**: The `urllib.request.urlopen` function can open `file://` or custom scheme URLs if not validated. This can lead to Server Side Request Forgery (SSRF) and Path Traversal vulnerabilities, where an attacker could access local files or make requests on internal networks if the URL is user-controlled.
- **Recommended Action**: Before calling `urlopen`, explicitly validate that the URL starts with an expected scheme (e.g., `http://` or `https://`). If it passes validation, you can append `# nosec B310` to the `urlopen` line to suppress the Bandit warning. For example:
  ```python
  if not url.startswith(('http://', 'https://')):
      raise ValueError('Invalid URL scheme')
  with urllib.request.urlopen(req) as response:  # nosec B310
  ```

---
