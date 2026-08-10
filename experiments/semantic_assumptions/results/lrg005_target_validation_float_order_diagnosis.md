# LRG005 target-validation arithmetic-order diagnosis

Status: **CORRECTABLE_VALIDATOR_ONLY_LOW_BIT_MISMATCH**.

The one authorized production target completed once and was not rerun. The
frozen clean validator reconstructed the complete score matrix, label vector,
nulls, folio effects, gates, status, and decision, but stopped before writing
validation output because two aggregate effects used an algebraically
equivalent scalar column mean instead of production's vectorized two-column
mean.

Only four low-bit scalars differ:

| channel | production effect | validator effect | difference | production z | validator z | difference |
|---|---:|---:|---:|---:|---:|---:|
| D1_BARE | 0.44034226134060517 | 0.4403422613406053 | -1.1102230246251565e-16 | 2.8397231549717943 | 2.839723154971795 | -8.881784197001252e-16 |
| D1_OTHER | -0.06604982340914846 | -0.06604982340914847 | 1.3877787807814457e-17 | -0.43950940861613413 | -0.43950940861613425 | 1.1102230246251565e-16 |

Every gate and the final nonconfirmation are unchanged. The original validator
and freeze remain immutable. A separately committed amendment may execute the
same non-production clean-room source with exactly two textual corrections:
construct `observed = folio_effects.mean(axis=0)` once, then take
`effect = observed[channel]`. It may not change any input, score, label, null,
gate, threshold, result, or report, and it may not rerun production.
