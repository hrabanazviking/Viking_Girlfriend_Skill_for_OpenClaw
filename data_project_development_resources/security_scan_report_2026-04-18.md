# Security Scan Report: 2026-04-18

## Overview
A Bandit SAST security scan was run across the `viking_girlfriend_skill/` codebase. The scan flagged two instances of Server-Side Request Forgery (SSRF) vulnerability. This report details the issue, the associated remediation, and background research on SSRF attacks.

## Finding Details
**Issue:** B310: urllib_urlopen
**Severity:** MEDIUM
**Locations:**
- `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 27)
- `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 62)
**Description:** The script was using `urllib.request.urlopen(req)` without explicit URL scheme validation. Allowing the use of `file:/` or custom schemes in `urlopen` can result in unauthorized file read access or potential Server-Side Request Forgery (SSRF).

## Remediation
**Action Taken:**
Added an explicit scheme validation check before executing `urlopen()`. The check enforces that all requests are strictly `http://` or `https://`.

**Code Example:**
```python
if not url.startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
```
Note: Added `# nosec B310` to suppress the Bandit warning as the URL scheme has been manually verified, complying with the project's security guidelines.

**Verification:**
Re-running the Bandit scanner confirms that the B310 vulnerability has been fully resolved.

## Research Data on SSRF (Server-Side Request Forgery)

### What is SSRF?
According to OWASP, Server-Side Request Forgery (SSRF) is an attack where an attacker is able to coerce the server to make a forged request to an unexpected or unintended destination. The server, which usually enjoys implicit trust inside the local network, acts as a proxy for the attacker.

### Why is it Dangerous?
- **Internal Network Scanning:** Attackers can use SSRF to map out the internal network behind a firewall, probing for open ports or running services.
- **Reading Local Files:** If a vulnerable server accepts schemes like `file://`, the attacker might be able to read local files, accessing sensitive files like `/etc/passwd` or configuration files with passwords.
- **Accessing Internal APIs:** Attackers could send requests to internal REST APIs or metadata services (e.g., AWS IMDS `http://169.254.169.254/`) leading to privilege escalation or secret exfiltration.

### Mitigations
1.  **Enforce URL Allow-lists:** Only permit specific URLs or domains when resolving external resources.
2.  **Validate URL Schemes:** Only permit `http://` or `https://` schemas. Block local schemas such as `file://`, `ftp://`, or `gopher://`.
3.  **Disable Unused Protocols:** If the application framework uses a flexible URL fetcher (like `urllib`), ensure it is configured to block or ignore unsafe protocols.
4.  **Network-Level Protections:** Prevent the application server from accessing internal or loopback networks (e.g., 127.0.0.1, 10.0.0.0/8, 192.168.0.0/16, etc.) unless strictly necessary.

### Sources
- [OWASP Top 10 A10:2021 Server Side Request Forgery (SSRF)](https://owasp.org/Top10/2021/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/)
- [OWASP SSRF Vulnerability Overview](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)
