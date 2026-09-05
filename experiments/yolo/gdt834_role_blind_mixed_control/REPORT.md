# GDT834 — roles recovered; two word values defeat the paired control

Status: **BASELINE_RECOVERY_FAIL**.

Both TYPED and BLIND recover 6,343 of 6,511 held words (97.4198%) and every
novel composed form/lemma occurrence, but miss the registered 99% character
floor. BLIND identifies all 35 observed symbol roles correctly. The remaining
two errors are wholeword values: true `ut` is decoded as `quod`, and true
`quod` as `cum`. All six selected keys have this same observed mapping and
held output. Missing role labels do not account for the errors in this panel.

A post-result census finds that **21 of the 48 existing restarts already
recover the complete observed true role/value mapping** (11 BLIND, 10 TYPED).
The other 27 recover the selected wrong mapping; there is no third observed
mapping class. The right answer was present in the frozen candidate panel.
The wrong selected keys score **3.5004736600 nats above the true key** on
discovery text. Greater optimization cannot make truth the global winner
under this fixed objective. This is a small observed misranking on one source
split, not a universal failure of probabilistic language models.

## Fixed test and scope

Public preregistration `1daf02ee1bf5bc74db9b1dbb5f86ec208bafa0a7` was pushed
before every fit. Fresh Epistolae I–VI supply 87 discovery citation runs / 3,180
words; VII–XIII supply 172 held runs / 6,511 words. Source-only capacity passed
without a changed split, deck, threshold, reference or discarded rare words.
The independent validator reconstructs all 259 runs, 376 sentences and 9,691
original normalized words. The 19,162-word native Monarchia reference,
candidate pools and encoder value decks are unchanged from GDT833.

TYPED and BLIND share the same source content and value key. BLIND receives a
separately shuffled X00–X37 inventory; its C++ process gets only its anonymous
discovery projection and reference model. Word/paragraph boundaries, atomic
units, positional rules and nominal 26L/4S/8W capacities remain supplied.
The wrapper checks aggregate capacity status but forwards no active-role counts.
A code/input review found no transfer of typed mappings or solutions into BLIND.
Blinding is procedural, not a security claim about public deterministic seeds.

Position alone forces 24 observed literals. Both the prospective fresh audit
and the separately marked retrospective GDT833 audit leave 67 observable role
partitions, or 219 after counting unused-slot completions. This is a small
finite disambiguation problem, not general segmentation or role induction.

## Original-spelling held results

Every row below applies identically to both arms and each of the three keys.
Those keys share one historical content split, not three independent texts.

| Metric | Result | Registered floor |
|---|---:|---:|
| Exact words | 6,343 / 6,511 = 97.4198% | 95% |
| Character similarity | 98.6575%; 504 edits / 37,542 denominator | 99% — fails |
| Exact novel composed form occurrences | 3,160 / 3,160 | 90% |
| Exact novel composed lemma occurrences | 1,977 / 1,977 | 90% |
| Exact complete held paragraphs | 79 / 172 | secondary |
| Active role identity | 35 / 35 | secondary, BLIND role component |
| Active literal role + value | 24 / 24 | BLIND requires exact identifiable values |
| Active suffix role + value | 3 / 3 | same |
| Active wholeword role + value | 6 / 8 | same — fails |

All 35 observed roles are identifiable when observed emissions are held
fixed; no same-emission role ambiguity occurs on these data. The three unused
slots are unscored throughout. Hence correct roles alone do not satisfy the
registered BLIND requirement of exact identifiable **role plus output**.

The 168 wrong held words are 59 occurrences of `ut→quod` and 109 of
`quod→cum`; corresponding discovery supports are 25 and 17. No original-spelling
normalization, selected-key replacement or recovery threshold adjustment follows
this result. The exact macro error audit is explicitly post-result and outside
the frozen fitting protocol; it creates no new fit or score. A second audit
independently confirms the 21/27 restart classes and every error count; all 59
protected primary/fit files remain unchanged across diagnostic replay.

## Objective and validation

True-key discovery objective: −47,086.06465938922 nats. Selected wrong-key
objective: −47,082.56418572922. The same 3.5004736600-nat advantage appears in
both arms for all three keys. All literal/suffix readings and every novel
composed held word are correct; the residual error is word-value discrimination
in this language objective. There is no observed extra role-hiding penalty.

All 48 restarts and six discovery selections were fixed before truth access.
FIT_LOCK SHA-256:
`9e91fa0af401d4777e9af6cec9955957d438fc9ee0909b2e1e4785e385eec872`.
Ten meaningful toy tests pass. The independent full validator and exact replay
pass: 48 discovery objectives, six selected fits, 39,066 held word predictions,
six true-key oracle scores and 210 active role domains checked by independent
max-flow. Its implementation imports neither the fitter, generator nor evaluator
for independent arithmetic; the reference-model probabilities are frozen and
shared. Result and validation artifacts remain distinct scientific statements.

## Interpretation and route

The paired recovery test fails because even its typed baseline misses the
character floor. Within this control, the missing role labels are successfully
resolved. Correct role identities do not supply correct word meanings: the
proper language score still prefers two wrong function-word values. The search
already found the right observed key in both arms for every source key;
post-truth selection of those 21 restarts would be a rescue, not the registered
outcome. The decisive remaining issue here is selecting the right reading.

This is no Voynich fit, language identification or translation. The architecture,
atomic units and boundaries are still supplied, and the 67-way ambiguity is
limited. GDT833's success, GDT832's failure, GDT616 and CDA001 remain unchanged.
Do not rerun this fixed objective/deck/split or hide the error by selecting a
lower-scoring key after truth. No next fit is selected; any successor must first
supply a genuinely different predeclared discriminator for word values.

Source, preregistration, fits, original truth, compact results, independent
validator and the separately marked diagnostic are published together. See
REPRODUCE.md for verification without optimization or a fresh frozen fit run.

Publication checks cover the exact staged privacy/scope tree and GDT834 bindings.
The separate global check retains unrelated GDT600 binding and index debt; it
is not reported as passing or repaired by this experiment.
