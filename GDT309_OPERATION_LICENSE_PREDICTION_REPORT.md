# GDT309 — opaque-host operation-license prediction

Status: **OPERATION_LICENSE_PARTLY_COMPRESSIBLE**.

No host glyph, substring, exact identity, surface identity, or wrapper count enters a predictor.

| operation | FULL gain | AUC | AP | max-12 p | class |
|---|---:|---:|---:|---:|---|
| `wrapper:ch>s` | -0.0041 | 0.913 | 0.525 | 0.880751861345 | OPAQUE_OR_UNRESOLVED_LICENSE |
| `wrapper:d>s` | +0.0019 | 0.885 | 0.530 | 0.624191382888 | OPAQUE_OR_UNRESOLVED_LICENSE |
| `wrapper:NONE>q` | +0.0709 | 0.806 | 0.828 | 0.040522397168 | STRUCTURALLY_PREDICTABLE |

## Model ablations

| operation | layout gain | compiler gain | register gain | full gain |
|---|---:|---:|---:|---:|
| `wrapper:ch>s` | -0.0017 | +0.0029 | +0.0013 | -0.0041 |
| `wrapper:d>s` | +0.0001 | +0.0044 | +0.0037 | +0.0019 |
| `wrapper:NONE>q` | +0.0653 | +0.0299 | -0.0033 | +0.0709 |

## Interpretation

`NONE->q` licensing is the only structurally compressible relation under the frozen rule. Its layout block already gives +0.0653 Brier improvement and the strongest corrected tail, while register alone is negative. This agrees with q as a broad field/position ecology rather than a domain-invariant displacement vector. The high raw AUCs for `ch->s` and `d->s` are already present in the frequency baseline; allowed structural features add no corrected Brier improvement. Their positional operations remain real on compatible hosts, but their compatibility list stays opaque under this instrument.

## Causal limitation

Although wrapper values/counts are excluded as columns, each host summary uses all of that host's events, including target q/s occurrences. GDT309 therefore classifies the full observed ecology of a known license; it does **not** predict a target alternant before that alternant is seen. A source-side-only successor is required for causal license prediction.

## Claim ceiling

Opaque operation-license structural prediction only; no lexical class grammar semantics sound language plaintext meaning or translation. No f84 row was opened, parsed, retained, joined, or scored.
