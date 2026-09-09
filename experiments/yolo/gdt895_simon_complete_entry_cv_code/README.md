# GDT895 — complete dictionary entries under one CV code

Status: `ALL_FOUR_PANELS_UNSAT`; independent full validation PASS. See [REPORT.md](REPORT.md),
[METHOD.md](METHOD.md) and [src/SPEC.json](src/SPEC.json).

Acquire the fixed captures into a separate cache using src/acquire_source.py;
supply a future UTC deadline. Then use src/replay_source_cache.py with
--receipts artifacts/RECEIPTS.json --captures artifacts/CAPTURES.json
--cdx artifacts/CDX_ALL.raw --acquired-cache ACQUIRED --replay-cache ORIGINAL.
It preserves original missing decisions and receipt bytes; it rejects changed
bodies. Modern HTML remains in the caller's local cache.

Run src/source_text.py and src/validate_source.py on ORIGINAL as documented
in METHOD.md. Their pool/audit hashes must match artifacts/SOURCE_LOCK.json.
The target is the fixed already validated GDT893 odd-only packet. First run
src/check_entry_domains.py, then src/fit_cv.py on all unresolved panels with
--budget-seconds 300 --solution-limit 10000; validate via
src/validate_entry_domains.py and src/validate_cv.py using the same limits.
Each CLI exposes required paths with --help. Full source text is not published.
