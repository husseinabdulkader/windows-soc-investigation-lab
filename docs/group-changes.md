# GROUP-001: local Administrators additions

Implemented in `group_changes.py`, using synthetic event and approval JSON arrays. No account or group is modified. No live Windows or KQL execution is claimed.

## Run

```text
python group_changes.py data/group-events.json data/group-approvals.json
python group_changes.py data/group-events.json data/group-approvals.json --validate-only
python -m unittest discover -s tests -v
```

Expected: 8 events and 2 approvals; 3 expected changes, 3 unexplained changes, 1 insufficient-evidence result and 1 out-of-scope result. Every event is retained with its evidence ID. See [investigation](../reports/group-investigation.md) and [output](../reports/group-results.json).

## Rule

Validate both files completely before analysis. Invalid input fails with exit code 2, rather than becoming missing approval. Select event 4732 and group SID `S-1-5-32-544` (built-in Administrators); display names do not determine group identity. The threshold is one addition, not the authentication detector's five failures.

Match computer, actor SID, member SID and group SID to the approval. Computer names are case-insensitive. Require status `approved`, approval recorded no later than the event, and event time within the inclusive `valid_from` to `valid_until` interval. There is no grace period.

| Condition | Disposition |
| --- | --- |
| Exactly one matching approval | expected_change, with approval ID |
| No matching approval | unexplained_change |
| Multiple matching approvals | review_required, with all matching IDs |
| Missing group SID on 4732, or missing computer/actor/member on selected addition | insufficient_evidence |
| Other event or non-Administrators group | out_of_scope |

An expected change means the supplied approval snapshot contains a match, not that the approval's authenticity or business need has been independently verified. Missing approval is not proof of an attack. A valid approval may cover multiple matching additions in its interval; one-time use is not enforced. The window governs when an addition is expected, not when membership must be removed.

## Schemas

UTF-8 JSON arrays, with exact field sets. All records require boolean `synthetic: true`; every other field is a nonempty trimmed string. IDs must be unique within each file. Empty arrays are allowed. Timestamps use whole-second UTC `YYYY-MM-DDTHH:MM:SSZ`. SID validation checks shape and numeric ranges, not directory existence. All identities, hosts, dates and approvals are invented.

### Events: data/group-events.json

| Field | Meaning / source |
| --- | --- |
| synthetic | Project provenance flag |
| record_id | Unique synthetic evidence label; not native EventRecordID |
| timestamp | Event time, corresponding to System/TimeCreated |
| event_id | Accepts 4732, 4733, 4728, 4756; only 4732 is selected |
| computer | Destination recording event, System/Computer |
| actor_sid | SubjectUserSid: account requesting addition |
| actor_name | Synthetic display label for subject domain/account |
| member_sid | MemberSid: principal added |
| member_name | Synthetic resolved display label |
| group_sid | TargetSid: receiving group |
| group_name | TargetUserName: group display name |

Missing computer/SIDs/names may be represented by `-`. Missing names alone do not prevent matching by SID. In event 4732, TargetUserName identifies the **group**, unlike the target account in authentication events. Native MemberName may be `-` or a distinguished name; friendly member names in this fixture are synthetic enrichment. The actor account does not conclusively identify a human operator.

### Approvals: data/group-approvals.json

| Field | Meaning |
| --- | --- |
| synthetic | Project provenance flag |
| approval_id | Unique synthetic change reference |
| computer, actor_sid, member_sid, group_sid | Exact authorized scope; missing values forbidden |
| status | approved, revoked or rejected; only approved matches |
| approved_at | Approval record time; retrospective approval cannot match an earlier event |
| valid_from, valid_until | Inclusive permitted addition interval; start must not exceed end |

Approval fields are external change-management context, not Windows telemetry. This static snapshot does not model revocation timing, historical versions, approver authority or approval-system integrity. A revoked record never matches, even for an earlier event.

## Scenario manifest

| Record | Case | Expected result |
| --- | --- | --- |
| G01 | helpdesk01 adds trainee01; no approval matches | unexplained_change |
| G02 | Exact match to CHG-001 | expected_change |
| G03 | Addition to Users, SID ending 545 | out_of_scope |
| G04 | Exact start of CHG-002, 11:00:00Z | expected_change |
| G05 | Exact end of CHG-002, 11:30:00Z | expected_change |
| G06 | One second after CHG-002 expiry | unexplained_change |
| G07 | Administrators addition with missing member SID | insufficient_evidence |
| G08 | CHG-001 member/host/group, different actor | unexplained_change |

## Prerequisites and limitations

Real collection requires Success auditing under Audit Security Group Management, access to the Security log and adequate retention. Inspect effective policy on the destination. No live collection or EVTX adapter was implemented; do not label real exports synthetic to bypass validation.

Missing, delayed or mis-scoped approval records, emergency changes and clock discrepancies can cause unexplained results. Confirm authoritative records before inferring intent. Do not suppress all helpdesk actors or select privileged groups by display name. Any timing tolerance should be explicit and tested; the current interval is exact.

Scope this version to direct built-in Administrators additions on workstations/member servers. Host role is not discovered automatically. Domain-controller groups, nested memberships, other privileged groups, overdue removals and post-change activity require separate analysis. The fixture cannot establish production accuracy. No GROUP-001 KQL query is supplied; local fields are not Sentinel or Defender table schemas.

Official references reviewed 2026-11-08: [4732](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4732), [security identifiers](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers), [audit policy](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/audit-security-group-management).
