# Code Scan & Bug Report: 2026-04-26

## Security Issues (Bandit)

- **./infra/bootstrap_host.py** (Line 3): [LOW] Consider possible security implications associated with the subprocess module.
- **./infra/bootstrap_host.py** (Line 15): [LOW] subprocess call - check for execution of untrusted input.
- **./research_data/tests/test_memory_and_persona.py** (Line 15): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./research_data/tests/test_memory_and_persona.py** (Line 17): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./research_data/tests/test_memory_and_persona.py** (Line 25): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./research_data/tests/test_memory_and_persona.py** (Line 26): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./research_data/tests/test_memory_and_persona.py** (Line 27): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./research_data/tests/test_micro_rag_and_truth.py** (Line 28): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./research_data/tests/test_micro_rag_and_truth.py** (Line 29): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./research_data/tests/test_micro_rag_and_truth.py** (Line 45): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_cycle_length.py** (Line 20): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_cycle_length.py** (Line 23): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_cycle_length.py** (Line 26): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_cycle_length.py** (Line 29): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_cycle_length.py** (Line 32): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_cycle_length.py** (Line 43): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_stochastic.py** (Line 33): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_stochastic.py** (Line 39): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_stochastic.py** (Line 47): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
- **./tests/test_bio_stochastic.py** (Line 56): [LOW] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.

*Note: Output truncated. Many assert statements detected in test files.*

## Type Issues (Mypy)

- **viking_girlfriend_skill/scripts/config_loader.py** (Line 24): Library stubs not installed for "yaml"  [import-untyped]
- **viking_girlfriend_skill/scripts/trust_engine.py** (Line 588): Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- **viking_girlfriend_skill/scripts/trust_engine.py** (Line 764): Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- **viking_girlfriend_skill/scripts/security.py** (Line 508): Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- **viking_girlfriend_skill/scripts/security.py** (Line 612): Incompatible types in assignment (expression has type "frozenset[str]", variable has type "set[str]")  [assignment]
- **viking_girlfriend_skill/scripts/scheduler.py** (Line 436): Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- **viking_girlfriend_skill/scripts/scheduler.py** (Line 499): Cannot find implementation or library stub for module named "apscheduler.schedulers.background"  [import-not-found]
- **viking_girlfriend_skill/scripts/project_generator.py** (Line 231): Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- **viking_girlfriend_skill/scripts/oracle.py** (Line 36): Library stubs not installed for "yaml"  [import-untyped]
- **viking_girlfriend_skill/scripts/metabolism.py** (Line 35): Library stubs not installed for "psutil"  [import-untyped]
- **viking_girlfriend_skill/scripts/ethics.py** (Line 490): Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- **viking_girlfriend_skill/scripts/dream_engine.py** (Line 387): Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- **viking_girlfriend_skill/scripts/bio_engine.py** (Line 32): Library stubs not installed for "yaml"  [import-untyped]
- **viking_girlfriend_skill/scripts/runtime_kernel.py** (Line 291): Cannot infer type of lambda  [misc]
- **viking_girlfriend_skill/scripts/mimir_well.py** (Line 44): Library stubs not installed for "yaml"  [import-untyped]
- **viking_girlfriend_skill/scripts/environment_mapper.py** (Line 267): Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- **viking_girlfriend_skill/scripts/vordur.py** (Line 687): Item "None" of "Any | None" has no attribute "complete"  [union-attr]
- **viking_girlfriend_skill/scripts/vordur.py** (Line 774): Module "scripts.mimir_well" has no attribute "VerdictLabel"  [attr-defined]
- **viking_girlfriend_skill/scripts/vordur.py** (Line 1298): Item "None" of "Any | None" has no attribute "complete"  [union-attr]
- **viking_girlfriend_skill/scripts/vordur.py** (Line 1881): Item "None" of "Any | None" has no attribute "complete"  [union-attr]

## Code Quality Issues (Pylint)

Found many issues, top few shown:
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 1087): C0301 Line too long (102/100) (line-too-long)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 1159): C0301 Line too long (106/100) (line-too-long)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 1): C0302 Too many lines in module (1325/1000) (too-many-lines)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 121): R1702 Too many nested blocks (6/5) (too-many-nested-blocks)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 162): R0902 Too many instance attributes (10/7) (too-many-instance-attributes)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 214): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 295): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 306): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 357): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 366): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 401): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 412): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 420): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 455): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 463): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 473): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 511): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 521): C0116 Missing function or method docstring (missing-function-docstring)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 543): C0103 Attribute name "DECAY_PER_TURN" doesn't conform to snake_case naming style (invalid-name)
- **viking_girlfriend_skill/scripts/wyrd_matrix.py** (Line 544): C0103 Attribute name "DECAY_RATE" doesn't conform to snake_case naming style (invalid-name)

## Recommended Fixes

1. **Unused Coroutines**: Await or properly schedule all async functions (e.g., `Coroutine[Any, Any, None] must be used`).
2. **Missing Imports/Undefined Variables**: Fix missing imports like `VerificationMode` in `main.py`.
3. **Type Checking Errors**: Address type mismatches, e.g., assigning `OracleState` to `WyrdState` variables, and assigning `frozenset` to `set`.
4. **Security Warnings**: Remove or appropriately use `assert` statements outside of tests, and be cautious with `subprocess` calls by sanitizing inputs.
5. **General Catch Exceptions**: Refactor `except Exception: pass` blocks to at least log warnings to prevent silent failures.

## Online Research Findings

### Context Overflow (Soul Eviction)
- Models operating at full context window limits can start 'evicting' their system prompts, losing critical instructions.
- Mitigation: Implement a lightweight context telemetry module to monitor token usage and warn before truncation occurs.

### Weak Hashing
- MD5 is used for cache keys in some scripts. While not directly for security, it is best practice to either use `hashlib.sha256()` or explicitly mark it with `usedforsecurity=False` in Python 3.9+.

### Subprocess Vulnerabilities
- Python's `subprocess` module can execute untrusted code if inputs aren't sanitized. It is recommended to use `shlex.quote()` on any dynamic arguments.

### Mypy "unused-coroutine" error
- Mypy reports `"Coroutine[Any, Any, None]" must be used [unused-coroutine]` when an async function is called but not awaited or used. This is a common bug in async Python code resulting in the coroutine not executing.

### Bandit "Test in comment" warning
- Bandit issues a warning like `[manager] WARNING Test in comment: ... is not a test name or id, ignoring` when it parses comments that have words incorrectly interpreted as test names or ids (e.g., `# nosec B311 - jitter, not cryptographic` might interpret `jitter` or `cryptographic` as the test name rather than just reading `B311`). The `# nosec` pragma should be strictly `# nosec B311`.
