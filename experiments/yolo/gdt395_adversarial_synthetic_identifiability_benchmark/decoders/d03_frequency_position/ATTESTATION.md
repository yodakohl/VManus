# D03 oracle-blind attestation

`D03_frequency_position` is an intentionally inexpensive standard-library
baseline designed independently by `gpt-5.6-luna`. Luna used only
`DECODER_CONTRACT.md`, `DECODER_IMPLEMENTATION_API.md`, and
`src/decoder_api.py`. No Voynich file, `f84`/`f84r` material, oracle row, world
generator, codebook, genealogy, manifest, artifact, or other decoder was
accessed.

The decoder learns only from supplied training observations: opaque identity
frequency, string shape, explicit record/line and boundary-position
associations, recurrence within a record, and anonymous schema/register
clusters. Identity is read only from the explicitly licensed observable field
names; unsupported or answer-bearing fields are ignored. Set-valued fields are
canonicalized deterministically. Without a licensed surface identity,
entity/lexical/stem claims remain `UNRESOLVED`; without a supported record,
schema/register claims remain `UNRESOLVED`. Reference, scope, semantic,
component, and meaning claims remain `UNRESOLVED`; no cluster is presented as
an English meaning. World scores are structural heuristics, not truth-fitted
probabilities.

No decoder import or function execution was performed while creating or
repairing this decoder. Only source compilation with `py_compile` is permitted
for verification.
