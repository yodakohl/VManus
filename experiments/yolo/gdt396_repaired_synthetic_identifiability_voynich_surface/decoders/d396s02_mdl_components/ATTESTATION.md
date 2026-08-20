# D396S02 blind-decoder attestation

Decoder: `D396S02`  
Method family: `MDL_COMPONENT_CONTEXT`  
API: GDT396 decoder API V2

I designed this decoder in an isolated Sol context. I inspected only:

- `AGENTS.md` and `VOYNICH_CURRENT_ROUTE.md`, as required workspace routing
  instructions;
- `CLAIM_INTERFACE.md`;
- `DECODER_QUALIFICATION_SPEC.md`;
- `src/decoder_api_v2.py`;
- `src/observation_api.py`; and
- blind GDT396 development observations loaded through `observation_api`.

I did not inspect GDT395 world sources, designs, generators, oracles, codebooks,
genealogies, scorers, reports, qualification or confirmation packets, Voynich or
f84/f84r material, sibling decoder implementations, sibling claims, or sibling
outputs. I performed no truth scoring. No cross-surface mapping was supplied to
or used by the decoder.

All learned inventories, component sequences, surface/context counts, centroids,
and thresholds instantiated by `fit` come from its training rows. Held rows are
used only to enumerate visible legal candidates, visible within-packet equality,
and visible record order. The model is canonical-JSON-safe and decode does not
mutate it.

The primary construction is a recurrent proper-substring inventory selected by
a two-part compression balance, followed by non-overlapping construction spans,
coarse context and record-transition classes, train-only record-schema
centroids, and conservative relation/reference/scope/morphology claims. Exact
surface equality supplies the easy equality control. Component candidates must
occur in multiple complete surface types and records; high-coverage components
are rejected, and held singleton types are never promoted into learned singleton
components. A distinct semantics-light signal suppresses morphology when
within-record copying is high but cross-record transition and ordinal structure
are weak.

No semantic, linguistic, historical, or readable class name appears in an
anonymous predicted class or subtype ID.
