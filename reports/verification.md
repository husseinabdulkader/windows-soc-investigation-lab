# Milestone 1 verification

Verification date: 2026-11-03. Environment: Windows, Python 3.14.2, Git 2.53.0.windows.3. Commands were run by the assisting agent in the local project directory. No user execution is claimed.

## Observed checks

| Command/check | Observed outcome |
| --- | --- |
| `python analyze.py data/authentication.csv --validate-only` | Exit 0; validated 32 synthetic events |
| `python analyze.py data/authentication.csv` | Exit 0; three alerts, success IDs P06, A06, E06; five failures each |
| `python -m unittest discover -s tests -v` | Exit 0; 21 tests passed |
| `git init -b main` | Local repository initialized |
| `git remote -v` | No remotes |

The observed unittest summary was:

```text
Ran 21 tests in 0.673s

OK
```

That duration is a single test-run observation, not a performance benchmark. The golden JSON file was saved from detector output after manually comparing the expected scenario IDs, counts, and time intervals with the fixture. Independent unit cases separately exercise the detection contract; the saved output alone would not independently validate the algorithm.

## Test coverage

Positive result and evidence IDs; unsorted events; below-threshold count; both exact time boundaries; one-second violations of each window; equal timestamps; success before failures; no success; every correlation-key component; case-insensitive identities; missing IP and non-network exclusion; history reset; tied failure non-reuse; fixture/golden comparison; UTF-8 BOM; malformed fields; duplicate IDs; empty input/wrong headers; wrong column count; CLI success and missing-file error.

The tests establish these specified behaviours, not complete security assurance, production accuracy or compatibility with every Python version.

## Artifact identity

SHA-256 of the exact delivered evidence/code at verification time:

```text
data/authentication.csv
2D9FA72A82B90CAB7D8C54BFD45D69FAC3BB675FFA8544838BAE2978973D39A4

analyze.py
64C7F6CCA8811DEC357BC3BB528059A964426359F92398C9117DF9142B63904E

reports/expected-alerts.json
62034424737A9A9CDEB4C0694DD9E7B716F93D6D9A0468733F08679F31AD2027
```

Line-ending conversion or subsequent edits can change hashes. These identify local artifacts, not authentic Windows evidence or forensic chain of custody.

## Unverified and deferred

- Independent authorship and unguided proficiency; learner-reported guided reproduction is recorded below.
- KQL syntax/runtime behaviour in a Kusto service; no live platform query was run.
- Real Windows audit collection, native EVTX conversion and sanitized real-log ingestion.
- GitHub Actions execution, Linux execution and Python versions other than 3.14.2.
- Sentinel/Defender licensing in an actual tenant, agents, roles, connectors, rules or alerts.
- Current CompTIA exam availability/latest blueprint revision: mapping is pinned to accessible official SY0-701 v6.0 objectives. SC-200 guide effective October 21, 2026 was checked.
- Privileged group membership and PowerShell cases: planned only.

## Learner acceptance checkpoint

During guided learning, the learner reported reproducing all three alerts, editing E06 by one second to obtain two alerts, and running all 21 tests successfully. They discussed alert-versus-incident reasoning and corrected the distinction between event IDs, accounts, destination and source. These are learner-reported actions and guided explanations, separate from the agent-observed checks above. Independent authorship or complete mastery is not claimed. The next case can now begin with another small guided exercise.
