# GDT807 preregistration and transparent preview

Registered: 2026-09-04, before the official builder and validator outputs.

## Why this experiment exists

GDT806 found no target-specific local role among six complete wholes.  Reusing
the same immediate neighbour tags with looser prose would add no information.
GDT807 therefore asks a different question: when the entire target-bearing
line is absent, can the rest of the complete paragraph predict which target
whole belonged to it?

The aim is not to prove a translation.  It is to discover whether pairs that
currently carry different concrete working rivals actually inhabit different
nonlocal textual ecologies.  A real split would tell the next historical
codebook round where to look; a failure would remove an attractive source of
invented specificity.

## Outcome-aware disclosure

Before registration, a quick unvalidated multinomial diagnostic was run on
the three pairings.  It used strict paragraph bounds, removed pair-bearing
lines and target surfaces, and held out folios, but it had no cyclic null, K24
controls, independent validator, or final eligibility gates.  Approximate
rank-stable ED1 AUCs were:

| Pair | Preview AUC |
| --- | ---: |
| `cheol` versus `otal` | 0.619 |
| `qokol` versus `qotal` | 0.703 |
| `qokeol` versus `qokol` | 0.589 |

Unquarantined values were approximately 0.655, 0.710, and 0.558.  These values
make the experiment transparent post-data exploration; they are not official
scores and receive no confirmatory p-value language.

## Fixed pair tournament

The official test contains exactly three scored pairs:

1. `cheol` versus `otal`: material/preparation versus quality/state is the
   displayed concrete rivalry.
2. `qokol` versus `qotal`: process/treated preparation versus quality/cold is
   the displayed concrete rivalry.
3. `qokeol` versus `qokol`: heat/process versus specialized preparation is an
   expected-near-null internal stress test.

`okal` and `ol` remain capacity and landmark audits.  They are not converted
into post-hoc pairs if one of the three registered tests fails.

## Information barriers

- The primary score sees only exact whole-surface counts in the target-masked
  paragraph remainder.
- Every line containing any of the seven registered targets is removed before
  eligibility, length bins, features, and overlays are computed.
- All eleven GDT805 target wholes and their exact GDT800 paired-terminal
  partners are excluded from features.
- Section, language, hand, length, folio, and page are controls or fold keys,
  not predictive features.
- GDT755/GDT756/GDT769 renderer categories and the GDT806 652-surface deck do
  not train the classifier.
- GDT757 contributes only exact positional wholes in a later overlay; words
  such as `nimm`, `danach`, or `mische` are not model inputs.
- A paragraph containing both members of a pair is excluded from that pair.
- No result may be rescued by an image, a pleasant-sounding renderer, or an
  occurrence-specific switch between noun, verb, quality, and relation.

## Fixed views and controls

Four views are registered: raw exact-family, GDT805 rank-stable exact-family,
raw ED1 sensitivity, and rank-stable ED1 sensitivity.  The stable exact-family
view is primary.  Unique forced-LCS reader identity is reported as an audit.

The official model, vocabulary threshold, alpha, folio grouping, score,
cyclic offsets, matched strata, K24 construction, result gates, and landmark
rule are fully specified in `METHOD.md`.  Before scoring, two operational
details were closed explicitly: length bins use
`floor(log2(retained_token_count))`, and the K24 deck uses GDT804's full
`PRIMARY_K12` registry because GDT806's six-target export omits `qotal`.
Each K24 pseudo-pair additionally removes every line containing either of its
two control surfaces and quarantines both surfaces from features; otherwise
the model would be allowed to read its own pseudo-label.
Eligibility and length are fixed immediately after that line mask and before
feature quarantine.  A document with no in-fold vocabulary token remains as a
zero-score tie; balanced-accuracy ties count one half.  Cyclic exchange moves
complete memberships across all eligible paragraphs, including empty sets,
using sorted destination `(page, numeric start line, paragraph id)` and source
`(i-offset) mod n`, and derives pair exclusivity afterward.  K24 membership stays inside the
GDT800 `l`-terminal universe; scoreability, target rank, and the single-folio-
removal denominator follow the explicit definitions in `METHOD.md`.
Any implementation correction must
be documented before interpreting changed results and must not choose a new
pair, direction, threshold, or candidate meaning from the observed score.

## Concrete rivals remain displays

The following rival families will be printed beside the structural outcome so
that a useful result points toward an intelligible next test:

- `cheol`: material/preparation versus dry/quality state;
- `otal`: initial preparation/item versus cold/quality state;
- `okal`: opaque register/system entry versus material/preparation;
- `ol`: general carrier/preparation versus a specific liquid medium;
- `qokeol`: process/heat field versus specialized heated preparation;
- `qokol`: process field versus treated preparation;
- `qotal`: cold/quality field versus preparation/item.

These are explicit hypotheses, not translations.  A GDT807 split can promote
only a structural paragraph-ecology contrast and exact landmark list.  It
cannot decide `water`, `wine`, `oil`, `salt`, `root`, `leaf`, `heat`, `dry`, or
any German word without a subsequent discriminating historical/visual test.
