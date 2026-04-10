# Security & Bug Report: 2026-04-10

## Discovered Issues

### 1. Bandit B310: SSRF / Path Traversal in `populate.py`
**File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Lines:** 26-27, 61-62
**Description:** The script used `urllib.request.urlopen` directly with user-provided or dynamically generated URLs. Because the URL scheme was not constrained, this exposed the script to Server-Side Request Forgery (SSRF) and Local File Inclusion (LFI/Path Traversal) vulnerabilities (e.g. if the URL used the `file://` scheme).
**Fix:** Introduced URL validation before executing `urlopen()`. Specifically, the URL is checked to ensure it explicitly starts with `http://` or `https://` before opening. After applying validation, the lines were annotated with `# nosec B310` to suppress the Bandit warning.

### 2. Type Error in E2E Pipeline due to `PromptSynthesizer.build_messages()` Return Value Change
**File:** `tests/test_e2e_system.py`
**Description:** A system-wide architecture change updated `PromptSynthesizer.build_messages()` from returning a raw list `List[Dict[str, str]]` to returning a tuple `(List[Dict[str, str]], VerificationMode)`. Multiple end-to-end tests failed because they were assigning the list-operations (like `msgs[0]`) to the returned tuple, throwing `TypeError: list indices must be integers or slices, not str`.
**Fix:** Refactored test calls in `tests/test_e2e_system.py` to correctly unpack the tuple (`msgs, mode = self.synth.build_messages(...)`), restoring proper type mapping.

### 3. Prompt Injection Test Did Not Catch Exception
**File:** `tests/test_e2e_system.py`
**Description:** The security test `test_sanitize_prompt_injection_attempt` expected `sanitize_text_input` to return a cleaned string even when a prompt injection was flagged. The `SecurityLayer` logic instead actively blocked and raised a `SecurityViolation` when matching the "ignore_previous" pattern. This caused test crashes.
**Fix:** Modified the unit test to catch the expected failure using `with self.assertRaises(SecurityViolation):`.

### 4. Flaky File Watcher Hot-Reload Test
**File:** `tests/test_synthesizer_hotreload.py`
**Description:** `test_watcher_detects_file_change_and_reloads` tested `_IdentityFileWatcher`'s capability to detect identity file modifications based on the file modification timestamp (`mtime`). Because the test modified the file in the exact same millisecond that the snapshot occurred on fast SSDs, the watcher did not detect an mtime delta.
**Fix:** Introduced a `time.sleep(0.1)` gap between snapshot initialization and file rewriting, confirming mtime drift and passing the test.

## Execution and Checks
- **Static Analysis:** `bandit -r viking_girlfriend_skill/ -f json -q` now reports 0 High/Medium issues for `populate.py`.
- **Testing Suite:** `PYTHONPATH=./viking_girlfriend_skill pytest tests/` completed successfully with all E2E pipeline regression tests and hot reload tests passing.

---
_Auto-generated via system audit_