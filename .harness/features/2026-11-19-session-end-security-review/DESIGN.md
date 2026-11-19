# Session-end security review

## ROUTING

The session-end heading in the root instructions routes code and configuration changes to the validation index. The index keeps one entry for the existing code review and a second entry for security review. Code-only and mixed sessions match both entries. Configuration-only sessions match security review and any other situational checks. Documentation-only sessions load only applicable guidance checks. A change's role in running, building, or deploying the system determines whether it counts as configuration.

## REVIEW

Start with the session's changes and trace actors, privileges, assets and data across changed interfaces. For new or altered trust boundaries, make those relationships explicit. Generate plausible threats and identify controls with STRIDE, cross-check relevant OWASP Top 10 risks, and use specific ASVS requirements to define evidence for changed web controls. Validate effective settings, including deployment overrides. Use project-approved security tooling for applicable checks, then verify the public behavior of changed controls with local fixtures when feasible. Assess the likelihood and impact of findings, fix what is in scope and report gaps and remaining risk.

Reviewers can use code and configuration inspection when a check has no scanner or the scanner cannot reach the relevant behavior. Record tooling limitations and keep missing required evidence or unresolved material findings visible in the result.

## SCOPE

Keep trigger routing in the two index files. Use one focused ruleset with contextual sections to avoid loading security procedures during unrelated work. Scale work to the changed behavior and the consequences of failure. Reuse existing project tools and safe local tests. Retain enough path, behavior, and scope detail for the next reviewer without exposing sensitive material.

Verify local links and walk through all four session types. Use a synthetic configuration override to verify permitted and denied access, and use a separate mixed example to trace workflow rules with an unavailable scanner. The verification summary is in the [feature history](../../../docs/agents/feature-history.md#session-end-reviews).
