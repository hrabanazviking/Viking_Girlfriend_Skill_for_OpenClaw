# Security Scan Report: 2026-05-15

## Overview
A security scan was performed using `bandit`. We identified medium severity vulnerabilities related to Server-Side Request Forgery (SSRF) and Path Traversal within the `populate.py` script.

## Vulnerabilities Identified

### 1. Medium Severity: SSRF / Path Traversal Risk (Bandit B310)
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Lines:** 27, 62
- **Issue:** The script uses `urllib.request.urlopen` without validating that the URL scheme is strictly `http` or `https`. This can potentially allow an attacker to read local files via `file://` or use custom schemes if the URL was attacker-controlled. While the URLs in this script currently target `https://en.wikipedia.org/...` explicitly, adhering to security best practices and suppressing false positives is important.

## Research Data
According to Python security best practices, using `urllib.request.urlopen` allows protocols like `file://` and `ftp://` which can lead to local file disclosure (SSRF/Path Traversal) if the URL is dynamically generated from user input.
- **SentinelOne CVE-2022-0391 Overview:** A flaw within the `urllib.parse` module allows for SSRF and injection attacks.
- **Mitigation:** Manually validate the URL scheme (e.g., ensure it starts with `http://` or `https://`) before passing it to `urlopen`.
- **Bandit Linter:** Even after adding validation, `bandit` will flag `urlopen`. The correct way to handle this in bandit is to add a `# nosec B310` comment on the specific line calling `urlopen` after implementing proper scheme validation.
- **Memory Rule Reference:** "When using URL open functions like `urllib.request.urlopen`, explicitly validate the URL scheme (e.g., ensuring it starts with `http://` or `https://`) to prevent B310 SSRF/Path Traversal vulnerabilities before appending `# nosec B310` to suppress Bandit warnings."

## Recommended Code Changes

Update `viking_girlfriend_skill/data/knowledge_reference/populate.py` to include URL scheme validation before `urllib.request.urlopen` is called, and add the `# nosec B310` comment.

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
                if not url.lower().startswith(('http://', 'https://')):
                    raise ValueError("URL scheme must be http or https")
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
                pages = data['query']['pages']
=======
        try:
            if not url.lower().startswith(('http://', 'https://')):
                raise ValueError("URL scheme must be http or https")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
                data = json.loads(response.read().decode())
                pages = data['query']['pages']
>>>>>>> REPLACE
```
