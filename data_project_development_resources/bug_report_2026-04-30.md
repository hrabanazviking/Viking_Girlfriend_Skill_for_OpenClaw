# Codebase Scan Report - 2026-04-30

## Bandit Security Scan

- **Issue**: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
  - **File**: viking_girlfriend_skill/data/knowledge_reference/populate.py:27
  - **Severity**: MEDIUM, **Confidence**: HIGH
  - **Recommendation**: Validate the URL scheme before calling `urllib.request.urlopen` to ensure it only starts with `http://` or `https://` to prevent B310 SSRF/Path Traversal vulnerabilities. Then append `# nosec B310` to suppress the warning.

- **Issue**: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
  - **File**: viking_girlfriend_skill/data/knowledge_reference/populate.py:62
  - **Severity**: MEDIUM, **Confidence**: HIGH
  - **Recommendation**: Validate the URL scheme before calling `urllib.request.urlopen` to ensure it only starts with `http://` or `https://` to prevent B310 SSRF/Path Traversal vulnerabilities. Then append `# nosec B310` to suppress the warning.

## Flake8 Report (Sample)

```
viking_girlfriend_skill/data/knowledge_reference/populate.py:5:1: F401 'sys' imported but unused
viking_girlfriend_skill/data/knowledge_reference/populate.py:8:1: E302 expected 2 blank lines, found 1
viking_girlfriend_skill/data/knowledge_reference/populate.py:14:80: E501 line too long (82 > 79 characters)
viking_girlfriend_skill/data/knowledge_reference/populate.py:22:80: E501 line too long (160 > 79 characters)
viking_girlfriend_skill/data/knowledge_reference/populate.py:23:1: W293 blank line contains whitespace
viking_girlfriend_skill/data/knowledge_reference/populate.py:26:80: E501 line too long (103 > 79 characters)
viking_girlfriend_skill/data/knowledge_reference/populate.py:29:1: W293 blank line contains whitespace
viking_girlfriend_skill/data/knowledge_reference/populate.py:42:80: E501 line too long (220 > 79 characters)
viking_girlfriend_skill/data/knowledge_reference/populate.py:48:28: E261 at least two spaces before inline comment
viking_girlfriend_skill/data/knowledge_reference/populate.py:52:1: E302 expected 2 blank lines, found 1
viking_girlfriend_skill/data/knowledge_reference/populate.py:58:80: E501 line too long (136 > 79 characters)
viking_girlfriend_skill/data/knowledge_reference/populate.py:59:1: W293 blank line contains whitespace
viking_girlfriend_skill/data/knowledge_reference/populate.py:61:80: E501 line too long (99 > 79 characters)
viking_girlfriend_skill/data/knowledge_reference/populate.py:67:80: E501 line too long (82 > 79 characters)
viking_girlfriend_skill/data/knowledge_reference/populate.py:73:1: E302 expected 2 blank lines, found 1
viking_girlfriend_skill/data/knowledge_reference/populate.py:75:64: E261 at least two spaces before inline comment
viking_girlfriend_skill/data/knowledge_reference/populate.py:75:80: E501 line too long (143 > 79 characters)
viking_girlfriend_skill/data/knowledge_reference/populate.py:77:1: W293 blank line contains whitespace
viking_girlfriend_skill/data/knowledge_reference/populate.py:79:1: W293 blank line contains whitespace
viking_girlfriend_skill/data/knowledge_reference/populate.py:81:80: E501 line too long (119 > 79 characters)
...
```

## Pylint Report (Sample)

```
            state = self.get_state()
            event = StateEvent( (duplicate-code)
viking_girlfriend_skill/data/knowledge_reference/populate.py:1:0: R0801: Similar lines in 2 files
==scripts.huginn:[611:616]
==scripts.mimir_well:[2369:2374]
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(bus.publish_state(event, nowait=True))
                else:
                    loop.run_until_complete(bus.publish_state(event, nowait=True)) (duplicate-code)
viking_girlfriend_skill/data/knowledge_reference/populate.py:1:0: R0401: Cyclic import (scripts.model_router_client -> scripts.vordur) (cyclic-import)

-----------------------------------
Your code has been rated at 8.69/10

```

## Mypy Report (Sample)

```
viking_girlfriend_skill/scripts/prompt_synthesizer.py:740: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/prompt_synthesizer.py:740: note: Are you missing an await?
viking_girlfriend_skill/scripts/prompt_synthesizer.py:907: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/prompt_synthesizer.py:907: note: Are you missing an await?
viking_girlfriend_skill/scripts/memory_store.py:1006: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/memory_store.py:1006: note: Are you missing an await?
viking_girlfriend_skill/scripts/cove_pipeline.py:364: error: Name "draft" already defined on line 318  [no-redef]
viking_girlfriend_skill/scripts/main.py:68: error: Library stubs not installed for "psutil"  [import-untyped]
viking_girlfriend_skill/scripts/main.py:68: note: Hint: "python3 -m pip install types-psutil"
viking_girlfriend_skill/scripts/main.py:511: error: Incompatible types in assignment (expression has type "BioState", variable has type "WyrdState")  [assignment]
viking_girlfriend_skill/scripts/main.py:512: error: "WyrdState" has no attribute "phase_name"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:512: error: "WyrdState" has no attribute "energy_modifier"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:512: error: "WyrdState" has no attribute "narrative_hint"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:520: error: Incompatible types in assignment (expression has type "DreamState", variable has type "WyrdState")  [assignment]
viking_girlfriend_skill/scripts/main.py:521: error: "WyrdState" has no attribute "prompt_fragment"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:522: error: "WyrdState" has no attribute "prompt_fragment"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:529: error: Incompatible types in assignment (expression has type "OracleState", variable has type "WyrdState")  [assignment]
viking_girlfriend_skill/scripts/main.py:530: error: "WyrdState" has no attribute "prompt_summary"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:635: error: Need type annotation for "messages" (hint: "messages: list[<type>] = ...")  [var-annotated]
Found 38 errors in 19 files (checked 26 source files)
```

## Research on Identified Issues

### B310: urllib_urlopen
The `urllib.request.urlopen` function can be exploited if an attacker controls the URL and uses a `file://` scheme to read local files (Path Traversal) or makes the server request internal resources (SSRF). To mitigate this, explicitly check that the URL scheme is `http` or `https` before making the request. In Python, this can be done by parsing the URL with `urllib.parse.urlparse` and checking the `scheme` attribute.

### Mypy Typing Errors
Mypy is reporting errors such as '"WyrdState" has no attribute "phase_name"' which means that properties are being accessed on a base class or an unexpected type that do not exist. To fix these, either ensure the variable is typed correctly (e.g., using `isinstance` checks or correct type hinting) or add the missing attributes to the base class if appropriate.

## E2E Testing Failures

During testing with pytest, multiple tests failed due to a `TypeError` in `test_e2e_system.py` when unpacking the result of `synth.build_messages()`. According to the project memory and the signature of `PromptSynthesizer.build_messages()`, it returns a tuple `(messages_raw, verification_mode)`, not just a list. Callers must unpack it correctly, e.g., `messages_raw, mode = synth.build_messages(...)` to avoid TypeErrors when assuming it returns a flat list.



## Mypy Type Errors

Mypy is reporting errors such as '"WyrdState" has no attribute "phase_name"'. This indicates that attributes are being accessed on the base `WyrdState` class that are only present in specific subclasses (like `DreamState`, `OracleState`, or `BioState`). The variables need to be type-hinted or narrowed correctly.

There are also warnings about unused coroutines in `prompt_synthesizer.py`, `memory_store.py`, and `trust_engine.py` (e.g., `bus.publish_state`). As noted in memory, these methods are coroutines and must be explicitly `await`ed or correctly scheduled via `loop.create_task` or `loop.run_until_complete` if running synchronously.

### Detailed URLs and References for Mitigation
- Bandit B310: https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html#b310-urllib-urlopen
