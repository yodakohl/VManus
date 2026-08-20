# D396S03 blind-decoder attestation

Decoder ID: `D396S03`

Method family: `RELATION_SCOPE_TOPOLOGY`

Designer context: independent Sol decoder context.

I attest that this decoder was designed and implemented under the GDT396 V2
blind boundary. I inspected only:

- `CLAIM_INTERFACE.md`;
- `DECODER_QUALIFICATION_SPEC.md`;
- `src/decoder_api_v2.py`;
- `src/observation_api.py`;
- development observations returned by `observation_api`.

I also read the workspace-required `AGENTS.md` and
`VOYNICH_CURRENT_ROUTE.md` before beginning. Those routing documents were not
used as decoder features or world labels.

I did not inspect a GDT395 world source, design, generator, oracle, codebook,
genealogy, scorer, report, or output. I did not inspect a sibling GDT396
decoder, sibling claims, qualification corpus, confirmation corpus, Voynich
source, `f84`, or `f84r`. I performed no truth scoring. FREE_SURFACE and
VOYNICH_SURFACE development checks ran in separate processes and no
cross-surface correspondence was retained.

The implementation treats visible atoms as anonymous equality values. Its only
surface operations are exact equality and contiguous component equality. All
thresholds and architecture rules were frozen from blind development
observations. At runtime, learned vocabularies, component candidates, role
maps, schema recurrence, boundary strengths, and scope modes come exclusively
from the supplied training rows. Declared held-seed transduction is limited to
visible equality/document recurrence used for anonymous partition resolution;
it does not fit thresholds or use hidden anchors.

The decoder intentionally abstains where topology does not license a semantic
name. Anonymous IDs are deterministic hashes. It emits record-local relation
candidates, genuinely prior same-seed reference candidates, adaptive
same-record scopes, proper-substring component spans, recurrent record-schema
clusters, and an explicit multi-constraint versus scalar architecture contrast.

Development self-tests checked API V2 table shapes, canonical-JSON model
serialization, model immutability across decode, target locality, unique and
contiguous descending ranks, same-record ordered scope endpoints, legal
morphology offsets, both surface channels, and deterministic reruns. These are
engineering checks only and are not qualification or scientific results.
