# GDT1349 — Exact conditional capacity of nested and circular fields

A globally fixed, disjoint field alphabet can survive if returns are allowed by nesting. On the FULL panels the exact maximum is 6 classes in IT2a, 6 in RF1b and 7 in ZL3b. Requiring each class to occupy one circular interval reduces the exact maximum to 4 in each reader. This excludes larger class counts under those contracts; it does **not** exclude either whole family.

## Contract and evidence

The [preregistered contract](PREREGISTRATION.md) uses the unchanged GDT1233 cache: internal complete P groups with definite spaces on both sides. The 22 working units and complete-group record boundaries are assumptions. Each reader is checked separately; these are alternate readings of one manuscript. No images, meanings, sound labels or reserve data enter the calculation.

A nested field may contain other fields between its own signs, but each class occurs at one node per record. Alternating subsequences ABAB force A and B into the same class. Necessary merge closure gives the unique finest valid partition. The circular condition permits arbitrary cuts and field order, but each class must form one circular interval. Exhaustive binary cuts of the forced blocks followed by exact cover give its maximum. Arbitrary coarsening need not preserve validity.

## Results

| Reader / panel | Groups | Types | Nested maximum | Circular maximum | Groups using >1 finest class | Groups with nesting under finest |
|---|---:|---:|---:|---:|---:|---:|
| IT2a_FULL | 22528 | 4272 | 6 | 4 | 4432 (19.67%) | 252 |
| IT2a_PHYSICAL_LEAVES_GE2 | 19687 | 1466 | 13 | 8 | 11165 (56.71%) | 6295 |
| RF1b_FULL | 19321 | 3818 | 6 | 4 | 1050 (5.43%) | 477 |
| RF1b_PHYSICAL_LEAVES_GE2 | 16786 | 1315 | 15 | 9 | 12270 (73.10%) | 7563 |
| ZL3b_FULL | 19332 | 3773 | 7 | 4 | 4367 (22.59%) | 483 |
| ZL3b_PHYSICAL_LEAVES_GE2 | 16865 | 1337 | 14 | 9 | 11241 (66.65%) | 8037 |

GE2 retains whole forms on at least two physical leaves, not merely two sides or two occurrences. It is a sensitivity panel, not error correction or independent confirmation. The FULL result remains binding for the full cache. Rare forms materially tighten the limits; no transcription error has been diagnosed.

The multi-class count is an upper bound for **any** admissible nested or circular partition on that panel. All valid partitions coarsen the forced blocks. Thus even the most expressive allowed nested partition leaves 80.33% of IT2a, 94.57% of RF1b and 77.41% of ZL3b FULL groups within one class. This is a limitation on a disjoint-field interpretation, not a percentage of meaning explained or lost. Internal order and repetition within one class may still carry arbitrary information. Maximum nesting depth is 2 under each finest partition; this is not a depth bound on every possible coarsening.

## Surviving alphabets

The FULL finest nested partitions are:

- IT2a_FULL: {a, ch, ckh, cth, d, e, i, k, l, o, p, q, r, s, sh, t, y} / {cfh} / {cph} / {f} / {m} / {n}.

- RF1b_FULL: {a, ch, ckh, d, e, i, k, l, n, o, p, q, r, s, sh, t, y} / {cfh} / {cph} / {cth} / {f} / {m}.

- ZL3b_FULL: {a, ch, ckh, d, e, i, k, l, o, p, q, r, s, sh, t, y} / {cfh} / {cph} / {cth} / {f} / {m} / {n}.

One maximum circular partition per FULL reader (witnesses, not uniquely identified historical fields):

- IT2a_FULL: {a, ch, ckh, cth, d, e, i, k, l, o, p, q, r, s, sh, t, y, f, n} / {cfh} / {cph} / {m}.

- RF1b_FULL: {a, ch, ckh, d, e, i, k, l, n, o, p, q, r, s, sh, t, y, cph, f} / {cfh} / {cth} / {m}.

- ZL3b_FULL: {a, ch, ckh, d, e, i, k, l, o, p, q, r, s, sh, t, y, cph, f, m} / {cfh} / {cth} / {n}.

All admissible cuts, activity and source-bound merge witnesses are retained in `artifacts/RESULT.json`. Class names above are transliteration units, not translations.

## Manual check of why classes merge

IT2a f3r.5 G002 `chololy` contains o–l–o–l at unit positions 1,2,3,4 (zero based). Keeping o and l in separate one-node fields would cross the fields, so they must merge. IT2a f7v.6 G005 `oksholshol` then crosses the merged o/l class with sh. Later witnesses propagate mergers; they are not independent evidence that every pair directly alternates. The final IT2a merger is witnessed by `dairair` at f106v.40 G006. The saved source rows and current class memberships make that chain auditable.

The recurrent panels still contain `dalor` as a merge witness in RF1b and ZL3b; the four positions refer to **already merged classes**, not four identical literal signs. This illustrates why checking only literal pair repetitions would miss necessary consequences. These are manual readings of cached transliteration, not new palaeographic verification.

## Validation and correction

The independent validator reparses all raw strings, reconstructs closure using explicit four-position subsequences in another word order, replays each certificate, and independently enumerates circular cuts by counting exits. Z3 checks that no exact cover with one additional class exists. Source-free exhaustive fixtures test the mathematical reduction. See `artifacts/VALIDATION.json` for completed checks.

The first validator stopped because it compared the two merge classes in encounter order while the producer records lexical order. For `chololy` those orders are reversed. The locked original is preserved; `src/validate_corrected.py` compares the unordered pair while retaining all source, position and membership checks. `artifacts/VALIDATOR_CORRECTION.json` documents the correction. No input, scientific criterion, producer or native result changed.

## Decision and limits

IDEA001025 and IDEA001018 now have measured conditional capacities; neither is a newly discovered writer. Do not repeat this census or infer that four semantic fields have been found. The old GDT1321 linear no-return failure remains: allowing ABA through nesting or a circular cut is a genuinely different contract. GDT1263 weak rank order and GDT1345 within-class sorting are also distinct and retain their original decisions.

The retained class is too broad to decode internal payload order: the large forced core remains essentially unconstrained. A useful continuation would need a separately justified, falsifiable rule for that payload, after duplicate and predecessor checks. No new payload route is selected here. Whole families with overlapping alphabets, repeated class-labelled nodes, context-dependent roles or different true units/boundaries remain outside this exclusion. Phonetic writing and meaningful content remain open. Confirmed English lexemes: **0**.
