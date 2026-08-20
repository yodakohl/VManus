# D04 surface-components attestation

Decoder ID: `D04_surface_components`; designer model: `gpt-5.6-luna`.

This decoder was designed to consume only the public blind-decoder contract,
implementation API, and the observation rows supplied at runtime. It does not
read oracle rows, world generators, designs, manifests, codebooks, genealogy,
other decoders, or manuscript material. Training recurrence, visible strings,
separators, token position, and record-key shape are fit from `train_rows`
only. Held rows are never used to fit thresholds or vocabularies.

All emitted labels are salted-free deterministic anonymous hashes or explicitly
`UNRESOLVED`; no label is presented as a meaning or translation. Relations,
references, and scopes remain unresolved because surface recurrence alone does
not defensibly identify event links.

The implementation ingests only an explicit allowlist of observable surface
fields and rejects keys suggestive of oracle, truth, meaning, semantic, label,
target, relation, reference, scope, translation, or gloss data. Components
recur across at least two distinct token forms. Productive and fossilized
component sets are disjoint by construction; fossilized output is retained
only for a separate low-recurrence criterion.

No Voynich or f84 material was accessed, and this decoder was not executed
against observations during development (source-only edits and hashing).
