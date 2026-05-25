# Bandit Security Scan Report (2026-05-25)

## Overview
A static application security test (SAST) was conducted using Bandit against the project codebase. The initial findings highlight a few low to medium severity issues, mostly tied to Python module usages known for potential security pitfalls.

## Findings Details

### B404 - Consider possible security implications associated with the subprocess module.
- **File**: `./infra/bootstrap_host.py`
- **Line**: 3
- **Severity**: LOW
- **Confidence**: HIGH
- **CWE**: [78](https://cwe.mitre.org/data/definitions/78.html)
- **More Info**: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess

**Code Snippet**:
```python
2 import sys
3 import subprocess
4 import platform
```

### B603 - subprocess call - check for execution of untrusted input.
- **File**: `./infra/bootstrap_host.py`
- **Line**: 15
- **Severity**: LOW
- **Confidence**: HIGH
- **CWE**: [78](https://cwe.mitre.org/data/definitions/78.html)
- **More Info**: https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html

**Code Snippet**:
```python
14     try:
15         subprocess.run([command, "--version"], capture_output=True, check=True)
16         return True
```

### B110 - Try, Except, Pass detected.
- **File**: `./tests/test_cove_pipeline.py`
- **Line**: 256
- **Severity**: LOW
- **Confidence**: HIGH
- **CWE**: [703](https://cwe.mitre.org/data/definitions/703.html)
- **More Info**: https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html

**Code Snippet**:
```python
255             cove._cb_pipeline.on_failure(RuntimeError("test failure"))
256         except Exception:
257             pass
258
```

### B110 - Try, Except, Pass detected.
- **File**: `./tests/test_e2e_system.py`
- **Line**: 169
- **Severity**: LOW
- **Confidence**: HIGH
- **CWE**: [703](https://cwe.mitre.org/data/definitions/703.html)
- **More Info**: https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html

**Code Snippet**:
```python
168             asyncio.run(bus.publish_state(ev, nowait=True))
169         except Exception:
170             pass  # offline / loop not running — acceptable
171
```

### B310 - Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **File**: `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line**: 27
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **CWE**: [22](https://cwe.mitre.org/data/definitions/22.html)
- **More Info**: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

**Code Snippet**:
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```

### B310 - Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **File**: `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line**: 62
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **CWE**: [22](https://cwe.mitre.org/data/definitions/22.html)
- **More Info**: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

**Code Snippet**:
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```

## Recommended Fixes

1. **B404 and B603 in `infra/bootstrap_host.py`**:
   - Issue: Bandit flags the `subprocess` import (B404) and `subprocess.run` call (B603) because executing system commands is inherently risky.
   - Fix: The command executed (`command + "--version"`) is derived from statically hardcoded commands like `"docker"` or `"podman"`. To suppress the warnings, append `# nosec B404` to the import and `# nosec B603` to the line with `subprocess.run`.
2. **B110 in tests**:
   - Issue: Capturing `Exception` with `pass` silently swallows errors.
   - Fix: While acceptable in tests, it's safer to catch specific exceptions or add `# nosec B110`. The instruction says we should not modify tests unless explicitly necessary. I will only document this.
3. **B310 in `viking_girlfriend_skill/data/knowledge_reference/populate.py`**:
   - Issue: `urllib.request.urlopen` is flagged because it might allow local file read using `file://` scheme if the URL is user-controlled.
   - Fix: Explicitly check that `url.startswith('http://') or url.startswith('https://')` before making the request, then append `# nosec B310`.
