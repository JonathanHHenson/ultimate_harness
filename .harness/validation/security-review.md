# Session-End Security Review

## When starting the security review

- Review the session's changes, including new and deleted files, and follow their effects into any unchanged callers, controls, or deployment settings they rely on. Use the diff and untracked files, or the session's change list when Git is unavailable.
- Identify the affected assets, actors, privileges, and entry points. For new or changed trust boundaries, sketch who sends what to which processes or stores, where trust changes, and what enforces it. Scale the review to exposure and impact. [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)

## When reviewing affected behavior

- Use STRIDE to ask what could go wrong in the changed flows and controls. Consider spoofing, tampering, repudiation, information disclosure, denial of service, and elevation of privilege. For plausible threats, identify who can trigger them, the impact, and the control. Check relevant workflow rules for valid actions used out of order, repeatedly, or concurrently. [Microsoft STRIDE threat categories](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- Cross-check relevant web risks with OWASP Top 10. Consider access control and authentication, input handling, secure design and configuration, dependency and data integrity, cryptography, logging, and failure paths. For changed web controls, use applicable ASVS requirements to define what evidence to collect. [OWASP Top 10:2025](https://top10.owasp.org/), [OWASP ASVS](https://asvs.owasp.org/)

## When reviewing configuration, dependency, or build changes

- Trace effective settings through defaults, environment-specific overrides, and their precedence. Check that access and network exposure match intent, privileges are limited, and missing or invalid settings cannot grant unintended access. Check how credentials are supplied, used, and logged.
- For changed dependencies or build inputs, verify their source, how versions resolve, and what permissions code runs with. Check whether untrusted inputs can influence privileged CI or deployment steps.

## When verifying changed controls

- Run applicable project-configured security checks within the approved scope, such as source, dependency, secret, or infrastructure scanning. Confirm their coverage, review findings in context, and manually inspect affected behavior and settings the tools cannot assess.
- Verify changed controls through existing tests or targeted local checks. Where applicable, cover permitted and denied requests, cross-role or cross-project access, and missing or overridden settings. Check that denied actions leave protected data and state intact. Use isolated fixtures and synthetic data.

## Before reporting the security review complete

- Fix actionable findings within scope and rerun affected checks. Report unresolved findings with location, severity, conditions, impact, and suggested remediation. State what you verified, what you could not verify, and why. Keep secrets and sensitive data out of review output.
- Report the review as incomplete if required evidence is missing or a material finding is unresolved. Record the review outcome and supporting evidence in the feature record when applicable.
