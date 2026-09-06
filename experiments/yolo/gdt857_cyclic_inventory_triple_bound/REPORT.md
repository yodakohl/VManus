# GDT857 — literal triples contradict exclusively nonsingleton cyclic pools

**Four exact all-reader coordinates contain a plain whole group three times
in succession, with definite internal and exterior boundaries.** Under the
registered cyclic-pool contract, each such codeword must have a singleton
pool. The subclass requiring every pool to contain at least2members is
therefore contradicted, conditional on the transcription and whole-group
codeword assumptions. This does not reject homophony generally.

## Exact three-reading coordinate concordance

| Locus | First source group | Literal triple |
|---|---:|---|
|f104v.27|3|`sheol sheol sheol`|
|f40r.9|6|`okaiin okaiin okaiin`|
|f47r.7|4|`chol chol chol`|
|f86v3.3|2|`ytaiin ytaiin ytaiin`|

The agreement key is exactly locus/start_index/raw. The three readings are
alternate observations of one manuscript, not independent manuscript copies.
No native image adjudication was performed. All four listed cases also have
definite exterior fields; no line-edge exemption is needed for them.

## Complete registered census

| Reading | Candidate P triples | Structurally eligible plain triples | Equal triples | Distinct repeated forms | Physical folios |
|---|---:|---:|---:|---:|---:|
| ZL3b | 24392 | 15543 | 6 | 6 | 6 |
| IT2a | 23910 | 21837 | 7 | 7 | 7 |
| RF1b | 23978 | 14337 | 5 | 5 | 5 |

Every stored three-group P window is a candidate. Eligibility adds plain raw
strings, consecutive indices, definite interior seams on both adjoining
fields, and the registered exterior-boundary conditions. Equality is then
required across all three groups. Overlapping windows are retained; counts
are not independent-trial denominators and no statistical test is attached.

## Every retained source witness

| Reading | Locus | Start group | Raw repeated group |
|---|---|---:|---|
|ZL3b|f104v.27|3|`sheol`|
|ZL3b|f108v.40|3|`qokeedy`|
|ZL3b|f40r.9|6|`okaiin`|
|ZL3b|f47r.7|4|`chol`|
|ZL3b|f79v.19|5|`qokedy`|
|ZL3b|f86v3.3|2|`ytaiin`|
|IT2a|f104v.27|3|`sheol`|
|IT2a|f108v.40|3|`qokeedy`|
|IT2a|f40r.9|6|`okaiin`|
|IT2a|f47r.7|4|`chol`|
|IT2a|f79v.19|5|`qokedy`|
|IT2a|f81r.5|4|`ol`|
|IT2a|f86v3.3|2|`ytaiin`|
|RF1b|f104v.27|3|`sheol`|
|RF1b|f40r.9|6|`okaiin`|
|RF1b|f47r.7|4|`chol`|
|RF1b|f79v.19|6|`qokedy`|
|RF1b|f86v3.3|2|`ytaiin`|

These18reading-specific records cover7distinct source loci on7physical
folios. At f79v.19 the qokedy triple starts at group5 in ZL3b/IT2a and group6
in RF1b; it is therefore excluded from the strict coordinate intersection,
not silently realigned. qokeedy at f108v.40 qualifies in ZL3b/IT2a only;
ol at f81r.5 qualifies only in IT2a. Absence from this exact inventory does
not supply the excluded alternative reading or a manuscript absence claim.
All18retained windows have definite exterior fields. Full raw rows, indices,
source IDs and metadata are in HITS.json; WITNESS_LINES.json contains each
complete corresponding source line with its native separator information.

## The deterministic implication and its limits

In a pool visiting each distinct member once per cycle, A A may straddle
one refill: A ends one cycle and starts the next. A third A immediately
requires the second A to end that next cycle too. That cycle has only A,
so the pool is singleton. Arbitrary permutations and starting phase do not
change this implication. The mathematical argument, not toy simulations,
supplies the bound.

The contract assumes each entire raw group is one codeword, disjoint fixed
pools, every draw visibly output exactly once unchanged, no hidden/skipped
draws, no different members sharing one visible spelling, and no copying or
transcription errors inside the model. It also forbids resets within the
physical prose line. These are explicit assumptions, not established facts
about the manuscript. The registered subclass fails under these assumptions.

A model permitting some singleton pools is not rejected. Nor does this test
reject sampling with replacement, contextual pool changes, finer-than-group
codewords or other mechanisms outside the contract. None is automatically
installed as a rescue. No codeword meaning, plaintext, alphabet, language,
null probability or general homophony result follows.

## Reproduction and timing

Preregistration f77c6472 was public at07:01:21UTC before cache loading.
All three frozen GDT851 source hashes matched;179selectors and explicit
f84/f84r exclusions remained unchanged. No new query, image, annotation
normalization, frequency model or post-result filter was used.

Independent validation reconstructed every source window and denominator,
verified each witness directly against its source IDs/metadata, and rebuilt
the exact three-reading coordinate intersection. Cached replay was byte-
identical and source/result binding passed. Registered toy cycle/phase and
source-boundary controls passed independently before data; they are software
checks, not empirical cipher evidence. Run, validation and replay took about
1.2seconds. This fixed deterministic counterexample test is complete.
