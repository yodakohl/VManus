# GDT1171 — fixed open-vocabulary source recovery

## Decision note, before fitting

The user authorizes one actual comparison after the source capacity census.
That census's55.906% novel-occurrence ceiling applies only to reference-word
intersection. The supplied declaration relation itself covers99.944% of those
occurrences. The new question is whether a single fixed character model can
select exact expansions without a reference-word veto, and whether crossing
word boundaries adds recovery. This is not a claim that OOV items are easy.

Positive predecessors: GDT1160 has supervised context benefit with supplied
per-form inventories. GDT832/833 use character backoff in a known synthetic
architecture;833 isolates a reference spelling intervention.832's original
failure and GDT1164/1166's failures stand. GDT995 supplies only retrospective
conditional key recovery. A pure word-bigram backoff cannot reorder two OOV
words at fixed neighbors relative to its unigram backoff; it is therefore not
the proposed OOV context mechanism. Use character context across spaces.

Success permits treating this narrowly specified source instrument as useful
for finite, supplied-rule reading alternatives. Failure stops this instrument
without automatically adding models/corpora or searching for an unknown key.
Neither result chooses a Voynich language, writer or word. No current Voynich
candidate readings receive scores. The user explicitly requests this
conditional instrument test despite that limited claim scope.

Smallest adequate implementation: one character architecture, three fixed
arms, six book folds, exact dynamic programming, all selected groups and
complete source records, an independent scorer/search replay, publication.
Work estimate90min inclusive:15design/preparation,35implementation,20execution/
validation,20report/publication. Reassess at the estimate rather than broaden
the task. This is not restoration of the revoked45min session limit.

## Source and input separation

Reuse the source_rule_package's pinned six CoReMA XML books, declaration,
unchanged projector and complete-group/record mapping. Preserve case, spelling,
word group boundaries, word order, empty expansions and unknown positions.
Source values, editorial graphic classes and language knowledge are supplied.
All data and some answers were exposed previously. No analyst blinding or
independent historical confirmation. No Voynich data or reserves.

Prepare one raw-input and one OTHER-FIVE-book expanded-reference file per fold,
plus a separate answer file for later scoring. A fit/predict worker sees only
its raw input and its other-book reference; the answer file is read only after
the prediction lock. Reference unknown expansions break training segments;
unknown raw groups break held decoding segments and retain null predictions.
Record boundaries also break segments. No held expanded neighbor is supplied.
Reference gold spelling is intentionally supplied, as in the prior proposal.

Predict every projected group, including ordinary groups, using the same
declaration relation. Editorial selected labels identify evaluation panels,
not special decoding rules. Count all11,724 selected groups and204 unresolved
obligations; unknown gold is zero credit. Keep all three known mismatches.
NOVEL means the exact native group is absent from every other-book raw group,
not that its expansion or concept is novel. OOV means its exact answer is
absent from the other-book expanded reference, and is evaluation-only.

## Fixed architecture and arms

Order5 character model (four-character history), additive alpha0.1, natural
logs. Train counts for all suffix history lengths0..4. At scoring time use the
longest history with any training count, then `(count(h,c)+0.1)/
(count(h)+0.1*alphabet_size)`. No interpolation weights or fit tuning.
The per-fold alphabet is the union of reference characters, a literal space,
and all characters in legal outputs for the raw target; no held answer
characters enter it. A start sentinel is history-only, not an output.

All words emit a literal space after their complete expansion. Internal spaces
in declared outputs remain internal; evaluation retains source group ownership
and never re-splits the decoded string on spaces. No length normalization,
separate lexical frequency term or reference-word restriction.

- U: train each reference expanded group independently from four start
  sentinels; score each raw held group independently, including its final space.
- C: train reference complete known segments in original order, starting from
  four sentinels once per segment; score held segments with history continuing
  across spaces. The decoder jointly selects neighboring outputs.
- S: same as C, but shuffle whole reference groups within each segment with
  `random.Random(1171)` in fixed book/segment order. Decode real held order.
  This is one ordering diagnostic, not a calibrated null or permutation p-value.

Four previous characters do not encode general sentence grammar. Left context
cannot directly affect a differing fifth letter after four shared letters;
a differing ending may affect the following word's initial characters.
U/C differ in boundary-history counts by design. S distinguishes genuine order
from an apparent advantage due only to U/C resets.

## Exact finite search and computational contract

Each raw character emits any string from its unchanged declaration class, or
its literal identity if undeclared. Duplicate alternatives are removed; empty
outputs remain. Unknown characters produce an unresolved group, never invented
restoration. No free letters, per-word rules, candidate truncation or beam.

Dynamic programming retains maximum log score per last-four-character state
after each raw character and fixed space. U resets per group; C/S reset only
at record or unknown boundaries. Backpointers retain input group ownership.
Merge duplicate derivations by MAX, not SUM. Exact floating equality ties keep
the first path in sorted-state/sorted-alternative iteration; final ties prefer
lexicographically smallest history. This is not semantic confidence.
Abort without altering the model if a segment exceeds100,000 live states or
20million saved nodes. Complete six folds with up to6CPU workers.

## Endpoints fixed before outcomes

Primary: for each NOVEL known native type, average exact correctness over its
occurrences; average types within each book, then books equally. Report U,C,S
on the same panel. Also retain pooled occurrences, pooled type means,
all selected groups, shared forms, NOVEL-and-OOV, full source groups, complete
record correctness, empty outputs, unresolveds and candidate compatibility.
Unknown-written groups have no invented type ID and remain in all-selected
occurrence denominators. No case folding or spelling equivalence.

For a useful conditional source instrument require ALL of:
1. C primary accuracy>=70%.
2. C minus U primary>=3percentage points, with C>U in at least4/6 books.
3. C minus S primary>=2points, with C>S in at least4/6 books.
4. C novel-OOV type accuracy (same book-then-type weighting)>=50%.
These are practical selection thresholds, not significance levels or promises
of full reconstruction. Report all results even if the first gate fails.
Never rescue the run by switching primary to tokens, dropping B6, selecting
only covered strings or promoting a better-looking arm after seeing gold.

## Validation, release and provenance

Before real fitting, publish method, executable source, parameters, input
hashes and toy-validator result. Predictions and model counts are hash-locked
before answer scoring. Public preregistration prevents later protocol edits,
not prior analyst knowledge.
Fixtures check OOV outputs, zero-length emissions, probability normalization,
exact search against exhaustive enumeration, duplicate derivations, boundary
dependence and deterministic ties. A separately implemented Viterbi replay
checks actual predictions and scores; anchored regexes check rule compatibility.
Recompute training counts and metrics independently. The validator does not
import the production language model or decoder. Shared projector reuse is
disclosed and is not independent native-image collation.
