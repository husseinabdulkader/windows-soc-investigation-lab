# Security objectives mapping

This mapping relates project components to selected Security+ and SC-200 objectives. It is not a claim of certification or full exam coverage.

## Objective mapping checked 2026-11-03

Security+ mapping is explicitly to **SY0-701, official objectives document version 6.0**, which was accessible. The current V7/V8 product pages could not be fetched during verification; this document does not assert that version 6.0 is the latest revision or establish current exam availability. Recheck CompTIA's current exam page and downloadable blueprint before using this mapping for exam preparation.

| Objective | Project evidence | Limit |
| --- | --- | --- |
| Security+ SY0-701 4.7: operations automation | Python validation/detection and regression tests | No orchestration or automated containment |
| Security+ SY0-701 4.8: incident response | Hypotheses, triage rationale and response recommendations | Synthetic tabletop analysis; no live incident |
| Security+ SY0-701 4.9: investigative data sources | Authentication records and evidence-linked timeline | Reduced schema; no forensic acquisition |
| SC-200: choose appropriate hunting tables | Schema comparison and illustrative KQL | No tenant query execution |
| SC-200: investigate evidence and entities | Account/host/source correlation and report | Concept practice, not Defender device investigation |
| SC-200: Windows Security event collection | Audit policy and connector prerequisites documented | Collection/AMA/WEF not configured |

Sources: [CompTIA official SY0-701 objectives v6.0](https://comptiacdn.azureedge.net/webcontent/docs/default-source/exam-objectives/comptia-security-sy0-701-exam-objectives-%286-0%29.pdf?sfvrsn=204179cc_6); [SC-200 official guide, skills effective October 21, 2026](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-200). These mappings are interpretations of relevant subsets, not endorsements or certification equivalences.
