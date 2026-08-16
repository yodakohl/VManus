# GDT168 — synthetic PAGE_HOST architecture calibration

Status: **ENCODERS FROZEN BEFORE BLIND DIAGNOSTIC SCORING**.

## Question

Can the GDT113/GDT160/GDT162--167 diagnostic family distinguish a genuine
short lexical/code address from a record notation in which information is
distributed across slot, wrapper, host, right field, and closure?

This is an instrument calibration.  It does not score Voynich text and it
cannot establish a Voynich word, meaning, plaintext, or language.

## Frozen real source

Both synthetic worlds use exactly the same already-frozen
`LATIN_MEDICAL_GRAPHEMATIC` panel in
`gdt159_diplomatic_corpora.json.gz`: 12,000 normalized source groups from 21
source units in five real medieval medical manuscripts.  The source was
admitted and sampled before GDT159 scoring from public CREMMA Medii Aevi data
at commit `292525969ad98380b398e6606a9c2a36d51913ae`.  Its dates are
1100--1399.  It contains medical treatises, recipes and related practical
material.  No Voynich row or aggregate selects a source group, concept, code,
renderer, or threshold.

The normalized source group is the hidden plaintext/concept identity.  It is
not asserted to be a modern expansion, lemma, or semantic annotation.  Full
source strings, concept indices, codebook mappings and decoder fields are
retained only in the ground-truth export.

## Shared record layout and renderers

Within each source unit, sampled groups are restored to source occurrence
order and divided mechanically into 18-group records and six-group physical
lines.  The final short record/line is retained.  Every record is rendered in
five register variants and two scribal variants.  These ten views are aligned
renderings, not independent content samples.

All renderer keys are deterministic symbol permutations derived only from
`GDT168_RENDER_V1|register|scribe|alphabet`.  The 19-character host alphabet
and seven-character compiler alphabet are disjoint.  No character frequency,
operation statistic, rectangle count, Voynich form, or GDT result is used to
choose them.

## World A — fixed short concept codebook

Every one of the 6,175 source concepts receives one canonical injective code.
The 361 most frequent concepts receive two-character base-19 codes; all
others receive three-character codes.  Frequency breaks ties by a frozen
SHA-256 ordering.  The rendered PAGE_HOST is the canonical code under the
register/scribe host permutation.

Wrapper, local frame, right field, line closure and record closure are fixed
functions of record/line position only.  They contain zero concept bits.
Thus PAGE_HOST alone, plus the renderer key, recovers the concept exactly.

## World B — distributed record/template notation

Concept index `c` at record slot `s` is transformed to
`u = (c + 137*s) mod 6175`.  `u` is decomposed into a 100-way host digit and
three four-way digits carried by wrapper, right field and closure.  The joint
capacity is 6,400 states.  Given slot and all four digits, decoding is exact;
PAGE_HOST alone is a 100-way many-to-one value and is not lexical.  Physical
line and record markers are added separately.

The constants 100, 4, 4, 4 and 137 were chosen for hand-auditable mixed-radix
capacity and coprime slot rotation, not from Voynich measurements.

## Blind diagnostic stage

The blind scorer receives surface strings, HPR2-analog structural columns,
record/line positions, source-unit folds and renderer labels.  It cannot read
source plaintext, concept IDs, canonical codes, decoder digits, encoder type,
or any ground-truth file.

It applies frozen analogues of:

1. GDT113 record/layer recurrence and retrieval architecture;
2. GDT160/GDT003 operation scale, LEFT×RIGHT compatibility and a
   degree/frequency-preserving label null;
3. GDT162 short-host concentration, recurrence, Hamming-neighbor structure,
   exact-host and neighbor outer-context transfer;
4. GDT163/GDT164 substitution transfer to same-group compiler and external
   neighboring-host endpoints separately;
5. GDT165 immediate next-host transfer;
6. GDT166 unordered window and whole-line context transfer;
7. GDT167 within-register codebooks, cross-scribe stability and glyph-blind
   cross-register alignment.

The blind outputs and their hash are frozen before the unblind evaluator reads
ground truth.  The evaluator then measures which known properties were
recovered, missed, or spuriously attributed.

## Claim ceiling

This calibration can measure diagnostic sensitivity and specificity for two
constructed architectures.  It cannot show that either architecture generated
Voynichese and supplies no Voynich lexeme, code value, morpheme, POS, sound,
language, semantic role, plaintext, meaning, or translation.  No Voynich
source table or image is an input, and f84r is not accessed.
