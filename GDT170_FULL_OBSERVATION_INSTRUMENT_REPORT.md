# GDT170 — full observation-layer instrument calibration report

Status: **PARTIAL_IDENTITY_AND_RECORD_SIGNAL_WITHOUT_COMPONENT_ARCHITECTURE_RECOVERY**.

GDT170 upgrades GDT168 by forcing both causal worlds through a manuscript-like
observation boundary.  The blind parser saw only visible groups, separators,
physical line/layout roles, register/hand metadata and permitted neutral
annotations.  Concepts, plaintext, codebook, record slots and encoder fields
were opened only after the 480,000 blind parses were committed and published.

## Recovery by instrument level (primary renderer)

| world | level | host information fraction | host held decoder accuracy / coverage | full-tuple held decoder accuracy / coverage | readout |
|---|---|---:|---:|---:|---|
| A: lexical codebook | surface only | 1.000 | 1.000 / 0.245 | 1.000 / 0.223 | PARTIAL_LEXICAL_IDENTITY_RECOVERY_WITHOUT_COMPONENT_SEGMENTATION |
| A: lexical codebook | annotation assisted | 1.000 | 1.000 / 0.233 | 1.000 / 0.223 | PARTIAL_LEXICAL_IDENTITY_RECOVERY_WITHOUT_COMPONENT_SEGMENTATION |
| A: lexical codebook | oracle ceiling | 1.000 | 1.000 / 0.516 | 1.000 / 0.223 | KNOWN_ARCHITECTURE_RECOVERED |
| B: distributed record code | surface only | 0.929 | 0.298 / 0.699 | 1.000 / 0.223 | PARTIAL_DISTRIBUTED_RECORD_SIGNAL_RECOVERY_WITHOUT_COMPONENT_SEGMENTATION |
| B: distributed record code | annotation assisted | 0.942 | 0.340 / 0.622 | 1.000 / 0.223 | PARTIAL_DISTRIBUTED_RECORD_SIGNAL_RECOVERY_WITHOUT_COMPONENT_SEGMENTATION |
| B: distributed record code | oracle ceiling | 0.443 | 0.048 / 1.000 | 1.000 / 0.223 | KNOWN_ARCHITECTURE_RECOVERED |

Empirical information on nearly unique inferred strings is optimistic; the
held-source decoder is the decisive calibration.  The blind levels do recover
limited transferable signal: System A's inferred whole-surface-like identities
decode perfectly where seen at 23--25% coverage, and System B's visible full
group plus physical record position decodes perfectly at 22% coverage.  These
are partial lexical-identity and distributed-record signals.  They are not a
recovery of the hidden components: exact true-host, left-edge, right-edge and
full-decomposition rates are all zero.  The oracle reproduces the original
GDT168 ceiling: System A's true host is a complete lexical address, while
System B requires its distributed tuple and slot.

## What annotations help

Visible layout helps find a subset of closure behavior: in the primary views,
annotation-assisted inferred right marks have record-end precision 1.0.  It
does not solve segmentation.  Exact true-host recovery is zero, the true
2–3-character host mass is reported as zero by the blind parser, operation
compatibility is zero, and the implanted distributed substitution coupling in
System B is missed.

## Instrument consequence

GDT168's earlier host and compiler diagnostics were computed from supplied
HPR2-analog truth columns.  They therefore calibrate **oracle-field
diagnostics**, not the end-to-end VManus surface pipeline.  GDT170 shows that
the current generic prefix/suffix contrast parser can recover some record
closure and some whole-identity/position transfer, but cannot recover either
the implanted lexical host boundary or the distributed compiler components
from manuscript-like observations.

Accordingly, a negative Voynich PAGE_HOST result cannot by itself distinguish
the two architectures, and an oracle-level positive cannot be credited to the
surface parser.  A future instrument improvement must be judged on these
frozen synthetic observations, not tuned on Voynich outcomes.

No Voynich source or image was used.  f84r was not accessed.
