# F76J001 independent prescore audit

Date: 2026-08-08  
Decision: **REVISE; TARGET MUST REMAIN UNRUN**

No target runner was executed and `TARGET_RESULT.json` was absent throughout
this audit.  The cached manual interlinear and the exposed target forms were
read only to audit source alignment and the proposed mechanism.  No image,
OCR, automated vision, English gloss, or semantic label was used.

## What is sound

- The current-locus pairs are reproduced by the Stolfi legacy/current locus
  table: `K1.4/6/8/11/14/17/21/24/29` map to `P1.4/6/8/11/14/17/21/24/29`,
  which are current loci `.4->.5`, `.7->.8`, `.10->.11`, `.14->.15`,
  `.18->.19`, `.22->.23`, `.27->.28`, `.31->.32`, and `.37->.38`.
  The manual source calls each K entry the label for its corresponding line.
- The marks are `s,d,q,s,o,l,k,r,s` in all three alternate readings.  The
  target page is excluded from model training.
- Enumerating `9!/3! = 60,480` assignments is the correct conditional orbit
  for the fixed mark multiset.  Synchronous assignments and the minimum
  alternate-reading z-score correctly avoid treating ZL/IT/RF as independent
  samples.  The tail convention counts ties against the observed assignment.
- This exact pairing mechanism is distinct from F76M001's aligned-line/block
  feature-bag similarity, F76V001's complete vertical-word ordering, and
  JD001's global `REL_I/FREE_SIDE` joined/detached role-transfer classifier.
  It is nevertheless post-exposure and cannot be called independent evidence.

## Blocking scientific mismatch

The registered statistic is not a test that joining is better than leaving a
mark detached.  For every assignment it sums

`log P(mark + word) - log P(word)`.

The second term is constant over every reassignment.  Consequently the exact
rank compares one set of **forced fusions** with other forced fusions; there is
no no-join or separate-token competitor.

Moreover, with the implemented order-2 character model the gain depends only
on the inserted mark and the first two characters of the line-first token.
All later characters have the same trigram contexts in `mark+word` and `word`
and cancel exactly.  The test therefore cannot establish that a complete
reconstructed word is ordinary.  Its real estimand is only local
`mark -> first-two-characters` compatibility.  The positive control's full
frequent words do not exercise whole-word reconstruction; only their planted
initial trigrams matter.

The source preserves the marks as separate left-margin units.  Left-side
placement and ordinary left-to-right writing fix the *side* of a hypothetical
attachment, but they do not establish erasure of the visible boundary.  A
pass of the current score would therefore not identify a detached prefix or a
control relation.  At most it would identify unusually compatible initial
character triples under one post-hoc forced-fusion model.

## Grammar distinction and rival mechanism

The second documented pair is standalone margin `d` followed by line-first
`qoaiin`.  In the frozen grammar the margin `d` row is `BARE`; it is **not**
the structural `D/BOUND_D` category in the confirmed mandatory-space
`D -> q` dependency.  Those two facts must not be conflated.

Even so, `dqoaiin` is only a hypothesized fusion.  The author-visible evidence
is `d | qoaiin`, and q is overwhelmingly a first parsed state in ordinary
prose.  The third pair would likewise become `qqotedshedy`.  A separate-token
boundary relation is therefore a required rival, not a dispensable
sensitivity.

A literal exact-mark separate-token line-start model is currently too sparse
to serve as that rival.  Outside f76r, complete one-character line-first
tokens followed by another token have counts for `s,d,q,o,l,k,r` of:

| reading | s | d | q | o | l | k | r |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZL3b | 18 | 3 | 1 | 23 | 3 | 1 | 1 |
| IT2a | 5 | 0 | 0 | 9 | 3 | 0 | 1 |
| RF1b | 30 | 10 | 2 | 15 | 7 | 2 | 2 |

Thus an exact identity-conditioned boundary-transition estimate has zero
all-reading support for several marks.  It must not be rescued with a
post-target favorable pooling rule.  A different boundary-aware formal model
would need its own score-blind support audit and controls before use.

## Implementation/control issues to repair

1. Rename the present estimand and ceiling to local initial-trigram pairing,
   or replace it with a grammar-defined whole-construction test plus a valid
   separate-boundary rival.  The present result cannot be called a detached
   prefix/control relation.
2. State explicitly that the exact p-value is descriptive after target-form
   exposure and prior F76 mechanism searches.  Gates cannot restore blinding.
3. Add controls for every implemented gate, especially all nine deletion
   paths, both reduced multiset sizes, above-median checks, ties, and
   degenerate-null rejection.  Current controls test only the primary plant,
   a rotation, the assignment count, and deterministic equality.
4. Bind `run_target.py` itself in `CONTROL_RESULT.json`; currently the target
   runner and its gate logic can change without making controls stale.  Bind
   the future independent validator as well.
5. Preserve the source qualification: line pairing is a human editorial
   alignment and the `r` and final `s` marks are explicitly noted as above
   baseline.  A passing score cannot upgrade this to authorial word ownership.
6. Do not add a nonimporting target validator until the estimand and rival
   mechanism are fixed.  Validating the present arithmetic would not cure the
   scientific mismatch.

## Disposition

**REVISE, not GO.**  The existing code may be retained only as a post-hoc
initial-trigram diagnostic under a sharply lowered claim.  If the intended
claim remains a detached line-opening prefix, the scorer and controls require
redesign before any target execution.  No current outcome may assign a mark
to a word class, letter, number, sound, lexeme, plaintext, or translation.
