# Security and Bug Report (2026-05-10)

## Bandit Issues

- `viking_girlfriend_skill/data/knowledge_reference/populate.py`: Lines 27 and 62 use `urllib.request.urlopen` without validating the URL scheme.
  - **Issue description**: This is a potential Server-Side Request Forgery (SSRF) and Path Traversal vulnerability (CWE-22). The `urlopen` call might allow access to unexpected locations like `file://` if the provided URL is not sanitized. (Reference: [Bandit B310 Documentation](https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html), [CWE-22 Description](https://cwe.mitre.org/data/definitions/22.html))
  - **Recommendation**: Add a check to restrict schemes: `if not url.startswith('https://'): raise ValueError('Invalid URL schema')` before the `urlopen` call. After securing the call, use `# nosec B310` to suppress the Bandit warning.

## Pylint Issues

- **Missing dependencies**: Pylint reports missing dependencies for `psutil`, `litellm`, `chromadb`, `requests`, `ollama` in various scripts.
  - **Recommendation**: Ensure the environment executing Pylint or the project itself properly installs these dependencies (found in `requirements.txt`).
- `viking_girlfriend_skill/scripts/vordur.py`: Multiple instances of `# nosec B324` were found, but Pylint/Bandit noted there was no failed test suppressed.
  - **Recommendation**: Review if `# nosec B324` is actually needed here.
- **Relative import errors**: Files in `research_data/src/wyrdforge/models/` and `micro_rag_pipeline.py` attempt relative imports beyond the top-level package.
  - **Recommendation**: Refactor module locations or use absolute imports correctly.
- `tests/test_e2e_system.py`: Sequence index is not an int, slice, or instance with `__index__` at lines 804, 813, 825.
  - **Recommendation**: Fix the array or dictionary access syntax at these lines.
- `tests/test_mimirvordur.py`: Methods `complete` and `smart_complete` are missing `self` as their first argument at lines 730, 742.
  - **Recommendation**: Add `self` to these method definitions if they are instance methods.
- `research_data/src/wyrdforge/models/bond.py`: Missing members in `FieldInfo` instance.
  - **Recommendation**: Correct the usage of the Pydantic `FieldInfo` instances.

## Flake8 Issues

- The codebase has over 7000 style and linting issues, with the top ones being:
  - `E501`: Line too long (6802 instances)
  - `F401`: Module imported but unused (149 instances)
  - `E999`: SyntaxError / IndentationError (107 instances) - many occur in generated files like `scripts/write_*.py`.
  - `E402`: Module level import not at top of file (90 instances)
  - **Recommendation**: Set up a code formatter like `black` or `yapf` to automatically fix formatting issues, and review `F401` unused imports. Fix indentation in the generator scripts or the generated scripts themselves.
