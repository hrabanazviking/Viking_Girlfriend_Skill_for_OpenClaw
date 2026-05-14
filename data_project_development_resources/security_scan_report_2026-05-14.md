# Security Scan Report: 2026-05-14

## Overview
A static application security testing (SAST) scan was performed using Bandit. The scan identified two `MEDIUM` severity issues related to URL opening functions.

## Findings

### 1. Bandit B310: SSRF / Path Traversal via `urllib.request.urlopen`
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Lines**: 27, 62
- **Description**: The `urllib.request.urlopen` function is being called without explicitly validating the URL scheme. By default, `urllib` permits not only `http://` and `https://` schemes, but also `file://` and custom schemes. If an attacker can manipulate the URL being fetched, they could potentially read arbitrary local files from the executing machine (Local File Inclusion / Path Traversal) or conduct Server-Side Request Forgery (SSRF) attacks against internal services.

## Research & Documentation
- **Bandit B310 Documentation**: https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html#b310-urllib-urlopen
- **Vulnerability Mechanism**: `urllib` does not inherently restrict the schemes it processes. When passed an untrusted or insufficiently validated URL, it may resolve a `file://` scheme, leading to local file exposure.
- **Remediation Strategy**: The application must explicitly validate that the URL scheme is strictly limited to permitted protocols (e.g., `http` and `https`) before initiating the request. Once this validation is in place, the Bandit warning can be safely suppressed using the `# nosec B310` comment.

## Recommended Code Changes

To resolve these vulnerabilities, implement URL scheme validation prior to calling `urlopen`.

**File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`

**Change 1 (around line 27):**
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
                    raise ValueError(f"Invalid URL scheme: {url}")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

**Change 2 (around line 62):**
```python
<<<<<<< SEARCH
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
=======
        try:
            if not url.lower().startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL scheme: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
                data = json.loads(response.read().decode())
>>>>>>> REPLACE
```
