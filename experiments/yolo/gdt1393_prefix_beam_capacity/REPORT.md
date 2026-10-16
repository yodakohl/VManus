# GDT1393 — reject the fixed forward beam before building its full decoder

**PREFIX_GATE_FAIL_NO_FULL_BEAM_ENGINE.** Ten of twelve positive control
messages already lose their correct first ten characters from all six fixed
source-prior beams. A later constraint or final likelihood score cannot recover
a discarded prefix in this algorithm. Stop its full implementation; no native
passage is decoded and no width, source-model or traversal repair is selected.

| Previously exposed controls | Prefixes retained in any beam | Total |
|---|---:|---:|
| Positive,77 characters |0|6|
| Positive,120 characters |2|6|
| Shuffled negative,77 characters |0|6|

The two retained prefixes are C07 in the middle-French model's beam and C17 in
the old-Hungarian model's beam. These are proposal-model memberships, not
language identifications or recovered messages. Their remaining characters
were not searched. Negative retention is not a readability false-positive rate.

## Why the short check is decisive for this proposed algorithm

GDT1390 demonstrated a search failure: all twelve true keys scored above its
returned wrong winners. A source-character beam with exact modular constraints
would be a different search strategy, not more restarts of that optimizer.
Before implementing it, the preceding diagnostic calculated when those
constraints first become useful.

For each of the eighteen old control matrices, every possible ten-character
prefix has a compatible modulo27 key. The first partial or complete character
restriction occurs at position11–21. Thus the proposed forward beams initially
select by the source model alone. The valid-key requirement does not change
this: modulo27 surjectivity permits lifts of modulo3 kernel directions, and
the13-dimensional kernel cannot vary only the offset. Every prefix therefore
also has a glyph key with at least one weight not divisible by3.

Each of the six unchanged order3 models retained65,536 prefixes at every step,
using cumulative source log probability and lexical tie-breaking. The union
still lacks ten positive true prefixes. The specified full search never
reintroduces discarded prefixes and applies the complete normalized channel
likelihood only to surviving complete candidates. Consequently it cannot meet
the unchanged all-twelve full-message control gate. We did not build the affine
decoder, search keys, fit a new language model or enlarge the beam.

This result does not reject a channel-aware proposal score, another traversal,
exact maximum-likelihood recovery, the cumulative writer or a source language.
Nor does it establish that the two surviving prefixes would survive later.
GDT1390's original decision remains a failure of its own different search.

## Evidence and verification

The preliminary rank diagnostic compared exact finite-ring image sizes with
affine-generator updates and exhaustive small fixtures. It corrected an
initial informal suggestion that23 initial characters would all be free:
constraints actually appear earlier. Its complete position schedules and
source hashes are retained in the existing C1064 dossier; this is control
geometry, not a native-manuscript finding.

The experiment code, protocol, six source tables and coefficient inputs were
locked at08:59:21 UTC. All six beam sets were computed without reading truth
in this computation, taking2.345seconds; their output seal was written at
09:00:25 UTC before the historical truth comparison was authorized. Cases
and truth had already been public and examined during1390. This order prevents
new outcome-driven changes; it does not create a fresh blind sample.

The independent implementation uses full sorting rather than partial selection,
recomputes every depth's retained set and score summaries, matches all final
arrays, independently verifies all180 first-ten modular choices, and reproduces
all eighteen membership records. Its3716 source-free fixture checks also pass.
The software validates this calculation and conditional decision, not meaning.

No Voynich text, image, new source corpus or reserve was opened. Confirmed
Voynich word meanings remain zero. The earlier ten-hour research request is
not fulfilled by this bounded control-method check.

Reproduce the full calculation and independent validation in a fresh directory:

```sh
python experiments/yolo/gdt1393_prefix_beam_capacity/src/reproduce.py --output-dir .cache/replay1393
```

See `PREREGISTRATION.md`, `METHOD.md`, `artifacts/COMPARISON.json`,
`artifacts/VALIDATION.json` and the manifest for exact inputs and limits.
