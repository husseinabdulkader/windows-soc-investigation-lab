# Skills mapping and interview preparation

Both certifications are planned, not earned. This lab provides narrow practice, not full exam coverage, readiness evidence or enterprise experience.

## Objective mapping checked 2026-11-03

Security+ mapping is explicitly to **SY0-701, official objectives document version 6.0**, which was accessible. The current V7/V8 product pages could not be fetched during verification; this document does not assert that version 6.0 is the latest revision or select an exam for the learner. Recheck CompTIA's current exam page and downloadable blueprint before booking or making a study schedule.

| Objective | Project evidence | Limit |
| --- | --- | --- |
| Security+ SY0-701 4.7: operations automation | Python validation/detection and regression tests | No orchestration or automated containment |
| Security+ SY0-701 4.8: incident response | Hypotheses, triage rationale and response recommendations | Synthetic tabletop analysis; no live incident |
| Security+ SY0-701 4.9: investigative data sources | Authentication records and evidence-linked timeline | Reduced schema; no forensic acquisition |
| SC-200: choose appropriate hunting tables | Schema comparison and illustrative KQL | No tenant query execution |
| SC-200: investigate evidence and entities | Account/host/source correlation and report | Concept practice, not Defender device investigation |
| SC-200: Windows Security event collection | Audit policy and connector prerequisites documented | Collection/AMA/WEF not configured |

Sources: [CompTIA official SY0-701 objectives v6.0](https://comptiacdn.azureedge.net/webcontent/docs/default-source/exam-objectives/comptia-security-sy0-701-exam-objectives-%286-0%29.pdf?sfvrsn=204179cc_6); [SC-200 official guide, skills effective October 21, 2026](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/sc-200). These mappings are interpretations of relevant subsets, not endorsements or certification equivalences.

Your existing AD account/permissions work helps explain identity context and troubleshooting hypotheses. Microsoft 365 support provides operational context but is not evidence of Defender XDR expertise. Your testing background is relevant to positive, negative and boundary tests. Prior OT scanning and Nmap familiarity are not claimed as activities performed by this repository.

## Two truthful draft CV bullets

Use these only if you can reproduce and explain the supplied implementation. The implementation and tests were created and run with AI assistance. You subsequently reported completing the guided reproduction and boundary exercise; this is distinct from independent authorship. These drafts describe the assisted project and do not claim a deployed SOC capability.

- Developed an AI-assisted Windows authentication investigation lab with a Python detector, 32 explicitly synthetic records and 21 passing local tests covering correlation, validation and timing boundaries.
- Documented evidence-linked authentication timelines, competing hypotheses, false-positive cases and proportionate response recommendations, with clear limits on unvalidated KQL and cloud integrations.

Do not add claims about prevented attacks, reduced incident response time, production accuracy, certifications, employer systems or deployed Sentinel/Defender services.

## Five interview questions

1. Why do you match domain, account, destination, source IP and logon type, and what attacks could that matching miss?
2. Walk through P01–P06 and E01–E06. How do the two five-minute windows differ from one ten-minute count or fixed time bins?
3. Why does A06 still trigger, and what independent evidence would justify closing a similar real alert as benign?
4. What happens with duplicate rows, out-of-order timestamps, missing IPs and an intervening successful logon? Which tests demonstrate those choices?
5. What would have to change before using this detector with Sentinel or Defender XDR, and which parts of this project have never been verified there?

Strong answers refer to code and evidence, acknowledge blind spots, and separate a successful authentication from proof of compromise. Start by answering in your own words; do not memorize the report.
