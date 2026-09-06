# Executable argument correction before target projection

The publicV1commitb05febf5 ran at10:20:25UTC. Both runner and validator encoded
the179allow-values as one comma-joined CLI value. query-tsv requires repeated
--allow flags (only --columns is comma-separated). Consequently allthree
projections selectedzero rows, includingzero of1777available fixed events.
No target raw group, category, full-line parity outcome or score was observed.
The population gate stopped as intended; the independent validator reproduced
the same zero-row stop but shared the argument-encoding bug.

Preserve attempt1/PROJECTIONS,RESULT,VALIDATION and PREREG_LOCK_V1; the original
source code remains reproducible atb05febf5. The new executable lock replaces
V1onlyafter this explicit amendment is publicly published. Runner and validator
now emit one --allow per page. Synthetic actual-CLI controls require two
allowed rows to materialize and one f84r fixture row to remain excluded.

No source selector, output column, source comparison, category, count, event
selection, source-contract gate or claim ceiling changes. This is a technical
pre-payload correction, not a rerun of a failed scientific hypothesis. Publish
the amended code/lock before the first nonempty target source projection.
