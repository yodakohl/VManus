# DANI001 fixed-mapping diagnostic specification

Status: **REGISTERED_POSTSELECTION_DIAGNOSTIC_UNSCORED**
Date: 2026-08-10

## Question and hard ceiling

The current DANI deposit fixes an EVA-to-consonant reduction and a curated
1,389-key lookup lexicon. DANI001 asks one deliberately narrower question:

> On complete manual source groups from ZL3b, IT2a, and RF1b, how exceptional
> is membership produced by that exact fixed reduction and lexicon among all
> 10! bijections of its ten core consonants?

This is a post-selection diagnostic. The DANI author saw the manuscript while
choosing the mapping, vowel deletion, compound rules, filters, affix rules,
lexicon, and domains. Permuting only the final ten core assignments does not
cover that adaptive search. ZL3b, IT2a, and RF1b are alternate readings of one
manuscript, never replications or held texts. Therefore no outcome can establish
Syriac, Aramaic, Semitic language, pharmaceutical content, a phonetic alphabet,
a Voynich lexeme, plaintext, or translation.

A strong outcome establishes at most this conditional fact: the released
reduction produces unusually high membership in its own released lookup set,
relative to other assignments inside the released ten-character family, and
the effect is or is not robust to source-group, type, concentration, and
deposited-metadata controls. No length-generalization claim is tested.

## Frozen inputs

Local human transcription evidence:

- `transcription/sources/ZL3b-n.txt`, SHA-256
  `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`
- `transcription/sources/IT2a-n.txt`, SHA-256
  `7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5`
- `transcription/sources/RF1b-e.txt`, SHA-256
  `e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782`
- `results/source_separator_transcription.tsv`, SHA-256
  `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`
- `results/source_separator_transcription_validation.json`, SHA-256
  `8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb`

The separator atlas contains 115,470 source groups in 15,985 source rows and
four manual separator states. Its independent validation has 2,771,299 checks.
The runner may consume the three raw sources, atlas, and validation. Both the
runner and clean validator must independently reconstruct the same groups from
the raw sources before any score.
No formal root, role, grammar, OCR, image, or automated-vision field is allowed.

External fixed evidence:

- Zenodo concept endpoint `https://zenodo.org/api/records/19583305`, whose
  current stable projection identifies revision 4 / record 19609475, SHA-256
  `780301fd3c4b2c3c328c1f69a1eab65d0b0600f2d491ea9578f81699d36ddfa7`
- `lexicon_v31_session31_final.json`, SHA-256
  `348992fa2bf555f1454a5a5485dd1ca9842acc143059f257f2fcdcf237821589`
- `pipeline_v31_1.py`, SHA-256
  `079b6de7b8d2082303a0789fb3904105aecaa491e35600a557090e7981255d6f`

The only permitted acquisition endpoints are the concept URL above,
`https://zenodo.org/api/records/19609475/files/pipeline_v31_1.py/content`, and
`https://zenodo.org/api/records/19609475/files/lexicon_v31_session31_final.json/content`.
Acquisition occurs before repository read isolation is installed, stores the
two downloaded bodies only in a fresh external temporary directory, verifies
their SHA-256 values before parsing, and deletes the directory after the run.
The stable metadata projection is canonical JSON containing only immutable
record/version/file fields; live view and download statistics are excluded.
Network or hash failure is an output-free stop. Neither downloaded body is
committed. The target freeze binds the acquisition/projection source and the
exact canonical stable-projection bytes as well as the hashes above.

The external pipeline is inspected as inert text only and is never imported or
executed. The lexicon's Syriac spellings and English meanings must never enter
a statistic, output, diagnostic example, or report. Only its exact keys and the
boolean presence of a nonempty `source`, plus the exact `domain` tag, may be
read. Each domain must be a string in
`{astro,botanical,function,general,medical,pharma}` or missing/empty, which is
canonicalized to `missing`; any other type or value hard-stops. Source strings,
Syriac spellings, meanings, and vowel hints are discarded immediately after
their permitted booleans/tags are projected and are forbidden from every
persisted or diagnostic object.

## Frozen parser panels and normalization

Parse the raw IVTFF sources minimally using the frozen source-atlas rules:
page metadata, locus rows, and the four manual separator states. Each
nonnested complete square form `[primary:alternate...]`, processed
left-to-right, is replaced by the bytes after `[` and before the first `:` (or
before `]` when no colon occurs). A complete `{...}`
or non-separator `<...>` form is deleted. Unmatched or nested square, brace, or
angle delimiters hard-stop. Reconstruct the source-separator atlas byte for byte:
15,985 source rows, 115,470 groups, and 99,485 manual boundaries. Do not use the
2,714 legacy cleaner-created fragment boundaries.

Freeze two panels before scoring:

- `DOT_ONLY_EMULATION`: within each locus, split only at definite `.` separators.
  Concatenate, with no inserted byte, the complete adjacent raw source groups
  across comma, `<->`, and `<~>` separators; then apply alternative selection
  and annotation deletion to the joined token. This applies the released
  dot-only splitting mechanics to the three public manual readings. It does
  not reproduce the missing `lsi_all.txt`, its H-only row selection, or its
  headline corpus.
- `MANUAL_GROUP`: every one of the four human separator states is a boundary;
  each of the 115,470 source groups remains indivisible, and alternative
  selection and annotation deletion are applied to that one raw group.

For each panel token:

1. apply the exact primary-branch and annotation rules above, then lowercase;
2. define `normalized_eva` by retaining only ASCII `a`--`z` characters;
3. exclude it when `len(normalized_eva) < 2`;
4. scan left to right, choosing the longest registered three-character, then
   two-character, then one-character atom;
5. skip an unregistered character exactly as the deposited code does;
6. exclude an empty output atom sequence.

Add a `STRICT_LITERAL` sensitivity. It excludes a panel token if any constituent
raw source group contained `[` or `{` before normalization, or if any character
of its post-annotation `normalized_eva` is not completely consumed by the
released longest-first scanner. Thus ambiguity propagates across a joined
`DOT_ONLY_EMULATION` token. Complete non-separator angle annotations are
deleted but do not by themselves trigger `STRICT_LITERAL`; unmatched/nested
angles already hard-stop. The score-blind source audit expects only 280
length-eligible manual groups across all readings with an unconsumed scanner
character; the calibration must freeze the exact reconstructed count before
scoring.

Types are exact `normalized_eva` strings. Admit only rows whose page matches
`^f[0-9]+[rv][0-9]*$`; this is also the deposited parser's page domain. The
compound pseudo-page `fRos` is therefore excluded from every numerator and
denominator, not merely from folio gates. This removes exactly 1,083 atlas
groups in 320 edition-locus rows / 160 physical locus names, all in ZL3b or
RF1b, and retains 114,387 atlas groups in 15,665 edition-locus rows. Any drift
hard-stops. A physical folio is the integer from
the leading `fNN`, so recto, verso, and numbered foldout panels share one folio.
The validator must reproduce every panel token/template digest from the raw
sources without importing the runner.

## Fixed reduction

Core inputs, in fixed order:

`(k, d, r, s, l, n, q, y, m, g)`

Core outputs, in the released-map order:

`(k, d, r, s, l, n, w, y, m, g)`

The observed released assignment is the identity permutation of those two
ordered tuples. Enumerate all 3,628,800 permutations of output indices
lexicographically, starting with identity. Every permutation is included.

Fixed non-core rules are copied exactly from the deposited pipeline:

- `sh->š`, `ch->k`;
- `cth->ṭk`, `ckh->kk`, `cph->pk`, `cfh->pk`;
- `t->ṭ`, `p->p`, `f->ṣ`;
- `a,o,e,i,x,h` emit nothing.

Use this exact nibble codebook in order:
`k:1,d:2,r:3,s:4,l:5,n:6,w:7,y:8,m:9,g:10,š:11,ṭ:12,p:13,ṣ:14`;
zero is padding. For code-point sequence `s[0:L]`, `0<=L<=10`, encode
`uint64(L << 40) | sum(uint64(code(s[i])) << (4*i) for i=0..L-1)`.
The first symbol is therefore the least-significant nibble, length occupies
bits 40--43, bits 44--63 are zero, and serialized integers are little-endian
`<u8`. Reject an unknown output symbol, nonzero reserved bit, padding inside
the declared length, or any value outside unsigned 64-bit range.

For one lexicon key `K`, the complete binary accepted-preimage union is exactly
`K`, `gp+K`, `gp+sp+K`, `sp+K`, and `K+yn`, for every
`gp in (ṭ,p,ṣ)` and `sp in (d,l,w)`, subject to the released nonempty-remainder
conditions. Binary coverage is unaffected by the deposited first-match label,
but the direct implementation must retain that exact decision order. Before
encoding, classify a key as reachable exactly when every code point is in the
14-symbol codebook. The 570 unreachable keys remain counted metadata but are
never passed to the encoder; adding or removing them must be score-vector
invariant. Before any source panel is accessed, enumerate and deduplicate the
preimage union for every reachable key in every frozen lexicon view and assert
that every accepted preimage has at most ten Unicode code points. Encode only
mapped token skeletons of length at most ten.
Longer token templates remain in every denominator and are fixed unmatched
under all permutations; an overlength accepted preimage hard-stops rather than
being silently lost.

## Lookup sets and match modes

Frozen lexicon subsets and invariants:

- `FULL`: all 1,389 deposited keys;
- `REACHABLE`: the 819 keys made only from the released emission alphabet;
- `SOURCE_PRESENT`: the 104 keys having at least one entry with a nonempty
  `source` (55 are reachable);
- `STRICT_NO_FUNCTION`: keys for which every deposited entry has
  `domain != "function"` (1,243 keys; 738 reachable);
- six leave-one-domain-out views formed by deleting entries tagged `astro`,
  `botanical`, `function`, `general`, `medical`, or `pharma`, retaining a key
  only while at least one other entry remains.

Report the exact number of keys and reachable keys in each set. Removing the
570 unreachable keys must leave every permutation score byte-identical. `source` and
`domain` are provenance labels supplied by the external author; DANI001 does
not validate their truth or interpret their meanings.

Frozen match modes:

- `DIRECT`: mapped skeleton is exactly a key;
- `DEPOSITED_AFFIX`: reproduce the deposited decision order: direct; strip
  one gallows prefix from `(ṭ,p,ṣ)`; strip gallows plus one standard prefix
  from `(d,l,w)`; strip one standard prefix; strip suffix `yn`.

For binary coverage the implementation may pre-expand the exact accepted
preimage sets, but it must prove byte-for-byte equivalence to the deposited
decision order on every synthetic control and, for actual normalized templates,
on nonidentity ranks during capacity. Rank-0 equivalence on actual templates is
checked only inside the authorized one-shot observed run.

## Capacity gate and exhaustive primary statistic

Synthetic-only controls may enumerate every rank of their synthetic universe,
including synthetic rank 0. The target-blind calibration must not evaluate,
store, return, or call the rank-0 score of an actual source-panel template. For
actual capacity it evaluates ranks 1 through 3,628,799 only.
A normalized type is *permutation-variable* for one frozen lexicon/match view
when its nonidentity match count `c=sum(indicator(rank), rank=1..3,628,799)`
satisfies `0<c<3,628,799`; rank 0 is neither evaluated nor inferred.
A capacity folio contains at least one eligible occurrence of such a type.
For every edition/panel/view, all three component vectors (token, type, and
equal-folio coverage) must have finite positive population SD over the
nonidentity ranks before a z score for that view is defined.

The mandatory `FULL/DEPOSITED_AFFIX` primary requires at least 100 variable
types and 20 capacity folios in every edition/panel. Failure stops as
`STOP_UNPOWERED_BEFORE_RELEASED_MAP_SCORE`. The mandatory `DIRECT_ONLY`,
`STRICT_NO_FUNCTION`, and `STRICT_LITERAL` views use the same 100/20 rule;
the top-20-deleted view uses 80/20. If the primary is powered but any of these
mandatory robustness views is not, no z score is computed for that view and
its robustness gate is false. `SOURCE_PRESENT` and leave-one-domain-out views
instead use their explicitly lower/conditional capacity rules below and may be
`INSUFFICIENT`. Only after a hash-bound calibration and capacity PASS may the
one-shot target runner enumerate rank 0 and compute the released score.

For every one of the 10! permutations, edition, and panel compute under
`FULL / DEPOSITED_AFFIX`:

1. eligible-token coverage;
2. unique normalized-type coverage;
3. physical-folio-balanced mean coverage: within each eligible physical folio
   divide matched eligible tokens by all eligible tokens, then average those
   ratios over eligible folios in ascending integer folio order.

Standardize every component against its complete 10! distribution using the
population mean and SD. The single primary score is

`T(permutation) = minimum z over 3 readings x 2 panels x 3 weightings`.

This applies one map jointly while treating readings as deterministic
sensitivity surfaces, not samples. The exact inclusive conditional tail is
`#{permutation: T(permutation) >= T(released)} / 3,628,800`; there is no plus
one. This tail is conditional on the author-selected mechanics and must not be
called a confirmatory p-value for Syriac.

Store for every raw component and for `T`: observed numerator/denominator or
floating score, exact minimum/maximum/mean/population-SD, median, strict-better
count, tie count, inclusive count/fraction, and a SHA-256 digest of the full
score vector in frozen permutation order. Store no favorable identity.

Token/type vectors are unsigned integer numerators with fixed denominators.
Their means, population SDs, medians, z vectors, and `T` contributions are
computed directly from those integer numerators converted exactly to binary64;
they are not recomputed from per-rank divided coverages. For the absolute
coverage gate, compute `(released_numerator - median_numerator) / denominator`
in that exact subtraction-then-division order.
Folio vectors and standardized vectors are IEEE-754 binary64, round-to-nearest,
with compiler fast-math and contraction disabled. In ascending integer folio order,
each folio coverage is one integer numerator divided by its fixed integer
denominator; their equal-folio mean uses a sequential Neumaier sum followed by
one division by the folio count. Distribution means use `math.fsum(values)/N`;
population variances use a second `math.fsum((x-mean)**2 for x in values)/N`;
SD uses `math.sqrt`. A median sorts by numeric value; for even N it is
`(lower + upper) / 2.0` in that operation order. Each z is
`(value - mean) / SD`; `T` takes the first minimum in the fixed component order
edition `ZL3b,IT2a,RF1b`, panel `DOT_ONLY_EMULATION,MANUAL_GROUP`, weighting
`TOKEN,TYPE,FOLIO`. Serialize vector digests as little-endian contiguous `<u4`
or `<f8`; any integer numerator outside `[0,2**32-1]` hard-stops before casting.
The target freeze binds CPython 3.12.3 on little-endian IEEE-754
x86-64; the compiled layer emits integer vectors only. The independent
validator must reproduce every raw and standardized vector digest exactly and
all separately recomputed displayed scalars within `1e-15`; comparisons and
ties use stored binary64 values with no tolerance.

## Primary robustness and concentration gates

Primary-core gates are items 1--3. A full all-gates pass additionally requires
items 4--7 and the mechanics ablations below:

1. exact joint inclusive conditional tail <= 0.001;
2. `T(released) >= 3.0`;
3. every one of the 18 raw coverage components is at least +0.020 absolute above its
   complete-permutation median;
4. separately in every edition/panel, at least 60% of eligible physical folios
   have positive released-minus-null-median advantage;
5. separately in every edition/panel, the largest folio contributes <=10% and
   the top five folios <=25% of total positive excess;
6. deleting the 20 most frequent exact normalized surface types separately
   within every edition/panel retains joint inclusive tail <=0.01 and `T>=2.0`;
7. `STRICT_LITERAL` retains joint inclusive tail <=0.01 and `T>=2.0`.

For gates 4 and 5, form the complete 10! coverage vector separately for every
eligible physical folio under `FULL/DEPOSITED_AFFIX`, with coverage equal to
matched eligible token instances divided by all eligible token instances in
that folio. Its null median uses the same frozen median rule. Folio advantage is
released folio coverage minus that
median. Gate 4 counts strictly positive advantages. Gate 5 defines contribution
as `max(0, advantage)`; its shares divide by the sum of positive contributions.
Zero total positive contribution fails both gates. Sort shares descending and
compare the largest and sum of first five; fewer than five folios is already a
capacity failure. These gates are separate per edition/panel and never pool
readings or panels. No favorable Voynich form, lexicon key, Syriac form,
English meaning, folio ID, or per-folio vector may be serialized.

For gate 6, rank types separately within each edition/panel by eligible token
frequency descending, breaking ties by the UTF-8 bytes of `normalized_eva`
ascending, and delete exactly the first 20. The deletion list and its digest
remain private runtime state; output only its count and the resulting aggregate
vector digests.

Top-20 deletion and `STRICT_LITERAL` each rebuild from scratch all 18 complete
10! component vectors, their means, population SDs, medians, z vectors, `T`
vector, tail, and concentration summaries. They never reuse primary
standardization constants. Every other mechanics/lexicon view likewise uses
its own complete-orbit standardization.

## Mechanics ablations

Apply the same joint minimum-z construction and exact inclusive tail to:

- `DIRECT_ONLY`: disable every stripping path; require tail <=0.01 and `T>=2`;
- `STRICT_NO_FUNCTION`: require tail <=0.01 and `T>=2`;
- `SOURCE_PRESENT`: first require at least 30 permutation-reachable observed
  types on at least 10 capacity folios in every reading/panel; if powered require tail
  <=0.01 and `T>=2`, otherwise report `INSUFFICIENT` rather than pass/fail;
- each leave-one-domain-out view: require at least 100 possible types and 20
  capacity folios in every reading/panel; every capacity-qualified view must retain a
  positive released-minus-permutation-median effect in every raw component,
  tail <=0.01, and no favorable domain may be selected later.

Here `permutation-reachable observed types` and `possible types` both mean the
permutation-variable eligible normalized types defined in the capacity section;
its eligible folios are exactly those containing at least one eligible token
instance of such a type.
Every qualified view must also have positive finite SD in all 18 components.
`SOURCE_PRESENT` and an unqualified leave-one-domain-out view are recorded as
`INSUFFICIENT` and are not required gates. `DIRECT_ONLY`,
`STRICT_NO_FUNCTION`, `STRICT_LITERAL`, and top-20 deletion are mandatory:
their capacity failure is itself a robustness failure, never an implicit pass
and never an attempt to compute z with zero SD.

Removing the 570 unreachable keys is an exact implementation invariant, not a
scientific ablation.

## Predeclared decisions

- Primary failure: `FINAL_CONDITIONAL_NONEXCEPTIONAL`; do not retune mapping,
  subset, domain, atom, tokenization, or threshold.
- Primary pass with any powered robustness or concentration failure:
  `HOLD_FRAGILE_POSTSELECTION_LEAD`; do not mine matched types.
- All required gates pass:
  `PASS_FIXED_PUBLIC_CONVERTER_EXCEPTIONAL_WITHIN_10_FACTORIAL_CORE_BIJECTIONS`.

Even the last label means only conditional lookup-set exceptionality and does
not activate Syriac, sound, wordhood, pharmaceutical content, or translation.
Decision order is exact: an unpowered primary stops before identity access;
otherwise failure of any primary-core gate 1--3 takes
`FINAL_CONDITIONAL_NONEXCEPTIONAL` regardless of descriptive ablations. When
all three primary-core gates pass, the result takes
`HOLD_FRAGILE_POSTSELECTION_LEAD` if any mandatory robustness, concentration,
or powered conditional-view gate is false. `SOURCE_PRESENT` or
leave-one-domain views marked `INSUFFICIENT` are nonblocking by definition.
Only a passed primary with every mandatory and every powered conditional gate
true takes the all-gates-pass label.

## Controls required before observed scoring

The runner must stop before the observed panel unless all controls pass:

1. exact scalar 4! and 6! brute-force engines match the optimized engine for
   every raw integer vector, folio vector, distribution scalar, standardized
   vector, `T`, tie/rank count, gate, and decision on every toy permutation;
2. 100 distributed planted-map trials recover the secret map and pass every
   gate in at least 95 trials;
3. at most one of 128 map-independent null trials passes every gate;
4. a fixed-compound/vowel/affix-heavy high-raw-coverage negative fails rank;
5. one-type and one-folio plants fail their concentration gates;
6. a prefix-only plant fails `DIRECT_ONLY`; an unknown-skip plant fails
   `STRICT_LITERAL`; a one-reading-wrong plant fails the joint minimum-z;
7. empty, duplicate, reordered, malformed-annotation, overlength, unknown-atom,
   missing-edition, page/folio-drift, lexicon-order, and row-order mutations are
   either rejected or exhibit their prescribed invariance;
8. core-input/core-output conjugate renaming preserves all score vectors;
9. single-worker and 32-worker score-vector digests are identical on the full
   synthetic 10! orbit;
10. direct/pre-expanded-affix equivalence holds exhaustively on controls;
11. adding/removing all 570 unreachable keys is exactly invariant;
12. no output exists and all input hashes match before observed access.

Before these controls are executed, `DANI001_CALIBRATION_FREEZE.json` must bind
the current science spec; raw-source hashes; stable external projection and
the two external body hashes; panel-builder, calibration generator, optimized
integer core, calibration runner, and independent calibration validator; every
synthetic row, generator domain, trial index, planted map, null map, expected
gate; and exact absence of the four calibration outputs. It must allow only
the named source/code reads, the two exact HTTPS acquisitions, and four
no-clobber output creations. Its static audit must be GO before execution.

After calibration and capacity validate PASS, `DANI001_TARGET_FREEZE.json`
must bind the registration commit and exact bytes/hashes of: this spec; both
freeze manifests; all raw and external inputs/projections; the panel builder;
optimized core; observed runner; clean observed validator; the calibration
result/report/validation JSON/report; the frozen runtime/endianness contract;
and exact absence of all four observed outputs. It must enforce that the
observed runner executes once, cannot read its output or validator, and installs
its result/report by paired no-clobber creation; the validator independently
installs its two outputs the same way. This science specification alone does
not authorize observed scoring.

CPU is the registered numerical reference. Use 32 workers and a string-free
compiled implementation. GPU execution is optional only as a byte-exact
cross-check and may not replace the CPU reference.

## Efficient exact implementation

Compile each token into fixed emitted atoms plus occurrences of the ten core
variables. Encode accepted skeletons of length at most ten in base-16 `uint64`.
For each token/accepted code of matching length derive compatible partial
bijection constraints, consolidate identical constraints with vector weights,
then enumerate completions into Lehmer-ranked arrays of 3,628,800 permutations.
Process metric/ablation blocks sequentially with OpenMP over 32 workers. A
scalar independent implementation validates toy universes and sampled full
maps. The registered CPU path must finish all synthetic controls before it is
allowed to read observed panel templates.

## Output and validation

The observed runner creates only:

- `results/dani001_fixed_mapping_diagnostic.json`
- `results/dani001_fixed_mapping_diagnostic.md`

The clean validator creates only:

- `results/dani001_fixed_mapping_diagnostic_validation.json`
- `results/dani001_fixed_mapping_diagnostic_validation.md`

All four must be absent before observed execution and installed without
clobbering in their two authorized phases. The result JSON
must contain aggregate counts, hashes, score summaries, gates, controls,
decision, isolation flags, and the claim ceiling. It must contain no source
group, surface form, folio ID, lexicon key, Syriac spelling, English gloss, or
matched-word list.

Canonical JSON is UTF-8 `json.dumps` under the frozen CPython runtime with
`sort_keys=True`, `separators=(",",":")`, `ensure_ascii=True`, and
`allow_nan=False`, followed by one LF. Normalize every computed numeric zero to
positive `0.0` before serialization. Nonfinite values hard-stop. The Markdown
report is a deterministic rendering of that canonical object; no locale-aware
formatting is permitted.

A nonimporting clean validator must independently reconstruct the raw source
groups, normalization, lexicon subsets, all 10! score vectors, concentration
summaries, controls, canonical JSON, and report. It may not import or execute
the runner, optimized core, or deposited pipeline. Publication requires exact
PASS validation.

## Route distinction

DANI001 is not a new known-language alignment, plant match, image route, or
grammar-to-meaning experiment. It audits one newly published fixed external
lookup mechanism. A positive result cannot reopen the closed known-language
route without a separately held bilingual/phonetic or authorial anchor and
connected specialist-readable text. A negative result rejects only the
conditional exceptional-membership claim for the released mapping/lexicon
mechanics at this frozen resolution; it does not show that the converter or
lexicon is intrinsically false.
