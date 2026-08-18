# GDT310 — source-side-only operation-license prediction

Status: **SOURCE_SIDE_LICENSE_NOT_PREDICTABLE**.

Predictors are computed only from the source wrapper of each operation. Target q/s events supply the binary license label but no predictor values.

| operation | hosts (+) | FULL gain | AUC | AP | max-12 p | class |
|---|---:|---:|---:|---:|---:|---|
| `wrapper:NONE>q` | 52 (31) | +0.0009 | 0.599 | 0.727 | 0.587330648114 | TARGET_BLIND_LICENSE_OPAQUE_OR_UNRESOLVED |
| `wrapper:ch>s` | 25 (7) | -0.0387 | 0.619 | 0.380 | 0.970096423776 | TARGET_BLIND_LICENSE_OPAQUE_OR_UNRESOLVED |
| `wrapper:d>s` | 16 (8) | -0.0362 | 0.867 | 0.760 | 0.858171609911 | TARGET_BLIND_LICENSE_OPAQUE_OR_UNRESOLVED |

## Fixed ablations

| operation | layout gain | compiler gain | register gain | full gain |
|---|---:|---:|---:|---:|
| `wrapper:NONE>q` | +0.0196 | +0.0044 | -0.0273 | +0.0009 |
| `wrapper:ch>s` | +0.0144 | -0.0149 | -0.0925 | -0.0387 |
| `wrapper:d>s` | -0.0108 | +0.0199 | -0.0393 | -0.0362 |

## Interpretation

None of the operations passes the frozen target-blind rule. GDT309's observed-ecology classification therefore does not survive removal of target-wrapper events; the compatibility lists remain opaque under this low-capacity instrument.

## Claim ceiling

Target-blind formal alternant-license prediction only; no lexical class grammar semantics sound language plaintext meaning or translation. No f84 row was opened, parsed, retained, joined, or scored.
