# D01 oracle-blind attestation

Decoder: `D01_MULTIVIEW_GRAPH`

I designed this decoder using only `DECODER_CONTRACT.md`,
`DECODER_IMPLEMENTATION_API.md`, and `src/decoder_api.py` from the GDT395
benchmark directory. I did not inspect any observation corpus, held packet,
world source, design or method document, generator, manifest, artifact,
oracle, codebook, genealogy, other decoder, Voynich source, or f84 material.

The implementation uses only Python's standard library. All discovered field
roles, vocabularies, frequencies, distributional contexts, affix candidates,
function/operator candidate sets, and numeric thresholds are fit from
`train_rows`. Held rows contribute only their visible event values and the
within-packet equality/topology graph needed to issue held-event predictions.
No readable semantic labels are emitted: predictions are anonymous stable
hash clusters or `UNRESOLVED`.

The decoder supports all six contract representations through the exact
`decode(train_rows, held_rows, representation)` and
`classify_world(train_rows)` API. It has not been run against benchmark data
or validation output during design.
