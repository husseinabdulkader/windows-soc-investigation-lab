# Next investigation: unexpected privileged group membership

Design brief for a planned extension. The detector, fixtures and tests are not implemented. Initial scope uses synthetic records and runs locally without a VM.

## Question

An account has been added to the local Administrators group. Was the change authorized, or could it provide unwanted privileged access?

Windows Security event **4732** records addition of a member to a security-enabled local group. Real collection requires Success auditing for **Audit Security Group Management**. Group scope matters: other event IDs describe additions to global or universal groups; do not treat them as interchangeable.

## Proposed synthetic scenario

Entirely invented scenario, not an actual Windows capture:

| Meaning | Example |
| --- | --- |
| Computer recording the event | LAB-PC01 |
| Event ID | 4732 |
| Actor requesting the change | LAB\helpdesk01 |
| Member being added | LAB\trainee01 |
| Group receiving the member | Administrators |

The actor, member and group are three different entities. In native event XML, `SubjectUserName` identifies the actor, `MemberSid` identifies the added member, and `TargetUserName` names the group. That last field does **not** mean the same thing as the authentication event's target account. `MemberName` can be missing (`-`); a real investigation may need SID resolution. The friendly member label in this scenario table is invented context, not a guaranteed native field value.

An addition is observable; whether it is expected requires separate approval/change evidence. A helpdesk-looking account name is not proof of authorization. A single unapproved privileged addition can justify review; the authentication rule's five-failure threshold does not apply here.

## Next implementation scope

Start with local Administrators membership only. Use stable group identifiers instead of trusting display names. Define a separate schema, positive and authorized cases, an unrelated group case, and missing-member/approval boundary cases. Match approval context to the exact actor, member, host, group and time window. Keep synthetic approval data separate from Windows telemetry. Add a report and meaningful tests before claiming the detector works.


Official references checked 2026-11-03: [event 4732](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4732), [Audit Security Group Management](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/audit-security-group-management). No live group change has been performed.
