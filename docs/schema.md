# Data contract and synthetic scenarios

`data/authentication.csv` is UTF-8 CSV, schema version 1. It is a reduced teaching model inspired by Windows Security events, **not Windows CSV export format**, a Sentinel table, or a Defender hunting table. All identities, hosts, addresses, timestamps, events and scenario context are invented. `192.0.2.0/24` addresses are used as example identifiers, not reachable lab targets.

Header order is enforced. Values must not contain surrounding whitespace. All rows must pass validation before detection begins.

| Local field | Type / rule | Windows XML counterpart or provenance |
| --- | --- | --- |
| synthetic | literal `true` | Lab provenance flag, no Windows equivalent |
| record_id | nonempty globally unique string | Lab evidence label; not a native EventRecordID |
| timestamp | ISO datetime with UTC `Z` suffix | `System/TimeCreated/@SystemTime` |
| event_id | `4624` or `4625` | `System/EventID` |
| computer | nonempty string, not `-` | `System/Computer`, destination generating the event |
| target_domain | nonempty string, not `-` | `EventData/TargetDomainName` |
| target_user | nonempty string, not `-` | `EventData/TargetUserName`, not SubjectUserName |
| source_ip | canonical IPv4/IPv6 text or `-` | `EventData/IpAddress`; `-` means unavailable |
| logon_type | integer text from documented supported list in code | `EventData/LogonType`; this detector uses only `3` |

Times are compared in UTC. File order is irrelevant. Names are compared case-insensitively; the output retains input spelling. IPv6 must use canonical spelling to avoid multiple strings representing one address. The validator accepts known non-network logon types so tests can demonstrate the detector's scope. Unknown types fail validation rather than being guessed.

In real evidence, preserve provider, channel, event version, original XML, status/substatus and original record ID. Real EventRecordID values are not globally unique across computers/channels/log resets. A later adapter must establish an evidence identity from source context and keep a provenance mapping. Current synthetic record IDs do not claim to model that behaviour.

## Scenario manifest

All events occur on 2026-01-15 UTC, on `LAB-FS01`, in domain `LAB`, with logon type 3. Each scenario uses a distinct account and IP.

| IDs | Invented scenario | Expected result |
| --- | --- | --- |
| P01–P06 | Five failures 09:00–09:04, success 09:05; cause unknown | Alert P06 |
| B01–B03 | Two mistyped attempts, then success 10:02 | No alert |
| A01–A06 | Authorized credential troubleshooting, five failures then success 11:05 | Alert A06; benign context is not visible to code |
| E01–E06 | Five failures spanning exactly 12:00–12:05, success 12:10 | Alert E06; both boundaries inclusive |
| N01–N05 | Four failures, then success 13:04 | No alert; below count threshold |
| L01–L06 | Five failures ending 14:04; success 14:09:01 | No alert; one second beyond success window |

The scenario descriptions are author-supplied ground truth for teaching. They are not independent evidence or real support tickets. Additional malformed and correlation cases are constructed by the tests.

Official field references: [4624](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624), [4625](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4625). Checked 2026-11-03. Fields vary by event/version; this subset deliberately omits context required for a real compromise verdict.
