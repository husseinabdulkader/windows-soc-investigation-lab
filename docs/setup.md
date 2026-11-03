# Setup, personal exercises and cleanup

## First session: offline, no VM required

Use the README quick-start commands in the folder containing `analyze.py`. No package installation or virtual environment is needed because this uses only Python's standard library. Do not run commands as administrator for the offline utility.

1. Validate the CSV and run the detector. Find P06 in the JSON. Locate its five evidence rows in the CSV.
2. Calculate the first-to-last failure interval and last-failure-to-success interval yourself.
3. Run the tests. A passing test means an explicitly checked behaviour worked; it does not prove all inputs or real attacks are covered.
4. Copy the CSV into `local-results/` (create that folder yourself). In the copy, change E06 from `12:10:00Z` to `12:10:01Z`. Run the utility against the copy: expect two alerts. Restore the time and expect three. Keep the original fixture unchanged.
5. Explain why A06 is still an alert even though the scenario manifest says it is authorized. Write your answer before reading the report's comparison section.

Suggested learning pace: two focused sessions for reading/running and a third for changing a case and explaining the code. More free time does not require rushing into a larger lab.

## Local Git basics

Git tracks versions; GitHub hosts shared repositories. Running Python does not require either. The first milestone was prepared locally and subsequently authorized for public GitHub publication. After publication, `origin` points to the portfolio repository.

```text
git status --short
```

Open README.md to review it. Before staging, inspect the file list and ensure it contains only the synthetic lab materials. When you are ready to make your own local commit:

```text
git add README.md analyze.py data docs queries reports tests .gitignore .github
git diff --cached --stat
git diff --cached
```

`add` stages the named files; `diff --cached` shows exactly what a future commit would contain. It does not upload them. The publication workflow uses a repository-local GitHub username and GitHub noreply email to avoid exposing a private email. Review future changes before committing or pushing them. GitHub CI is not considered verified until an actual hosted run succeeds.

## Optional next exercise: observe a Windows event

Status: documented, not performed or verified on your VM. Your 32 GB RAM and 2 TB SSD are sufficient for a small lab, but the hypervisor and guest OS versions remain unspecified. Start with an existing Windows guest, not a new purchase. Use a legitimate existing licence or a suitable evaluation under its terms; synthetic analysis avoids any Windows licensing dependency.

Use an isolated virtual switch without a bridge to work, school or household production networks. Take a VM snapshot before policy changes. Use invented lab accounts and no employer data. A separate client and server are helpful later for network logons; signing in at the VM console usually exercises another logon type and will not satisfy AUTH-001.

On the target Windows VM, open an elevated Command Prompt and inspect policy:

```text
auditpol /get /subcategory:*
```

This lists effective audit settings; it does not change them. Locate the Logon subcategory (names can be localized). Save your existing settings privately or use the VM snapshot for restoration.

On Windows editions exposing Local Security Policy, open `secpol.msc`, then Advanced Audit Policy Configuration > System Audit Policies > Logon/Logoff > Audit Logon. Configure Success and Failure for this lab exercise. On a domain member, controlling Group Policy can override local changes; inspect the effective policy again. Avoid mixing basic and advanced audit policy settings. Confirm the setting that forces audit subcategory policy to override legacy category settings where applicable.

Open Event Viewer > Windows Logs > Security. Filter for 4624 and 4625. Inspect Details > XML View, including the target account, computer, timestamp, source IP, logon type and failure status/substatus. Observe one authorized success and, if safe under your lab lockout policy, one manual incorrect-password attempt. Do not generate repeated failures until you understand the lab account lockout threshold. The synthetic dataset already provides the repeatable five-failure case.

For network resource access, inspect the destination/resource host, not just the client. Audit Logon records creation of sessions on the accessed computer; domain account validation can involve different events on domain controllers. This is why a console sign-in or DC-only export is not interchangeable with the network scenario.

Preserve any real lab exports under ignored `local-evidence/`, with original timestamps and provenance. Review manually before sharing. Do **not** feed them into v1 by marking them synthetic. A sanitized adapter and real-evidence provenance handling are a separate future milestone.

Sources checked 2026-11-03: [Audit Logon](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/audit-logon), [auditpol](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/auditpol), [advanced audit policy](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/advanced-audit-policy-configuration).

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `python` unavailable | Try `py` on Windows or `python3` on Linux; verify an installed interpreter |
| Cannot find CSV/script | Terminal must be in the repository root; paths are relative to it |
| Header or line validation error | Restore the documented header/order, UTC Z timestamps, unique IDs and synthetic flag; do not suppress validation |
| Unexpected alert count | Check that you are running the original file; manually check matching keys and both time windows |
| Tests fail on expected output | Inspect the behaviour and changed inputs first; never overwrite expected output just to get a pass |
| No 4624/4625 in VM | Check effective audit policy, correct destination, Security log permissions, retention and time filter |
| No IP or logon type differs | Some logons do not provide usable source IP; v1 intentionally excludes them |
| CSV exported by Event Viewer fails | Native export is not this lab schema; no import adapter exists yet |

## Cleanup

Offline commands do not modify system policy or create cloud resources. Remove your own temporary copies from `local-results/` when finished. Keep the delivered evidence and reports. Python may create ignored `__pycache__` directories, which can be deleted manually if desired.

If you performed the VM exercise, preserve the evidence you need and restore the pre-exercise VM snapshot or your recorded policy settings. Remove only test accounts/resources you created. Do not clear Security logs as a cleanup shortcut. No cloud cleanup is needed for milestone 1.
