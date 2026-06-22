# Security Scan & Research Report - 2026-04-21

## Overview

A security scan was performed using Bandit (a Python AST-based security linter). The following potential security issues were found:

## Findings

### 1. B404/B603: Use of `subprocess` module
- **File:** `infra/bootstrap_host.py`, Lines 3, 15
- **Severity:** Low
- **Description:** The scan detected the use of `subprocess.run()`. While `check_command("podman")` etc. passes static strings, `subprocess` calls can be vulnerable to command injection if untrusted user input is passed into the command array.
- **Remediation:** In this specific file, the commands are hardcoded (e.g., `['podman', '--version']`), which means there is no actual untrusted input being executed. To satisfy the linter and mark this as acknowledged, we should add `# nosec B603` and `# nosec B404` to the respective lines.

### 2. B310: Audit url open for permitted schemes (SSRF vulnerability)
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`, Lines 27, 62
- **Severity:** Medium
- **Description:** The scan detected the use of `urllib.request.urlopen()`. The `urllib` module can open not just `http://` or `https://` URLs, but also `ftp://` and `file://`. If the URL is controllable by a malicious user, this can lead to Server-Side Request Forgery (SSRF) or arbitrary local file read.
- **Remediation:** According to Bandit documentation and best practices, URLs should be validated before opening them. We should ensure the URL scheme starts with `http://` or `https://` before passing it to `urlopen`.
- **Recommended Code Change:**
  ```python
  if not (url.startswith('http://') or url.startswith('https://')):
      raise ValueError("Invalid URL scheme")
  req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  with urllib.request.urlopen(req) as response: # nosec B310
      # ...
  ```

## Action Plan

1. **`infra/bootstrap_host.py`**: Add `# nosec B404` to the `import subprocess` line and `# nosec B603` to the `subprocess.run` line.
2. **`viking_girlfriend_skill/data/knowledge_reference/populate.py`**: Add strict URL scheme validation (checking for `http://` or `https://`) before calling `urllib.request.urlopen` and append `# nosec B310` to the `urlopen` lines.
