# Platform boundaries and optional extensions

Current route: offline synthetic CSV and Python, zero cloud cost. No tenant, agent, licence purchase, Azure resource, cloud upload or trial has been created. The KQL file is an illustrative reference; it requires no ingested tenant data but still needs an authorized Kusto-compatible execution surface to run. None was used here.

## Schemas are different

| Meaning | Windows Security XML | Sentinel `SecurityEvent` | Defender `DeviceLogonEvents` |
| --- | --- | --- | --- |
| Time | `TimeCreated/@SystemTime` | `TimeGenerated` | `Timestamp` |
| Event category | `EventID` (4624 / 4625) | `EventID` | `ActionType`; inspect supported values in portal |
| Destination | `Computer` | `Computer` | `DeviceName`, plus service `DeviceId` |
| Target account | `TargetUserName`, `TargetDomainName` | `TargetUserName`, `TargetDomainName` where populated | `AccountName`, `AccountDomain` |
| Source IP | `IpAddress` | `IpAddress` where populated | `RemoteIP` |
| Logon type | numeric event data | `LogonType` (int) | `LogonType` (string categories) |

This is a conceptual mapping, not a tested conversion. Missing fields and event versions matter. Defender does not expose native EventID as a substitute for ActionType in this table. Do not copy a `SecurityEvent` filter into a Defender query and assume equivalence. A shared portal or query language does not make schemas identical.

The local CSV's `record_id` and `synthetic` are project fields. The example KQL defines its own table rather than pretending the CSV is a native connector schema. Its expected three alerts are inferred from fixture inspection, **not an observed KQL result**. It omits intervening-success reset and must be revised and compared against Python fixtures before any operational reuse.

Sources checked 2026-11-03: [SecurityEvent schema](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/securityevent), [DeviceLogonEvents schema](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicelogonevents-table), [datatable syntax](https://learn.microsoft.com/en-us/kusto/query/datatable-operator?view=microsoft-fabric).

## Sentinel: prerequisites, not deployment instructions

- Access/licensing: an authorized Azure subscription and a Log Analytics workspace with Sentinel enabled. This is a billable Azure service; a student account or trial is not assumed.
- Permissions: read/write access to the target workspace and rights to create the required collection rules and manage the target machines/agents. Scope roles for the task; Sentinel Contributor can manage Sentinel resources, but does not by itself guarantee every Azure/Arc deployment permission. Query-only reviewers should receive appropriate read access rather than subscription-wide administration.
- Telemetry: eligible Windows machines, effective audit policy, the Windows Security Events via AMA connector, Azure Monitor Agent and data collection rules selecting the needed events. Non-Azure machines need Azure Arc under the documented connector prerequisites. Check supported OS versions before onboarding an existing guest. The connector writes to `SecurityEvent`; Windows Forwarded Events uses a different table (`WindowsEvent`).
- Cost: ingestion volume, retention/tier, any compute/storage and automation can incur charges. Free allowances are conditional. Estimate for the actual region/subscription and obtain explicit budget approval before creating resources. Budget alerts are not a guaranteed hard spending cap. Zero budget means leave this extension unprovisioned.

References: [Windows connector setup](https://learn.microsoft.com/en-us/azure/sentinel/connect-services-windows-based), [connector inventory](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference), [roles](https://learn.microsoft.com/en-us/azure/sentinel/roles), [current pricing](https://www.microsoft.com/en-us/security/pricing/microsoft-sentinel/).

## Defender XDR: prerequisites, not deployment instructions

- Licensing: verify a qualifying subscription and the specific endpoint hunting entitlement, for example an appropriate Defender for Endpoint Plan 2 entitlement. General portal access from a Microsoft 365 licence does not guarantee every product's telemetry or feature.
- Permissions: authorized tenant administration for initial enablement; Microsoft documents Security Administrator as the minimum for turning on Defender. Give the analyst read access to the relevant endpoint data and device groups under the tenant's active RBAC model. Do not assume tenant membership gives hunting access.
- Telemetry: deploy/onboard the supported endpoint service and verify sensor health. `DeviceLogonEvents` is populated by Defender for Endpoint; ordinary Windows antivirus installation or a CSV file alone does not populate it. Confirm actual ActionType values and sample fields in the portal before porting a rule.
- Cost: existing entitlement might cover access; otherwise a licence/trial is needed. No trial, licence or paid service is assumed or activated. A licence does not remove separate Sentinel ingestion costs if forwarding data.

References: [Defender prerequisites](https://learn.microsoft.com/en-us/defender-xdr/prerequisites), [hunting access](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-overview), [endpoint table source](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicelogonevents-table).

## Evidence needed before claiming a live integration

Record sanitized telemetry samples, actual table/schema, connector/agent configuration, least-privilege role scope, query text and execution date, positive/benign/boundary results, and limitations. Distinguish a query returning rows from a scheduled detection creating an alert. Store only sanitized evidence; do not fabricate screenshots or claim deployment from an illustrative query.
