# Security Scan Report - 2026-06-08

## Findings

A static security scan was performed using Bandit (`bandit -r . -f json -q`). The scan identified several security warnings that needed attention. The B101 `assert_used` warnings were ignored, as they are prevalent and expected in the project's test suite.

### 1. Subprocess Security Warnings (B404, B603)
**Files:** `infra/bootstrap_host.py`
**Details:**
- **[B404]** `import subprocess` - Consider possible security implications associated with the subprocess module.
- **[B603]** `subprocess.run([command, "--version"], capture_output=True, check=True)` - subprocess call - check for execution of untrusted input.

**Research & Mitigation:**
- **Research:** According to Bandit documentation and PyCQA discussions (e.g. https://github.com/PyCQA/bandit/issues/333, https://bandit.readthedocs.io/en/latest/plugins/b603_subprocess_without_shell_equals_true.html), `B404` and `B603` are raised to alert developers about potential shell injection vulnerabilities. In `bootstrap_host.py`, the `command` variable passed to `subprocess.run` is a hardcoded string or comes from a controlled source (e.g., `"podman"`, `"docker"`, `"nvidia-smi"`). Since it's executed with `shell=False` (the default) and the input is trusted, this is a false positive.
- **Code Change Recommendation:** Suppress the warnings by adding `# nosec B404` to the import statement and `# nosec B603` to the `subprocess.run` call.

### 2. Try-Except-Pass (B110)
**Files:** `tests/test_cove_pipeline.py`, `tests/test_e2e_system.py`
**Details:**
- **[B110]** Try, Except, Pass detected. Catching exceptions and using `pass` can mask important errors.

**Research & Mitigation:**
- **Research:** Using `try-except-pass` can hide bugs or failures. Bandit flags this as a potential issue. However, in these specific test scenarios (e.g., bypassing circuit breakers manually or catching offline/loop issues), the `pass` is intentional and acceptable as noted in comments.
- **Code Change Recommendation:** Suppress the warnings by adding `# nosec B110` to the `except` blocks.

### 3. URL Open (B310)
**Files:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Details:**
- **[B310]** `urllib.request.urlopen(req)` - Audit url open for permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected.

**Research & Mitigation:**
- **Research:** Bandit flags `urllib.request.urlopen` because if the URL parameter is not sanitized, an attacker could potentially read local files using the `file://` scheme or perform Server-Side Request Forgery (SSRF) attacks. Even though the URLs in this script are currently built with `https://en.wikipedia.org/w/api.php`, explicitly validating the scheme before opening the URL adds a defense-in-depth layer against malicious input if the script is ever modified to accept dynamic URLs.
- **Code Change Recommendation:** Explicitly validate that the URL scheme starts with `http://` or `https://` before calling `urlopen`. Then append `# nosec B310` to suppress the Bandit warning.

```python
if not url.startswith('http://') and not url.startswith('https://'):
    raise ValueError('Invalid URL scheme')
with urllib.request.urlopen(req) as response:  # nosec B310
    # ...
```
