# Security Scan Report

## Date
2026-06-05

## Overview
A Bandit static analysis security scan was performed on the codebase. One major issue was detected related to improper URL opening.

## Findings

### B310: Audit url open for permitted schemes
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Lines**: 27, 62
- **Issue description**: The use of `urllib.request.urlopen` is susceptible to SSRF (Server-Side Request Forgery) and path traversal if it opens unexpected schemes like `file://` or `ftp://`.

#### Code Location 1
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```

#### Code Location 2
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```

## Research & Mitigations

### Vulnerability Explanation
As found via online research (Stack Overflow discussion on "Audit url open for permitted schemes"):
- `urllib` can open more than just `http://` or `https://` URLs; it can also handle `ftp://` and `file://`.
- This feature is a security risk because if an attacker can manipulate the URL, they might be able to read local files from the server where the code is executing.

### Recommended Code Changes
To fix this and satisfy the security linter, the URLs should be validated to ensure they only use `http` or `https` schemes before being opened. We can then add `# nosec B310` to suppress the Bandit warning, since we are handling the validation manually.

**Location 1 Changes (`viking_girlfriend_skill/data/knowledge_reference/populate.py` around line 27):**
```python
<<<<<<< SEARCH
        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
=======
        while True:
            try:
                if not url.lower().startswith(('http://', 'https://')):
                    raise ValueError(f"Invalid URL scheme: {url}")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
>>>>>>> REPLACE
```

**Location 2 Changes (`viking_girlfriend_skill/data/knowledge_reference/populate.py` around line 62):**
```python
<<<<<<< SEARCH
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
=======
        try:
            if not url.lower().startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL scheme: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
>>>>>>> REPLACE
```
