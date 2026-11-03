# Milestone 1 verification

Verification date: 2026-11-03. Environment: Windows, Python 3.14.2, Git 2.53.0.windows.3. Checks were executed in the local project directory.

## Observed checks

| Command/check | Observed outcome |
| --- | --- |
| `python analyze.py data/authentication.csv --validate-only` | Exit 0; validated 32 synthetic events |
| `python analyze.py data/authentication.csv` | Exit 0; three alerts, success IDs P06, A06, E06; five failures each |
| `python -m unittest discover -s tests -v` | Exit 0; 21 tests passed |

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

- KQL syntax/runtime behaviour in a Kusto service; no live platform query was run.
- Real Windows audit collection, native EVTX conversion and sanitized real-log ingestion.
- Python versions other than the locally tested 3.14.2 and the GitHub CI Python 3.14 environment.
- Sentinel/Defender licensing in an actual tenant, agents, roles, connectors, rules or alerts.
- Current CompTIA exam availability/latest blueprint revision: mapping is pinned to accessible official SY0-701 v6.0 objectives. SC-200 guide effective October 21, 2026 was checked.
- Privileged group membership and PowerShell cases: planned only.

## Public release verification

Published to `husseinabdulkader/windows-soc-investigation-lab`. The initial remote head matched local commit `faeb75a7284d9a56c033210cade29147b3f2a768`. The [GitHub Actions run](https://github.com/husseinabdulkader/windows-soc-investigation-lab/actions/runs/41594928632) completed successfully on Ubuntu with Python 3.14, validating the dataset and running the test suite. Later documentation-only commits do not change the tested detector.
