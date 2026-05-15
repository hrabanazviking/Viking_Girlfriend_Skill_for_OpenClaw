## Bug Scan Report - 2026-05-15

### Bandit Scanning Results

A static security scan using Bandit was performed on the `viking_girlfriend_skill/` codebase. The scan identified the following medium-severity security issues (B310):

**Issue 1: Audit url open for permitted schemes**
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Lines:** 27, 62
- **CWE:** [CWE-22](https://cwe.mitre.org/data/definitions/22.html)
- **Description:** The `urllib.request.urlopen` function is used to open URLs provided as variables. If these URLs are not validated, they could allow arbitrary local file reading (if a `file://` scheme is supplied) or Server Side Request Forgery (SSRF) attacks.
- **Code context:**
  ```python
  26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  27                 with urllib.request.urlopen(req) as response:
  28                     data = json.loads(response.read().decode())
  ```
  And similarly on line 62.

### Research and Analysis of Bandit B310 Vulnerability

According to DeepSource and Bandit documentation, `urllib.request.urlopen` not only opens `http://` or `https://` URLs but also `ftp://` and `file://`. Opening local files on the executing machine is a security risk if the URL can be manipulated by an external user. Performing requests from user-provided data could allow attackers to make requests on the internal network or change, retrieve, or delete sensitive information.

**Recommended Solution:**
To mitigate this issue, explicitly validate the URL scheme before calling `urlopen`. In our case, `url` always points to `https://en.wikipedia.org/...`, but as a best practice, the validation should be explicit. After validation, we can safely append `# nosec B310` to ignore the Bandit warning.

### Recommended Code Changes for `viking_girlfriend_skill/data/knowledge_reference/populate.py`

```python
<<<<<<< SEARCH
        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
=======
        while True:
            try:
                if not url.startswith('https://en.wikipedia.org/'):
                    raise ValueError(f"Invalid URL scheme or domain: {url}")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

```python
<<<<<<< SEARCH
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
=======
        try:
            if not url.startswith('https://en.wikipedia.org/'):
                raise ValueError(f"Invalid URL scheme or domain: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
                data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

### Other Code Quality Observations

We ran Flake8 and Pylint on the codebase. They identified numerous stylistic and structural issues, primarily:
- Line length violations (E501 in Flake8, C0301 in Pylint)
- Missing docstrings (C0116 in Pylint)
- Too many attributes or complex functions (R0902, R1702 in Pylint)
- Unused imports (F401 in Flake8)

No other major logic bugs were prominently identified. It is recommended to run formatting tools like `black` or `autopep8` to fix structural issues progressively.
