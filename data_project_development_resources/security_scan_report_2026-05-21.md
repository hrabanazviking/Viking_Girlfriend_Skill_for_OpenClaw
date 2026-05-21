# Security Scan Report

## Overview
A static security scan was performed using Bandit, a SAST tool for Python. The scan identified several potential security issues.

## Findings

### B101: assert_used
- **Severity**: Low
- **Confidence**: High
- **Description**: The use of `assert` statements was detected in several test files. In Python, `assert` statements are removed when compiling to optimized byte code (using the `-O` flag). This can lead to test bypasses if tests are run in optimized mode.
- **Affected Files**:
  - `tests/test_vordur_trigger.py` (lines 197, 204, 217, 228)
  - `tests/test_wyrd_vitality_modulation.py` (lines 21, 27, 35, 43, 51, 57, 65)
- **Recommended Changes**: Replace raw `assert` statements with `pytest.fail()` or raise a custom exception (e.g., `AssertionError` or a specific project exception like `SecurityViolation`) in test files to ensure assertions are always evaluated regardless of optimization flags. However, in standard pytest testing environments, `assert` is typically acceptable and rewritten by pytest. Since the task only asks to report and the memory guidelines state "Within pytest test files, avoid using sys.exit()... Prefer raising a custom exception or using pytest.fail() rather than raw assert statements", replacing them is the recommended change.

### B310: urllib_urlopen
- **Severity**: Medium
- **Confidence**: High
- **Description**: Audit url open for permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected and can lead to Server Side Request Forgery (SSRF) or Path Traversal vulnerabilities. By default, `urllib.request.urlopen` supports multiple schemes, including `file://`. If the URL is user-controllable, an attacker could potentially read local files or make requests to internal network services.
- **Affected File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27, 62)
- **Research Details**:
  - The vulnerability relates to CWE-918 (Server-Side Request Forgery) and potentially CWE-22 (Path Traversal).
  - Python's `urllib` can parse and open `file://` URLs, allowing local file reads.
  - Mitigation involves explicitly validating that the URL scheme is strictly `http://` or `https://` before opening the URL.
- **Recommended Changes**: In `viking_girlfriend_skill/data/knowledge_reference/populate.py`, validate the URL scheme before calling `urllib.request.urlopen`. Example:
  ```python
  if not url.lower().startswith(('http://', 'https://')):
      raise ValueError("Invalid URL scheme")
  req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  # nosec B310
  with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode())
  ```
  The `# nosec B310` comment should be added to suppress the Bandit warning after validation is implemented.

## Research Sources
- DeepSource BAN-B310 Documentation: https://deepsource.com/directory/python/issues/BAN-B310
- SentinelOne CVE-2022-0391 Analysis: https://www.sentinelone.com/vulnerability-database/cve-2022-0391/
