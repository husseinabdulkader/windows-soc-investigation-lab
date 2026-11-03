# Next investigation: unexpected privileged group membership

Status: learning brief only; detector, fixtures and tests are not implemented yet. This remains part of windows-soc-investigation-lab, rather than a separate unrelated repository. No powerful PC or VM is needed for the synthetic first version.

## Question

An account has been added to the local Administrators group. Was the change authorized, or could it provide unwanted privileged access?

Windows Security event **4732** records addition of a member to a security-enabled local group. Real collection requires Success auditing for **Audit Security Group Management**. Group scope matters: other event IDs describe additions to global or universal groups; do not treat them as interchangeable.

## First teaching example

Entirely invented scenario, not an actual Windows capture:

| Meaning | Example |
| --- | --- |
| Computer recording the event | LAB-PC01 |
| Event ID | 4732 |
| Actor requesting the change | LAB\helpdesk01 |
| Member being added | LAB\trainee01 |
| Group receiving the member | Administrators |

The actor, member and group are three different entities. In native event XML, `SubjectUserName` identifies the actor, `MemberSid` identifies the added member, and `TargetUserName` names the group. That last field does **not** mean the same thing as the authentication event's target account. `MemberName` can be missing (`-`); a real investigation may need SID resolution. The friendly member label in this teaching table is invented context, not a guaranteed native field value.

An addition is observable; whether it is expected requires separate approval/change evidence. A helpdesk-looking account name is not proof of authorization. A single unapproved privileged addition can justify review; the authentication rule's five-failure threshold does not apply here.

## Next implementation scope

Start with local Administrators membership only. Use stable group identifiers instead of trusting display names. Define a separate schema, positive and authorized cases, an unrelated group case, and missing-member/approval boundary cases. Match approval context to the exact actor, member, host, group and time window. Keep synthetic approval data separate from Windows telemetry. Add a report and meaningful tests before claiming the detector works.

First exercise: identify who requested the change and who received membership in the example above. Then name the authorization evidence you would seek before calling it malicious.

Official references checked 2026-11-03: [event 4732](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4732), [Audit Security Group Management](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/audit-security-group-management). No live group change has been performed.
