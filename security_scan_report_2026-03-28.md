# Security Scan Report

**Date:** 2026-03-28

## Overview
This document outlines the findings from a recent Static Application Security Testing (SAST) run using [Bandit](https://github.com/PyCQA/bandit) on the Viking Girlfriend Skill codebase. Bandit is designed to find common security issues in Python code.

## Key Findings & Resolutions

### 1. Hardcoded Subprocess Execution (infra/bootstrap_host.py)
**Issue Details:**
- `infra/bootstrap_host.py:3` - Consider possible security implications associated with the subprocess module.
- `infra/bootstrap_host.py:15` - subprocess call - check for execution of untrusted input.

**Context:** The script used `subprocess.run` to check if certain commands (`podman`, `docker`, `nvidia-smi`) existed on the host. This triggered warnings B404 (importing subprocess) and B603 (subprocess without shell equals true).

**Resolution:**
Replaced `subprocess.run` with `shutil.which()`, which is a much safer and cleaner way to check for command existence without spawning external processes.

### 2. URL Open for Permitted Schemes (viking_girlfriend_skill/data/knowledge_reference/populate.py)
**Issue Details:**
- `populate.py:27` & `populate.py:62` - Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

**Context:**
The code used `urllib.request.urlopen` with a URL built using the Wikipedia API endpoint `https://en.wikipedia.org/w/api.php...`. Bandit flags `urlopen` with warning B310 by default because it can potentially open dangerous file schemes if user input controls the URL.

**Resolution:**
Since the URL string starts with a hardcoded `https://en.wikipedia.org` base, the risk is zero. This is a false positive. We added `# nosec B310` to the lines with `urlopen` to explicitly inform Bandit that this specific line is safe.

### 3. Assert Statements in Tests
**Issue Details:**
Numerous B101 warnings were reported in `tests/` such as:
- `tests/test_vordur_repair.py`
- `tests/test_vordur_trigger.py`
- `tests/test_wyrd_vitality_modulation.py`

**Context:**
Bandit warns against using `assert` statements because they are removed when Python runs with optimized byte code (`-O`).

**Resolution:**
This is a common false positive for test suites using PyTest, as PyTest relies heavily on `assert` statements. No code changes are required. The warnings can be safely ignored.

## Summary of Bandit Error Codes Mentioned
- **B101 (assert_used):** Warns about the use of `assert`.
- **B310 (urllib_urlopen):** Warns about `urllib.request.urlopen` usage which can permit `file://` schemes.
- **B404 (import_subprocess):** Warns about importing the `subprocess` module.
- **B603 (subprocess_without_shell_equals_true):** Warns about the use of `subprocess` methods with `shell=False`.

## Recommendations for Future Work
- Always review SAST findings carefully to differentiate between legitimate vulnerabilities and false positives.
- Continue to run Bandit in the CI/CD pipeline to catch potential issues early.
- When ignoring false positives, always use targeted suppression (e.g., `# nosec B310`) rather than a blanket `# nosec` to avoid masking real issues that might be introduced later.