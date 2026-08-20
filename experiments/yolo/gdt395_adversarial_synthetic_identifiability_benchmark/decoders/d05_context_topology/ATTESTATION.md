# D05 attestation

D05 is an independent, oracle-blind decoder designed by `gpt-5.6-luna`, based
on explicitly licensed observable surface equality, adjacent cooccurrence,
record/line identity, and anonymous graph topology. It fits all vocabularies,
frequency thresholds, and context labels from `train_rows` only. It reads no
world metadata, generator, oracle, codebook, genealogy, or other decoder
output.

The implementation has not accessed Voynich material or `f84`, and has not
executed the decoder or inspected corpus/world/oracle data. Only a source
syntax check is permitted for this attestation.

The emitted labels are hashes of observable structural features. They are not
English translations or semantic names. Surface extraction is restricted to
the explicit licensed fields in the source; blocked oracle/truth/meaning,
semantic, and label-like keys are ignored, and set-valued values are rejected.
If surface, record, or topology evidence is absent, the corresponding claims
remain `UNRESOLVED`; no implicit per-event records are created. Directional
relation, reference, and scope claims remain `UNRESOLVED` because this decoder
has no alignment oracle. Component labels are likewise anonymous structural
component candidates.
