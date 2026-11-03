# AUTH-001 investigation: synthetic authentication sequence

Case: LAB-AUTH-001. Analysis date: 2026-11-03. Evidence dates: 2026-01-15 UTC. Status: offline lab analysis completed; real-world disposition cannot be established from this synthetic subset. No containment action performed.

## Question and evidence

Did repeated failures for `LAB\analyst01` followed by success justify investigation? Yes, the sequence meets the lab rule; it does not establish who controlled the account.

Evidence consists of `data/authentication.csv`, the schema/manifest, `analyze.py` and reproduced JSON in `expected-alerts.json`. These are generated lab artifacts, not collected forensic evidence. File hashes and command output are recorded separately in `verification.md`. Hashes identify this artifact version; they do not prove the events actually happened.

## Timeline

| UTC time | Evidence ID | Observation |
| --- | --- | --- |
| 09:00 | P01 | Failed network logon for LAB\analyst01 |
| 09:01 | P02 | Same account, host, source and logon type; failure |
| 09:02 | P03 | Same correlation key; failure |
| 09:03 | P04 | Same correlation key; failure |
| 09:04 | P05 | Fifth failure; burst spans four minutes |
| 09:05 | P06 | Success on LAB-FS01 from 192.0.2.10, one minute after last failure |

Result: five counted failures, one qualifying success. Failure reasons, authentication package, account privilege, accessed resource and post-logon actions are absent. A source IP is a correlation attribute, not proof of a person's identity.

## Competing hypotheses

| Hypothesis | Supporting observation | Evidence needed to decide |
| --- | --- | --- |
| Password guessing followed by access | Repeated failures followed by success | Source ownership, account-owner confirmation, status codes, endpoint activity and resource access |
| User corrected a password mistake | Same account and source throughout | Independent user confirmation and expected activity/time/location |
| Stored credentials or support troubleshooting | Repeated retries can precede repair | Authorized change/support record, scheduled task or service configuration and process evidence |
| Incomplete or misleading telemetry | Dataset contains only a selected field subset | Raw XML, logging health, collection gaps and surrounding events |

No hypothesis is proven. The input lacks enough evidence to distinguish a malicious actor from legitimate troubleshooting.

## Severity and response decision

Use **medium triage priority**, with low confidence in malicious intent: successful authentication after repeated failure deserves review, but neither privilege nor impact is known. This is an qualitative triage assessment, not a measured business risk score.

First preserve the relevant original logs and confirm clocks, host identity, account type and audit coverage. In a real authorized investigation, verify the account owner's activity through a trusted channel and review the source endpoint plus subsequent resource access. Do not disable an account solely because AUTH-001 triggered.

If independent evidence establishes unauthorized access, recommend containment appropriate to the affected system: isolate the source host where justified, restrict the affected account, reset exposed credentials, address active sessions and investigate scope. Seek the required incident-response authority before disruptive changes. Escalate urgency if privileged access, lateral movement or harmful actions are confirmed. These are recommendations only; none was executed.

If authorized troubleshooting is confirmed, document the evidence, repair the credential issue and close with a reason. Any suppression should be specific and time-limited.

## Controls and comparison cases

The A sequence produces the same kind of alert, but the synthetic manifest stipulates authorized troubleshooting. In a real case that assertion would need a verified support record; here it demonstrates that the same pattern can have benign intent. B and N do not meet the failure threshold. E triggers at both exact time boundaries. L misses the success window by one second. Non-alerting cases are not automatically safe; they simply do not satisfy this rule.

## Lessons learned

Separate an observation from its interpretation. Match the target account, not the account reporting the event. Preserve domain and destination to avoid mixing identities. Test time boundaries, not just a happy path. Record missing evidence explicitly. Do not report production detection rates from a tiny synthetic fixture.
