# Inverse historical writing channel: decision before implementation

Date: 2026-10-03. Status: **DO_NOT_IMPLEMENT_WITHOUT_A_TARGET_IDENTIFICATION_TASK**.
Source-only proposal review; no target fit, new source-payload evaluation,
Voynich access, or word assignment. This is not a registered experiment.

## Decision

The authentic abbreviation calibration below is technically feasible, but is
not selected now. Success would show that a supervised historical writing
channel can recover expanded identities in another book of the same source
collection. Voynich currently supplies neither those paired training identities
nor an established correspondence to this channel. Success and failure
therefore leave the immediate Voynich decision unchanged: do not normalize
similar forms to one meaning or fit an unconstrained decoder.

This corrects the initial suggestion that a successful source calibration alone
would justify target canonical-family inference. It would not. A useful control
can still be premature research work when its proposed target inference lacks
the control's identifying inputs.

## Existing evidence actually checked

* GDT157 learned expanded-to-diplomatic generation on four held Nuremberg books:
  436,572 aligned groups, 84.154% MAP accuracy versus 72.829% unchanged baseline.
  Some surface features were generated, but abbreviation did not explain the
  full Voynich operation breadth, direction or reset pattern. This is a forward
  channel result, not inverse canonical-identity recovery.
* GDT832: continuous context recovered all eight synthetic wholeword values;
  the family term added no recovery. Original CONTROL_RECOVERY_FAIL remains.
  Reference spelling mismatch and an incorrect key outscoring truth are known
  counterexamples to interpreting language-model preference as correctness.
* GDT837: all selected synthetic keys recovered letters and wholewords but
  misread one suffix; original STRICT_RECOVERY_FAIL remains. Supplied role and
  word boundaries are not discovered Voynich properties.
* GDT995: full deterministic forward compatibility repaired 45 of 48 frozen
  near-correct synthetic maps conditionally, with literal/role/wholeword maps
  fixed. The inverse identified the suffix set, not its carrier permutation;
  the unchanged language score selected the permutation. This is neither fresh
  full-key recovery nor a historical optional-abbreviation model.
* GDT605/608: recurrent units and directed component backoff are real formal
  information, but unit inventory is not an alphabet. Exact merged identity
  retains residual information; `ol/or`, `ok/ot`, and standalone behavior block
  free component stripping.
* GDT915/916: known phrase co-variation transfers, but unseen licensed stem-pair
  concordance is not established. Do not impose productive agreement.
* GDT276/609 already compare operational writing architectures and design a
  contextual abbreviation FST. GDT207 does not authorize a flexible inverse
  transducer. GDT394 rejects privileged latent-role compression over matched
  generic alternatives; GDT611 retains concrete lexical permutation ambiguity.
  GDT616's original failed decision remains unchanged.

Claim-bearing primaries are the corresponding REPORT.md files returned by
`vmanus-work lookup`; historical root reports are
`GDT157_LEARNED_ABBREVIATION_CAUSAL_REPORT.md`,
`GDT207_DIPLOMATIC_ABBREVIATION_LANGUAGE_SCREEN_REPORT.md`, and
`GDT276_RESIDUAL_CHANNEL_WORLD_COMPARISON_REPORT.md`.

## Available source and parser, without opening payloads

All three source files exist; only their header lines were read in this review:

| File | Useful columns |
|---|---|
| `gdt155_blinded_diplomatic.tsv` | corpus, book_or_ms, page_id, line_id, writer_id, diplomatic_marked, record_id, line_index |
| `gdt155_unblinded_lines.tsv` | corpus, book_or_ms, record_id, line_id, expanded_diplomatic |
| `gdt155_unblinded_record_truth.tsv` | corpus, book_or_ms, record_id, expanded_diplomatic_record and regularized content fields |

The regularized content/addressee fields are unnecessary and must not become
candidate hints. Read only NUREMBERG source data under a future fixed contract.
The existing GDT157 parser, `run_gdt157_learned_abbreviation_causal.py:489-517`,
joins by line_id, applies its existing group functions, removes the historical
abbreviation marker from observed forms, and pairs groups only for equal-count
lines. It asserts 45 excluded unequal-count lines and four fixed book IDs.
These historical exclusions must be retained and reported, not silently
repaired. Marker removal and token boundaries are supplied conventions.

GDT157's Channel learns training-only exact lexical realizations plus aligned
character emissions with context backoff. Its generate method produces a MAP
or sampled forward realization; it is not a normalized inverse scorer and
cannot be advertised as one without a separately specified likelihood.

## Smallest retained design, if a concrete target task is later identified

Question: can historical spelling transformations plus observable diplomatic
context recover an unseen written variant's expanded identity better than
either source alone? No transformer or new corpus is needed.

1. Keep the four leave-one-book-out partitions. Fit all dictionaries, edits,
   context tables, smoothing and candidate cutoffs using only the other books.
   Candidate identities are the complete TRAIN expanded vocabulary plus UNK;
   never add the held truth, a gold lemma, or gold expanded neighbors.
2. Learn an explicit probabilistic character edit channel from TRAIN aligned
   expanded/diplomatic pairs, with fixed deterministic edit alignment and fixed
   short-context backoff. Identity operations and unobserved-character escape
   probabilities must be nonzero and normalized. Rank every candidate by the
   likelihood of the actual diplomatic form; do not require the MAP generated
   spelling to equal it. Full candidate enumeration avoids an oracle shortlist.
3. Compare three fixed models: (A) exact written-form counts plus expanded
   frequency/context backoff, (B) edit-channel likelihood plus expanded
   frequency, (C) the same edit channel plus TRAIN-learned immediate observed
   diplomatic-neighbor likelihoods. The latter are conditioned on candidate
   expanded identity, with count backoff; test neighbors stay written forms.
   Hold the word-context contribution and smoothing fixed before evaluation;
   no held spelling or truth-driven retuning.
4. Predict every eligible held group before revealing its expanded identity.
   Evaluate overall and on the predeclared subset: actually abbreviated held
   forms unseen as diplomatic types in TRAIN, whose expanded type is known in
   TRAIN through a different written form. Truth defines the scored subset only
   after predictions; it must not change candidates or rankings. Report zero
   capacity honestly, rather than weakening unseen-variant criteria.
5. Report per-book exact identity accuracy, rank and normalized log loss,
   candidate coverage/UNK, unchanged forms, seen variants and unseen underlying
   lexemes separately. A positive method result requires C to beat both A and B
   on the designated abbreviated unseen-variant subset in each supported book,
   and preserve full-population performance. No significance claim is needed.
   A context-permuted diagnostic must rerun the identical complete procedure;
   it does not calibrate the whole project search.

This is supervised source-channel generalization. An unsupervised Voynich
version would constitute a materially different identification problem, not
the same model with a different input file.

## Outcome-to-action table

| Outcome | What it permits | What it does not permit |
|---|---|---|
| Contextual channel wins | Retain a tested ranking component for a future task with independently justified candidate identities and channel training evidence | No Voynich family collapse, German/Latin identification, abbreviation claim, assigned meaning or target decoder |
| Edit-only wins | Prefer the smaller source ranking component in such a future task | No proof that visual/edit neighbors share Voynich meanings |
| Whole-form wins or recovery fails | Do not build the proposed contextual inverse method from these assumptions | No refutation of all historical abbreviation or semantic text |
| Subset has insufficient support | Record missing source capacity if the experiment was selected | No relaxation of the subset or substitute favorable cases |

Without a common-content anchor, success supplies **no new manuscript inference**.
It cannot distinguish a shared underlying meaning from content-dependent
orthography, formula reuse, local copying, or an arbitrary latent codebook.
The immediate target action is thus the same across outcomes; implementation
is not justified at present.

## Target dependency and physical-layout alternative

A useful reopening input would be an independently supported repeated target
content identity under contrasting writing conditions, or a specific target
prediction whose candidate identities and writing law can be constrained
without assuming the desired translation. Neither was established by this
review. GDT829's zero exact reflow-context capacity and GDT1154's nonconfirming
paragraph-order comparison must not be repaired by shortening contexts.

DIC001 drawing interruptions provide a real formal contrast, but are not an
exogenous experiment holding content constant. Their comparator is consecutive
below-locus transitions, not known paragraph resets. The post-confirmation
right-initial residual alone did not pass its descriptive threshold. A new
physical-edge transfer test may assess a writing-context mechanism without
this inverse calibration; it would not justify interpreting variants as the
same lexical item. Keep GDT800's many nonfinal-m/final-l counterexamples.

## Budget and stop

This source-only decision review is bounded to ten minutes and writes no code.
Current implementation budget: zero. If the target dependency is later met,
the smallest comparison above should receive one separately registered budget
covering preparation, fitting, independent validation and publication, rather
than an open chain of control or decoder repairs. No experiments were executed
or existing conclusions overwritten in this review.
