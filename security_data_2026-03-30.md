# Security Analysis: B310 Vulnerability in `urllib.request.urlopen`
**Date:** 2026-03-30

## Overview
A Bandit security scan of the `viking_girlfriend_skill/` directory identified two MEDIUM severity issues related to the use of `urllib.request.urlopen()`.

### Vulnerability Details
- **Bandit ID:** B310 (`urllib_urlopen`)
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') / Local File Inclusion)
- **Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27, 62)

### Description
The Python standard library function `urllib.request.urlopen()` supports multiple URL schemes, including `http://`, `https://`, `ftp://`, and critically, `file://`. When URLs are constructed from untrusted or external input and passed to `urlopen()`, an attacker can potentially manipulate the URL to use the `file://` scheme.

This leads to two primary risks:
1. **Local File Inclusion (LFI):** An attacker can read local files on the server (e.g., `file:///etc/passwd` or `file:///path/to/secrets.json`).
2. **Server-Side Request Forgery (SSRF):** The application can be coerced into making requests to internal network resources that are otherwise inaccessible from the outside.

While the script `populate.py` hardcodes the base URL to `https://en.wikipedia.org/w/api.php`, the use of `urlopen` is inherently risky, and it's best practice to secure it against potential future refactoring where URLs might become user-controlled.

## Recommendations
To mitigate this vulnerability, it is highly recommended to validate the scheme of the URL before passing it to `urlopen`, or to migrate to a safer HTTP client library like `requests`. The `requests` library does not support the `file://` scheme by default, providing an implicit layer of defense against LFI attacks.

### Recommended Code Changes
#### Option 1: URL Scheme Validation (Minimal Change)
If continuing to use `urllib`, explicitly validate that the URL starts with a permitted scheme before calling `urlopen()`.

```python
import urllib.request
import urllib.parse
import json

url = f"https://en.wikipedia.org/w/api.php?..."

# Validate scheme
if not url.lower().startswith(('http://', 'https://')):
    raise ValueError(f"Unsupported URL scheme in: {url}")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

#### Option 2: Migrate to the `requests` library (Preferred)
The `requests` library is the standard for making HTTP requests in Python. It is safer by default as it does not handle the `file://` scheme.

First, ensure `requests` is in `requirements.txt`. Then, refactor the code:

```python
import requests
import json
import time

# ...

def fetch_category_members(category, max_results=5000):
    # ...
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{category}&cmlimit=500&format=json"

        while True:
            try:
                headers = {'User-Agent': 'SigridKnowledgeBuilder/1.0'}
                response = requests.get(url, headers=headers)
                response.raise_for_status() # Raise exception for bad status codes
                data = response.json()

                # ...

                if 'continue' in data:
                    cont_token = data['continue']['cmcontinue']
                    url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{category}&cmlimit=500&cmcontinue={cont_token}&format=json"
                else:
                    break
            except Exception as e:
                print(f"Error fetching category {current_cat}: {e}")
                break
            time.sleep(0.1)
    # ...
```

Applying one of these recommendations will resolve the B310 Bandit warnings and improve the overall security posture of the application.
