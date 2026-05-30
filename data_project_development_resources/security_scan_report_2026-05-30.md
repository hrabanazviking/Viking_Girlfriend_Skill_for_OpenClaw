# Security Scan Report - 2026-05-30

## Overview
A static application security testing (SAST) scan was performed using Bandit across the project codebase. Several security vulnerabilities and code quality issues were identified. This report documents the findings along with recommended code changes to mitigate the risks.

## Findings & Recommendations

### 1. `infra/bootstrap_host.py`

**Issue:** B404 (import_subprocess) & B603 (subprocess_without_shell_equals_true)
- **Severity:** LOW
- **Confidence:** HIGH
- **Description:** The `subprocess` module is imported, and `subprocess.run` is used. Bandit flags this as a potential vector for command injection, even when `shell=False`, depending on how input is handled.
- **Analysis:** The script uses `subprocess.run([command, "--version"], capture_output=True, check=True)` where `command` is passed directly as a variable. While the commands passed in this specific script (`podman`, `docker`, `nvidia-smi`) are hardcoded in the caller, it's good practice to suppress these specific warnings if the inputs are fully trusted and controlled, or sanitize/validate the `command` variable explicitly.
- **Recommended Change:**
  Since the commands are strictly controlled within the script, we can add `# nosec B404` to the import and `# nosec B603` to the `subprocess.run` call.

  ```python
  import subprocess  # nosec B404

  # ...
  def check_command(command: str) -> bool:
      # ...
      subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
  ```

### 2. `tests/test_cove_pipeline.py`

**Issue:** B110 (try_except_pass)
- **Severity:** LOW
- **Confidence:** HIGH
- **Description:** A `try-except-pass` pattern was detected.
- **Analysis:** The test forces a circuit breaker to open by artificially triggering failures in a loop. The exception raised by `on_failure` is caught and silently ignored using `pass`. While this is just test code, suppressing exceptions entirely can mask other unexpected errors.
- **Recommended Change:** Catch the specific exception expected (e.g., the one raised by the circuit breaker logic when it trips) rather than a broad `Exception`, or add a suppression comment `# nosec B110` since it's a test intentionally ignoring an error. Better yet, assert the exception if one is expected to be raised.

  ```python
  <<<<<<< SEARCH
          except Exception:
              pass
  =======
          except Exception:  # nosec B110
              pass
  >>>>>>> REPLACE
  ```

### 3. `tests/test_e2e_system.py`

**Issue:** B110 (try_except_pass)
- **Severity:** LOW
- **Confidence:** HIGH
- **Description:** A `try-except-pass` pattern was detected.
- **Analysis:** The code attempts to publish an event asynchronously inside a synchronous context and silently ignores any `Exception`.
- **Recommended Change:** Add `# nosec B110` as it explicitly states that offline/loop not running is acceptable.

  ```python
  <<<<<<< SEARCH
          except Exception:
              pass  # offline / loop not running — acceptable
  =======
          except Exception:  # nosec B110
              pass  # offline / loop not running — acceptable
  >>>>>>> REPLACE
  ```

### 4. `viking_girlfriend_skill/data/knowledge_reference/populate.py`

**Issue:** B310 (urllib_urlopen)
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **Description:** Audit url open for permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected and can lead to SSRF (Server-Side Request Forgery) or local file read vulnerabilities.
- **Analysis:** The script uses `urllib.request.urlopen` with dynamically constructed URLs. While it appears to only query `https://en.wikipedia.org/w/api.php`, the use of `urllib.request.urlopen` without scheme validation is a general security risk flagged by Bandit.
- **Recommended Change:** Explicitly validate that the URL starts with `http://` or `https://` before calling `urlopen`, and then add `# nosec B310` to suppress the warning.

  ```python
  <<<<<<< SEARCH
              try:
                  req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                  with urllib.request.urlopen(req) as response:
  =======
              try:
                  if not url.lower().startswith(('http://', 'https://')):
                      raise ValueError("Invalid URL scheme")
                  req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                  with urllib.request.urlopen(req) as response:  # nosec B310
  >>>>>>> REPLACE
  ```

  (Apply to both occurrences in `fetch_category_members` and `fetch_extracts_in_batches` functions).
