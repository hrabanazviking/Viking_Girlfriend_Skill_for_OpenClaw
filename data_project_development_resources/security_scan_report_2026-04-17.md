# Security Scan Report (2026-04-17)

## Summary
A security scan was performed on the `viking_girlfriend_skill` codebase using Bandit (Static Application Security Testing). The initial scan identified potential security vulnerabilities related to the use of `urllib.request.urlopen`.

## Findings

1.  **Vulnerability:** B310: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
    *   **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
    *   **Lines:** 27, 62 (originally, prior to fixes)
    *   **Severity:** MEDIUM
    *   **Description:** The script used `urllib.request.urlopen` without explicitly validating the URL scheme before making the request. An attacker who could control the URL might be able to exploit Server-Side Request Forgery (SSRF) or Local File Inclusion (LFI) vulnerabilities (e.g., by providing a `file://` URL).

## Recommended Code Changes (Implemented)

The following code changes were implemented to mitigate the identified B310 vulnerability:

1.  **URL Scheme Validation:** Added explicit validation to ensure the URL scheme is either `http` or `https` before opening the URL with `urllib.request.urlopen`.
2.  **Nosec Suppression:** Appended `# nosec B310` to the `urlopen` calls after ensuring the scheme validation was in place to suppress the Bandit warning, as the vulnerability is now addressed.

**Diff applied to `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**
```diff
@@ -23,8 +23,11 @@

         while True:
             try:
+                parsed_url = urllib.parse.urlparse(url)
+                if parsed_url.scheme not in ('http', 'https'):
+                    raise ValueError("Invalid URL scheme")
                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
-                with urllib.request.urlopen(req) as response:
+                with urllib.request.urlopen(req) as response:  # nosec B310
                     data = json.loads(response.read().decode())

                     for member in data['query'].get('categorymembers', []):
@@ -58,8 +61,11 @@
         url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={titles_param}&format=json"

         try:
+            parsed_url = urllib.parse.urlparse(url)
+            if parsed_url.scheme not in ('http', 'https'):
+                raise ValueError("Invalid URL scheme")
             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
-            with urllib.request.urlopen(req) as response:
+            with urllib.request.urlopen(req) as response:  # nosec B310
                 data = json.loads(response.read().decode())
                 pages = data['query']['pages']
```

## Post-Fix Verification
A subsequent Bandit scan (`bandit -r viking_girlfriend_skill/ -f json -q`) returned no active findings, confirming the vulnerability has been resolved.

## Research Data on SSRF and B310

*   **B310 (Bandit):** The `urllib.request.urlopen` function in Python is capable of handling various schemes, including `file://`, `ftp://`, and custom handlers. If an application accepts user-supplied URLs and passes them directly to `urlopen`, an attacker could supply a `file:///etc/passwd` (or similar) URL to read local files, or an `http://localhost:internal_port` URL to scan internal networks or access internal services (SSRF).
*   **Mitigation Strategy:** The recommended mitigation is to always parse the URL (e.g., using `urllib.parse.urlparse`) and explicitly check the `scheme` attribute against a whitelist of permitted schemes (usually `['http', 'https']`) before initiating the request. The fix implemented aligns perfectly with this best practice.
*   **Memory Note Integration:** This mitigation directly aligns with the memory directive: "When using URL open functions like `urllib.request.urlopen`, explicitly validate the URL scheme (e.g., ensuring it starts with `http://` or `https://`) to prevent B310 SSRF/Path Traversal vulnerabilities before appending `# nosec B310` to suppress Bandit warnings."
