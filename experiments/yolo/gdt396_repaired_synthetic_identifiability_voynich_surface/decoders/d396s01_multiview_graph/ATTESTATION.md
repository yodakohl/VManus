# D396S01 blind decoder attestation

Decoder ID: `D396S01`

Designer model: `gpt-5.6-sol`

Method family: `MULTIVIEW_RECORD_GRAPH`

API: GDT396 decoder API V2

I designed and implemented this decoder in an isolated context. I inspected
only the workspace instructions/current-route snapshot, the four authorized
GDT396 interface files (`CLAIM_INTERFACE.md`, `DECODER_QUALIFICATION_SPEC.md`,
`src/decoder_api_v2.py`, and `src/observation_api.py`), and blind development
observations loaded through `observation_api`.

I did not inspect any GDT395 world source, design, generator, oracle, codebook,
genealogy, scorer, report, or other implementation. I did not inspect GDT396
qualification or confirmation material, sibling decoder source or output, any
Voynich source, `f84`, or `f84r`. I did not use a cross-surface mapping. I did
not score the development smoke test against truth.

The decoder learns all vocabularies, graph/record centroids, recurrent
components, transition counts, and thresholds from its supplied training rows.
Held decoding uses only visible equality and physical record, line, boundary,
register, hand, layout, and position metadata. Its ranked candidate universes
are the frozen visible-only `RECORD_EXCL_SELF` and `PRIOR_SEED_EVENTS` sets.

The decoder emits anonymous class and relation subtype identifiers, treats
structural classes as nonsemantic, and explicitly abstains when a supported
component or scope analysis lacks its frozen evidence threshold.
