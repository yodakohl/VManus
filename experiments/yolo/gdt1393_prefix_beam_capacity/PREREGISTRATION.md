# GDT1393 — necessary prefix capacity before a new decoder

Selected 2026-10-16 before computing any of the six retained prefix sets or
comparing control plaintexts. This is a retrospective control-method decision,
not a Voynich experiment or fresh blind recovery.

## Decision note

GDT1390 failed all twelve complete positive controls, although every true key
scored above the returned winner under the same normalized likelihood. More
starts are not selected. A genuinely different candidate would search source
characters sequentially, maintaining the exact affine key fiber modulo27,
then rescore complete candidates with the unchanged1390 likelihood.

The preceding C1064_PREFIX_RANK diagnostic computes the exact prefix image of
all eighteen public control matrices. All first ten positions allow all27
characters. Constraints begin at positions11–21; the early-prefix problem is
therefore real, but the earlier suggestion of23 completely free initial
characters was too strong. This diagnostic did not inspect control truth.

The unknown is whether a practically bounded source-prior beam would already
discard known correct prefixes before the first cipher restriction. The
smallest adequate test is to construct those first ten steps only. A failure
avoids implementing a complete decoder. Passing allows only a separately
registered full recovery test; it is not permission to decode native passages.

Inclusive budget: 08:46–09:40 UTC on2026-10-16, including the preceding rank
diagnostic, preparation, implementation, validation and publication. No larger
beam, alternative ranking, extra source model or decoder repair follows a
failure within this experiment.

## Fixed proposed search and necessary gate

Keep one independent forward beam for each of the six unchanged1390 order3
character models. Source alphabet remains SPACE=0,a..z=1..26. Each starts with
the empty prefix at score0. At every step expand all27 next characters and
retain at most65,536 prefixes, ordered by decreasing cumulative source-model
log probability, then lexicographically by their fixed-length residue sequence.
Use the original shorter context at positions1–3 and the original order3
context thereafter. Do not switch source components within a prefix.

The contemplated full search keeps these six beams separately throughout;
there is no revisiting of discarded prefixes, future-aware score, adaptive
width, beam merger, corpus lookup, crib, null symbol or supplied source word.
Complete-message source-mixture and exact packet normalization would be used
only to rank surviving complete candidates. They cannot restore a prefix
discarded by this specified algorithm. This is a proposal search, not an
exact maximum-likelihood algorithm.

Compute the six source-only beams through exactly ten characters. The control
matrix diagnostic is independently checked: the first ten modular image
increments are all27. These same unrestricted prefix sets are therefore the
specified search's initial sets for every case. Do not infer this equivalence
for a different algorithm with early channel scoring or other restrictions.

Freeze the six final sets, their per-step counts and hashes, model/source/code
hashes and a timestamp before opening the old truth for this computation.
Runtime arrays may remain outside the public tree; publish sufficient source,
fixed model pointers and compact hashes/results to reproduce them exactly.

Then compare the exact first ten source characters of all eighteen old1390
controls against each set and their union. Primary necessary gate: all twelve
positive prefixes must survive in at least one component beam. A missing
positive prefix proves that this fixed search cannot meet the unchanged
all-twelve complete-message recovery gate. No full solver is implemented or
run after such a failure. Retain all negative-control results descriptively;
survival is not readability, recovery or a false-positive rate.

## Exposure, assumptions and dependencies

- Cases and truth were previously public and examined during1390. A new output
  lock prevents outcome-driven changes in this computation; it does not erase
  historical exposure or create independent validation data.
- All source models, initial-state framing, working-unit count convention,
  mixture definition and valid-key condition are inherited assumptions.
  The diagnostic's affine equations relax the valid-key restriction; it is
  not a historical writer identification or a recovered plaintext.
- A surjective key must have at least one of its22 glyph weights nonzero
  modulo3; the offset does not satisfy that condition. At ten independent
  prefix equations the modulo3 kernel has dimension13, so it cannot vary
  only the offset. Valid-key feasibility does not remove a first-ten prefix.
- First-ten retention is only a necessary condition. It does not establish
  later survival, model adequacy, key identifiability or native applicability.
- GDT1390's failure, GDT1324's limited toy recovery, and GDT602/604's warning
  about language-model pseudotext remain unchanged.
- No native text, image, new source corpus or reserve is inspected. f84 and
  f84r remain sealed; f116v, f1r bodies and GDT327/GDT336 remain unadmitted.
  No Voynich word meaning is assigned.

## Verification

An independent implementation recomputes all six beams using a different
selection procedure, verifies the source-table context convention and exact
tie order, and checks small exhaustive fixtures. It separately verifies the
first-ten matrix freedoms from the public packet arrays and compares the
released truth only after the prefix-set lock. Any arithmetic/implementation
correction must retain the original source and explicitly record its reason.
