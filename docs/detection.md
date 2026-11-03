# AUTH-001: failed network logons followed by success

Status: implemented in `analyze.py`; local tests documented in the verification report. This is a lab rule, not a Microsoft rule or a production-ready analytics rule.

## Exact behaviour

1. Validate and sort the entire input by timestamp. At equal timestamps, process failures before successes. Equal-time failures cannot establish that they preceded that success.
2. Consider only logon type 3 and a known source IP.
3. Group by destination computer, target domain, target account, source IP and logon type. Compare names case-insensitively.
4. For each successful logon, consider failures **strictly earlier** than that success and **after the previous matching success**. An intervening success resets failure history, even if it did not alert.
5. Let F be the last of those failures. Count failures in the inclusive interval `[F - 5 minutes, F]`. Alert if the count is at least 5 and success occurs no more than 5 minutes after F.
6. Emit one alert per matching success, with every counted failure ID. Reset history. No alert is emitted for failures without a success.

These are rolling windows anchored to actual events, not fixed five-minute clock bins. A boundary-crossing burst must not disappear simply because the clock passes 09:05. Two windows mean a sequence can span ten minutes; the bundled E case demonstrates that.

The threshold is a transparent teaching choice. It is not derived from business baselines or validated production precision/recall. The output contains facts, not an automatically assigned incident severity.

## False positives and missing coverage

Repeated password mistakes, cached credentials repaired by support, scripted retries and shared source IPs can trigger. The authorized A case deliberately triggers. A whitelist would hide that example but would not solve the need to establish authorization.

Distributed guessing, password spraying across accounts, low-rate attacks, successes using another IP, missing telemetry and non-network logons are outside coverage. Missing IPs are excluded rather than joined together. Missing events may cause false negatives. Duplicate evidence labels fail validation rather than inflating the count. Equal timestamps are ambiguous and treated conservatively.

## Tuning safely

Review distributions by account type and destination before changing the count/window. Track known authorized events and unexplained alerts separately. Use narrowly scoped, time-limited exceptions supported by evidence; retain the source records. Test below, at and above any new threshold. Larger windows catch slower activity but may connect unrelated retries. Lower thresholds increase sensitivity and analyst workload. This fixture is too small to estimate accuracy or choose a production threshold.

## Query learning

`queries/authentication-demo.kql` shows a self-contained table, filtering, joining and time-window counting. It is **illustrative and unexecuted in Kusto**. It uses only one success per account and does not implement Python's intervening-success reset. Do not substitute it for the Python detector or label it a deployed Sentinel rule. See [platform boundaries](platforms.md) before using any tenant table.
