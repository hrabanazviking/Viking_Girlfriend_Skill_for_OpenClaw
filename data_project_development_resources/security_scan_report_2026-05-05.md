# Security Scan Report - 2026-05-05

## Overview
A static application security testing (SAST) scan was performed using Bandit. Below are the findings, excluding test files where appropriate, and actionable recommendations.

## Findings

### B404: Consider possible security implications associated with the subprocess module.
**Count:** 1

**Recommendation:**
- **Issue:** Use of `subprocess` without careful validation of inputs can lead to command injection vulnerabilities.
- **Action:** Ensure inputs to `subprocess` calls are strictly controlled and not user-supplied. If the commands are static/hardcoded, append `# nosec B404` and `# nosec B603` to the import and function call lines.

**Examples:**
- File: `./infra/bootstrap_host.py` (Line: 3)
  ```python
2 import sys
3 import subprocess
4 import platform
  ```

---

### B603: subprocess call - check for execution of untrusted input.
**Count:** 1

**Recommendation:**
- **Issue:** Use of `subprocess` without careful validation of inputs can lead to command injection vulnerabilities.
- **Action:** Ensure inputs to `subprocess` calls are strictly controlled and not user-supplied. If the commands are static/hardcoded, append `# nosec B404` and `# nosec B603` to the import and function call lines.

**Examples:**
- File: `./infra/bootstrap_host.py` (Line: 15)
  ```python
14     try:
15         subprocess.run([command, "--version"], capture_output=True, check=True)
16         return True
  ```

---

### B101: Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
**Count:** 745

**Recommendation:**
- **Issue:** Use of `assert` in production code is dangerous as it can be disabled by running Python with the `-O` flag.
- **Action:** Replace `assert` statements in production code with proper error handling (e.g., `raise ValueError(...)`). For test files, `assert` is typically acceptable and expected when using pytest.

**Examples:**
- File: `./research_data/tests/test_memory_and_persona.py` (Line: 15)
  ```python
14     results = store.search("calm mystical guide")
15     assert results
16     promoted = store.promote(record.record_id)
  ```
- File: `./research_data/tests/test_memory_and_persona.py` (Line: 17)
  ```python
16     promoted = store.promote(record.record_id)
17     assert promoted.truth.approval_state == "approved"
18
  ```
- File: `./research_data/tests/test_memory_and_persona.py` (Line: 25)
  ```python
24     packet = compiler.compile(persona_id="persona:veyrunn", user_id="user:volmarr", mode=PersonaMode.COMPANION, records=[record], bond_edge=bond)
25     assert packet.persona_id == "persona:veyrunn"
26     assert packet.identity_core
  ```
- *...and 742 more instances.*

---

### B110: Try, Except, Pass detected.
**Count:** 2

**Recommendation:**
- **Issue:** `try/except/pass` blocks silence exceptions, which can hide critical errors and make debugging difficult.
- **Action:** Log the exception instead of passing, or explicitly state why it is safe to ignore it using a comment. If it's expected, catch specific exceptions rather than broad `Exception`.

**Examples:**
- File: `./tests/test_cove_pipeline.py` (Line: 256)
  ```python
255             cove._cb_pipeline.on_failure(RuntimeError("test failure"))
256         except Exception:
257             pass
258
  ```
- File: `./tests/test_e2e_system.py` (Line: 169)
  ```python
168             asyncio.run(bus.publish_state(ev, nowait=True))
169         except Exception:
170             pass  # offline / loop not running — acceptable
171
  ```

---

### B310: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
**Count:** 2

**Recommendation:**
- **Issue:** `urllib.request.urlopen` used without scheme validation can lead to Server-Side Request Forgery (SSRF) or Local File Inclusion (LFI) via `file://` schemes.
- **Action:** Validate that the URL scheme is strictly `http://` or `https://` before opening it. If it's safe and verified, append `# nosec B310` to suppress the warning.

**Examples:**
- File: `./viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line: 27)
  ```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
  ```
- File: `./viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line: 62)
  ```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
  ```

---

## Action Plan
1. **B310 (URL Open):** Add URL scheme validation (checking for `http://` or `https://`) in `viking_girlfriend_skill/data/knowledge_reference/populate.py` before calling `urllib.request.urlopen`, and add `# nosec B310` to bypass the bandit check.
2. **B404/B603 (Subprocess):** Add `# nosec B404` and `# nosec B603` to `infra/bootstrap_host.py` since the inputs are hardcoded commands.
3. **B110 (Try/Except/Pass):** The two instances in test files are acceptable as they are designed to ignore specific loop/pipeline errors during testing. Consider adding a comment or logging.
4. **B101 (Asserts):** The majority of these are in test files, which is expected for pytest. If any exist in production code, they should be converted to explicit exception raising.

## Mitigation Research Findings

### Subprocess Vulnerabilities (B404, B603)
- **Source:** [Bandit Documentation for B603](https://bandit.readthedocs.io/en/latest/plugins/b603_subprocess_without_shell_equals_true.html)
- **Details:** Python possesses many mechanisms to invoke an external executable. However, doing so may present a security issue if appropriate care is not taken to sanitize any user provided or variable input. This type of subprocess invocation is not vulnerable to shell injection attacks, but care should still be taken to ensure validity of input.
- **Remediation:** In order for the code to be secure, you need to know that arguments passed to `subprocess.run` aren't malicious. Once you know the subprocess line is secure, you can add `# nosec` comment to tell bandit not to give a warning about the line.

### URL Open Vulnerabilities (B310)
- **Source:** [Bandit Documentation for B310](https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b310-urllib-urlopen)
- **Details:** Audit url open for permitted schemes. Allowing use of `file:` or custom schemes is often unexpected and could lead to Server Side Request Forgery (SSRF) vulnerabilities.
- **Remediation:** Validate that URLs being opened strictly begin with `http://` or `https://` schemes before attempting to open them. Once validated, `# nosec` can be appended to the line to bypass Bandit.
