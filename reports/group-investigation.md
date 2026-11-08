# GROUP-001 investigation: unexplained privileged addition

Analysis date: 2026-11-08. Case LAB-GROUP-001. All evidence is synthetic; no response action was performed.

## Evidence and timeline

At 2026-01-16 09:00:00 UTC, G01 records event 4732 on LAB-PC01. LAB\helpdesk01 (SID ending 1001) adds LAB\trainee01 (SID ending 1101) to built-in Administrators, SID S-1-5-32-544. The supplied approvals cover different members and later windows. Neither matches G01.

Sources: [events](../data/group-events.json), [approvals](../data/group-approvals.json), [rule](../docs/group-changes.md), [output](group-results.json). Friendly account names are synthetic context, not evidence of authorization.

## Hypotheses and missing evidence

Result: `unexplained_change`, reason `no_matching_approval`. This establishes no match in the supplied snapshot; it does not establish absence of approval everywhere.

Possible explanations include an undocumented emergency change, a mistaken addition, an incomplete approval export, or unauthorized use of the actor account. Check authoritative change records for the exact identities/host/group/time, confirm the administrator's activity through a trusted channel, establish business need, and inspect the member's subsequent actions. Account names alone do not determine intent.

## Severity and response

Medium initial triage priority: the addition grants privileged membership, but intent and impact are unknown. Escalate if account compromise, unauthorized activity or sensitive-host exposure is established. Preserve original logs and validate collection completeness before disruptive changes.

If authorization is established, document the matching evidence and reconcile the approval record. If the addition is unauthorized, recommend removing inappropriate membership under the incident process, assessing sessions/credentials and investigating actions taken while privileged. These are recommendations, not actions executed by the utility.

## Comparison cases and lessons

G02 is expected because CHG-001 matches. G08 shows that the same member and host are insufficient when the actor differs. G04/G05 are included at both exact boundaries; G06 is unexplained one second later. G07 preserves incomplete identity evidence. G03 is outside privileged-group scope.

Use stable identifiers, keep authorization context separate from telemetry, and retain incomplete evidence. Approval expiry does not establish removal of existing privileges. Original Windows telemetry, trustworthy authorization records and post-change activity remain necessary for a full incident verdict.

## Verification

On 2026-11-08, 36 local tests passed: 21 authentication tests and 15 group-rule tests. CLI validation accepted 8 synthetic events and 2 approvals. Results: 3 expected, 3 unexplained, 1 insufficient-evidence and 1 out-of-scope. Tests cover correlation keys, inclusive boundaries, names versus SIDs, malformed input, missing identities, overlapping and retrospective/revoked approvals, ordering and CLI errors. The [GitHub Actions run](https://github.com/husseinabdulkader/windows-soc-investigation-lab/actions/runs/42459814460) passed for commit `76b59fe29668f96905864a62b99c9701be335da2` on Ubuntu with Python 3.14, including all 36 tests and both dataset validation steps. Live Windows collection and KQL remain unverified.
