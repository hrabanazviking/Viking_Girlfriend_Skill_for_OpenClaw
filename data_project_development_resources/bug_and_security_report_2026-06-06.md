# Codebase Security and Bug Scan Report (2026-06-06)

## Bandit Static Application Security Testing (SAST) Results

### Vulnerability: B310 - blacklist
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 27)
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **CWE:** [22](https://cwe.mitre.org/data/definitions/22.html)
- **Description:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

**Code Snippet:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())

```

### Vulnerability: B310 - blacklist
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 62)
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **CWE:** [22](https://cwe.mitre.org/data/definitions/22.html)
- **Description:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

**Code Snippet:**
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())

```

## Research on B310: urllib.request.urlopen

**Description:**
The B310 vulnerability reported by Bandit indicates that `urllib.request.urlopen` is being used without explicitly verifying the URL scheme. `urllib` not only supports `http://` and `https://` URLs, but also local schemas like `file://` and `ftp://`.

**Security Risk:**
If the URL provided to `urllib.request.urlopen` is user-controllable or fetched from an untrusted source, an attacker could manipulate the URL to read local files on the system or access internal network services. This makes the application vulnerable to **Server-Side Request Forgery (SSRF)** (CWE-918) and **Path Traversal / Local File Inclusion** (CWE-22) attacks.

**Recommended Code Changes:**
Before opening the URL, validate that it uses an allowed and expected scheme (e.g., `http` or `https`). If the validation is successful, the `# nosec B310` comment can be appended to the `urlopen` line to acknowledge that the security check was performed and suppress the Bandit warning.

*Example Recommended Change for `viking_girlfriend_skill/data/knowledge_reference/populate.py`:*

```python
<<<<<<< SEARCH
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
=======
            if not url.lower().startswith(('http://', 'https://')):
                raise ValueError("Invalid URL scheme.")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
>>>>>>> REPLACE
```

## Pylint Scan Results (Selected issues)
************* Module scripts.wyrd_matrix
viking_girlfriend_skill/scripts/wyrd_matrix.py:1087:0: C0301: Line too long (102/100) (line-too-long)
viking_girlfriend_skill/scripts/wyrd_matrix.py:1159:0: C0301: Line too long (106/100) (line-too-long)
viking_girlfriend_skill/scripts/wyrd_matrix.py:1:0: C0302: Too many lines in module (1325/1000) (too-many-lines)
viking_girlfriend_skill/scripts/wyrd_matrix.py:121:4: R1702: Too many nested blocks (6/5) (too-many-nested-blocks)
viking_girlfriend_skill/scripts/wyrd_matrix.py:162:0: R0902: Too many instance attributes (10/7) (too-many-instance-attributes)
viking_girlfriend_skill/scripts/wyrd_matrix.py:214:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:295:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:306:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:357:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:366:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:401:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:412:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:420:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:455:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:463:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:473:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:511:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:521:4: C0116: Missing function or method docstring (missing-function-docstring)
viking_girlfriend_skill/scripts/wyrd_matrix.py:543:4: C0103: Attribute name "DECAY_PER_TURN" doesn't conform to snake_case naming style (invalid-name)

## Flake8 Scan Results (Selected issues)
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

## Mypy Static Type Checking Results
A number of typing issues were identified. Below is a subset focusing on critical errors:

```text
viking_girlfriend_skill/scripts/config_loader.py:24: error: Library stubs not installed for "yaml"  [import-untyped]
viking_girlfriend_skill/scripts/trust_engine.py:588: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/trust_engine.py:764: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/security.py:508: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/security.py:612: error: Incompatible types in assignment (expression has type "frozenset[str]", variable has type "set[str]")  [assignment]
viking_girlfriend_skill/scripts/scheduler.py:436: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/scheduler.py:499: error: Cannot find implementation or library stub for module named "apscheduler.schedulers.background"  [import-not-found]
viking_girlfriend_skill/scripts/project_generator.py:231: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/oracle.py:36: error: Library stubs not installed for "yaml"  [import-untyped]
viking_girlfriend_skill/scripts/metabolism.py:35: error: Library stubs not installed for "psutil"  [import-untyped]
viking_girlfriend_skill/scripts/ethics.py:490: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/dream_engine.py:387: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/bio_engine.py:32: error: Library stubs not installed for "yaml"  [import-untyped]
viking_girlfriend_skill/scripts/runtime_kernel.py:291: error: Cannot infer type of lambda  [misc]
viking_girlfriend_skill/scripts/mimir_well.py:44: error: Library stubs not installed for "yaml"  [import-untyped]
viking_girlfriend_skill/scripts/environment_mapper.py:267: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/vordur.py:687: error: Item "None" of "Any | None" has no attribute "complete"  [union-attr]
viking_girlfriend_skill/scripts/vordur.py:774: error: Module "scripts.mimir_well" has no attribute "VerdictLabel"  [attr-defined]
viking_girlfriend_skill/scripts/vordur.py:1298: error: Item "None" of "Any | None" has no attribute "complete"  [union-attr]
viking_girlfriend_skill/scripts/vordur.py:1881: error: Item "None" of "Any | None" has no attribute "complete"  [union-attr]
viking_girlfriend_skill/scripts/model_router_client.py:518: error: Library stubs not installed for "requests"  [import-untyped]
viking_girlfriend_skill/scripts/model_router_client.py:1267: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/prompt_synthesizer.py:430: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/prompt_synthesizer.py:740: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/prompt_synthesizer.py:907: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/memory_store.py:1006: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/cove_pipeline.py:364: error: Name "draft" already defined on line 318  [no-redef]
viking_girlfriend_skill/scripts/main.py:68: error: Library stubs not installed for "psutil"  [import-untyped]
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
```


## Mypy Issues Research

**Unused Coroutine (`[unused-coroutine]`)**
Many errors like `Value of type "Coroutine[Any, Any, None]" must be used` were found across multiple files (`prompt_synthesizer.py`, `memory_store.py`, `trust_engine.py`, etc.).
- **Cause:** This happens when an asynchronous function (`async def`) is called but its result is neither `await`ed nor scheduled as a task (e.g., `asyncio.create_task()`).
- **Risk:** The asynchronous operation will never execute, leading to silent failures, missing state updates, or incomplete operations.
- **Recommended Fix:** Explicitly `await` the function call if in an async context. If called from a synchronous context, it must be scheduled using the appropriate event loop methods.

**Missing Type Stubs (`[import-untyped]`)**
Errors related to `yaml`, `psutil`, `requests`.
- **Cause:** Mypy cannot find type definitions for these third-party libraries.
- **Recommended Fix:** Install the corresponding type stubs. For example, `pip install types-PyYAML types-psutil types-requests`.
