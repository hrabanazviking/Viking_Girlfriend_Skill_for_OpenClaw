# Bug Report - 2026-04-04

## Security Vulnerabilities (Bandit)
- **B310 (urllib_urlopen):** Discovered in `viking_girlfriend_skill/data/knowledge_reference/populate.py`. The `urlopen` call was passing a URL directly without validation, risking SSRF or Path Traversal if a `file://` or custom protocol was fed.
  - **Resolution:** Added URL scheme validation (`if not url.startswith("http://") and not url.startswith("https://")`) and then a `# nosec B310` ignore tag.

## Code Quality & Logic Errors (Pytest / Flake8 / Pylint)
- **TypeError in `test_e2e_system.py`:** The `build_messages` function returned a tuple containing `(messages_list, verification_mode)`, but callers assumed it was a flat list and attempted to unpack dictionaries from it with string indices.
  - **Resolution:** Unpacked the return correctly using `messages_raw, mode = self.synth.build_messages(...)`.
- **SystemExit in Test Framework:** In `tests/test_huginn.py`, a `sys.exit(1)` call was executed upon failure, crashing the entire test session instead of merely failing that individual test module.
  - **Resolution:** Removed the `sys.exit(1)` statement and replaced it with standard `pytest.fail()`.
- **Timing Condition in File Watcher (`test_synthesizer_hotreload.py`):** The `PromptSynthesizer`'s hot reload tests relied on polling file modification times (`mtime`) immediately. Because modern file systems write extremely quickly, the timestamps matched the previous snapshots, causing the `assert` on the file change detection event to fail.
  - **Resolution:** Introduced a `time.sleep(0.1)` delay before the file rewrite to ensure the `mtime` delta registers on subsequent polling.
- **Missing Mocked Dependencies:** The `MimirWell` module attempted to connect to `chromadb` during initialization, while `test_metabolism_hamingja.py` failed due to a missing `psutil` dependency.
  - **Resolution:** Installed the required dependencies to properly load.
- **Unused Coroutines & Missing Awaits (`trust_engine.py`, `prompt_synthesizer.py`, `model_router_client.py`):** State bus `publish_state` methods are asynchronous, but modules called them without awaiting them. This resulted in `RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited`.
  - **Resolution:** Synchronous functions trying to call asynchronous ones were updated to fetch the `asyncio.get_event_loop()`. If the loop was running, `loop.create_task()` was employed; otherwise `loop.run_until_complete()` or `asyncio.run()`.

## Best Practices going forward
- Keep dependencies locked and clearly documented (e.g. explicitly validating Python requirements such as `chromadb` and `psutil`).
- Explicitly mock or inject test configurations to isolate I/O boundaries from the rest of the application context.
