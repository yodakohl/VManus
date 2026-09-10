# GDT905 — constructive complete-passage CV hypotheses

Exploratory construction selected by the user's new explicit instruction on
10 September 2026. This is not a successful control or a translation test.
The short decision and predecessors are in `docs/joint_reading/PROPOSAL.md`.
GDT892's 12+9 control-capacity stop, all thresholds and source bytes remain.
GDT832/837 showed that high language scores can select wrong keys. Here no
fluency objective selects a winner. GDT895 assumed complete Simon entries;
this construction assumes no copied source sentence or entry.

## Fixed writing and language hypothesis

Use GDT892's unchanged `src/core.py` channel and `src/SPEC.json`: normalized
Latin spelling, six possible inherent vowels, greedy consonant-vowel syllables,
27 components, injective prefix-free component codes of length 1 or 2, one
complete written group per complete word, no nulls or exceptions. The full
cipher alphabet is always `acdefghiklmnopqrstxy`, including letters absent from
a paragraph. All 2^20 singleton masks are considered. A legal mask must allow a
complete 27-component codebook, counting unused singleton codewords too.

The unchanged 425561-form reference and complete ambiguous six-field analyses
come from the hash-bound GDT892 cache. Its fixed feature/dependency CFG must
recognize the entire decoded paragraph, allowing its registered concatenation
of complete source-rooted parses. This is a restricted Latin hypothesis, not
evidence that Voynich is Latin or that the CFG captures full Latin grammar.
No independent lemma/feature cross-product is introduced. Complete decoded
forms receive their original complete analyses. The six features do not
establish tense, voice or gender distinctions absent from that grammar.

## Fixed manuscript scope and exposure

Reuse GDT904 `intake()` unchanged: GDT888 odd physical leaf training membership,
selector-first queries of the original raw/STA/paragraph tables and exact
source parity. No even-leaf bodies, new visual page, f84 or f84r. Save the intake
as TARGET.json; then select EVERY complete paragraph containing 12 through24
raw groups inclusive. All four reading panels remain separate; consensus is
not a fourth manuscript. Report all scope exclusions as metadata. Any character
outside the fixed alphabet is a channel-domain failure, never silently removed.
Prior exposure is acknowledged. No concealed group is revealed in this pass.

Each selected complete paragraph seeds a candidate global key. The key must
apply to every group in that paragraph; independent seed keys do not establish
one shared manuscript key. No windows, word deletions, reordered groups or
locally assigned root values. Results on different paragraphs are a complete
exploratory search family, not independent confirmation of a chosen candidate.

## Exact construction and bounded search

First use the unchanged GDT892 mask scanner to enumerate every segmentation
whose complete-word equality patterns have lexical realizations for an inherent
vowel and whose union of codewords allows 27-component completion. This is a
necessary relaxation: different words may use incompatible local component
values here. Save every surviving mask and vowel bitset. A zero mask list proves
that this complete paragraph cannot fit the full fixed model.

For each surviving actual segmentation, solve the finite table CSP over observed
codeword-to-component assignments, injectively shared by all complete words.
Equivalent masks on observed words may be grouped; retain their full masks in
the artifact. Each complete assignment decodes uniquely for an inherent vowel.
Accept it only if all words belong to the fixed lexicon AND the full CFG accepts
their complete tag lattice. Record its explicit observed key, deterministic
completion to all27 components, entire plaintext, source groups and analyses.
Unobserved completion values are arbitrary representatives, not recovered rules.

Source compilation, scanner and CSP code are reused unchanged. New orchestration
only connects whole-paragraph tables to complete CFG acceptance. No optimization
objective, higher score, manual reading choice or post-result model repair.
Keep all accepted observed assignments encountered, including multiple readings
with the same plaintext. A complete search permits reporting the full set;
incomplete search permits only explicit witnesses and UNKNOWN, never uniqueness.

Budget: decision 05:50UTC, total40min through06:30UTC including publication.
First target scan by06:02UTC; all search stops by06:17UTC. Scanner timeout60s
per paragraph; exact CSP at most20s per paragraph across all segmentations/vowels,
and at most64 accepted observed keys per paragraph. Hitting either limit is
UNKNOWN_BUDGET / UNKNOWN_WITNESS_LIMIT. Source-order paragraph IDs, alphabetical
reading order, masks and vowels define deterministic traversal; clocks affect
only explicitly incomplete cases. No unseen data used to rank alternatives.

## Claims and validation

A fully explicit grammatical plaintext is a conditional candidate, not a
confirmed word or passage. It can motivate a separately fixed consequence test
only after its remaining ambiguities and evidence route are assessed. This pass
does not open held data, run semantic scores or waive GDT388/CDA001 gates.
Zero domains stop this construction scope; unknowns stop optimization. No larger
lexicon, changed grammar, word length, channel or automatic decoder successor.

Independent validation recomputes the six source pattern indexes using a
separate CV encoder; segmentation/mask impossibility via per-word local-mask
truth tables; codebook legality and full witness reencoding; and CFG acceptance
with an independent bottom-up recognizer. Software validation does not establish
the language or code hypothesis. Publish all outcomes, not only witnesses.
