# Security Policy

Lixvn takes the security and integrity of our open-source ecosystem, SDK runtime, and developer infrastructure seriously. We appreciate the contributions of security researchers and developers in identifying and safely reporting potential vulnerabilities.

---

## Supported Versions

Security fixes and patches are actively provided for the following versions:

| Version | Supported          | Security Status                       |
| :------ | :----------------- | :------------------------------------ |
| 0.4.x   | :white_check_mark: | Current active release & main branch |
| < 0.4.0 | :x:                | Unsupported                           |

---

## Reporting a Vulnerability

If you discover or suspect a security vulnerability or sensitive exposure in Lixvn, **please do not open a public GitHub issue, pull request, or discussion**.

Instead, report all security issues confidentially to:

- **Security Team Email**: [security@lixvn.dev](mailto:security@lixvn.dev)

### What to Include

To facilitate rapid triage and reproduction, please provide:

1. **Description**: A clear summary of the issue and potential impact.
2. **Affected Components**: File paths, functions, API endpoints, or configurations affected.
3. **Reproduction Steps**: Step-by-step instructions or minimal proof-of-concept (PoC) code demonstrating the vulnerability.
4. **Environment**: Operating system, Python version, runtime dependencies, or deployment context.
5. **Mitigation Suggestions**: Any initial ideas or proposed patches (if available).

If you wish to encrypt your submission using PGP/GPG, please indicate this in an initial message or request our public key via `security@lixvn.dev`.

---

## Response Timeline & Service Level Agreement (SLA)

Our security response team commits to the following timelines:

- **Initial Acknowledgment**: Within **24 hours** of receiving your report.
- **Triage & Severity Assessment**: Within **72 hours**, confirming reproducibility and assigning a CVSS severity score.
- **Remediation Updates**: Regular progress updates every **3 to 5 business days** while a fix is being engineered and tested.
- **Coordinated Release & Advisory**: Within **14 to 30 days** of initial triage, depending on complexity and severity, published alongside a security advisory and attribution.

---

## Safe Harbor & Responsible Disclosure

We fully support responsible security research and adhere to safe harbor principles. If you conduct vulnerability research in good faith:

- We will **not** pursue legal action or refer your activity to law enforcement.
- We will work collaboratively with you to validate, patch, and publicly credit your discovery.
- We request that you provide reasonable time for remediation prior to public disclosure.

### Research Guidelines
- Avoid testing techniques that degrade service availability (e.g., Denial of Service, brute force).
- Avoid accessing, modifying, or destroying user or third-party data.
- Never deploy destructive exploits in live environments.

---

## Scope

### In-Scope
- Lixvn core runtime library and SDK entry points.
- Official documentation, configuration templates, and repository workflows (`lixvn123/lixvn`).
- Live production web properties (`https://lixvn.dev`).

### Out-of-Scope
- Volumetric Denial of Service (DoS/DDoS) attacks.
- Social engineering, phishing, or physical attacks targeting contributors.
- Vulnerabilities solely present in unmaintained third-party dependencies without demonstration of practical exploitability within Lixvn.
