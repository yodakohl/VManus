# GDT345 prepublication model-label correction

Date: 2026-08-19

The public freeze commit `97a0f97` was followed by one immediate, uncommitted
diagnostic run. It reported a nominal `FACTORIAL_OPERATOR` gain of
8,085.840976 bits over exact predecessor and max-two p=.000244.

That result is invalidated and is not evidence. The V1 `PLACEMENT` model counted
the source-relative labels `KEEP` and `SET:<target>` without conditioning on the
source value. Since the name of the delta is itself a deterministic function of
source and target, a source-aware model could beat this null even if target
coordinates were independently generated. Shrinking exact-predecessor tables
to that same direct-delta baseline inherited the asymmetry.

The corrected V2 instrument uses target-coordinate values as the common
categorical label space for all four models. Only after a held target value is
predicted is it mapped mechanically to a source-relative delta and applied to
the source state. `PLACEMENT` is therefore the fair independence model
`P(target-coordinate | observable layout)`, while exact predecessor, full
source state, and factorial source-component models add their respective
source information to the same target-value code.

No gate, smoothing constant, split, state coordinate, operator application
rule, null world count, semantic restriction, or f84 seal changed. The V1
generated files were never committed or pushed. V2 is frozen before its
authoritative scores are generated.
