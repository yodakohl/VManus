# Concrete text patterns from three Luna searches

2026-09-08. User-directed descriptive text lookup, not a meaning experiment.
Three explicitly selected gpt-5.6-luna agents searched independently for exact
phrase repeats, variable-middle frames, and serial patterns. Each used the
179-selector GDT631 roster through the selector-first guard;96,184 source rows
are alternate-reading group records, not independent manuscript occurrences.
No image, outside LLM API, semantic renderer, significance test or decoder ran.

## Selected examples

| Pattern | Literal example | Locus |
|---|---|---|
| Repeated pair ABAB | `shol kaiin shol kaiin` | f8r.19 |
| Repeated pair ABAB | `cheor chey cheor chey` | f30r.11 |
| Fixed flanks, differing middle | `chol y daiin` | f16v.8 |
| Same flanks | `chol daiin daiin` | f21v.4 |
| Same flanks | `chol todaiin daiin` | f21v.6 |
| Another fixed frame | `ol r aiin` | f105r.15 |
| Same frame | `ol s aiin` | f55v.10 |
| Repeated complete triple | `chey qol chedy` | f104v.4 and f111v.32 |

Root independently reacquired these nine locus examples and the additional
`ol cheor aiin` at f107r.46. All ten have one exact matching raw sequence in
each reading. Nine have definite internal spaces throughout. At f107r.46,
ZL3b has an uncertain small space between `cheor` and `aiin`; IT2a/RF1b mark it
definite. The first frame summary overstated this seam agreement and is corrected.
Use `qh3_verified_examples.json` for the exact reader-specific indices/seams.

The exact-phrase agent also finds `shedy qol shedy qokaiin` at f78r.40 and
f80r.35, but the latter is exact only in IT2a. Its length4–6 search finds no
length5/6 sequence recurring at distinct loci, and just that length4 sequence.
This is exact raw grouping **within each locus**, across the specified scope;
it is not a search across line boundaries, normalized spelling or uncertain
word reconstructions. The code retains separator classes, including drawing
interruptions where present; raw index adjacency is not always an ordinary space.
The longer recurrence is already in GDT639/GDT661 artifacts.

## Interpretation and priorities

The nonsymmetric `chol … daiin` and `ol … aiin` frames, together with the two
ABAB examples, are the most concrete comparison material in this delivery.
Their presence does not establish a grammatical construction, synonymy, a
copying mechanism, numerical values or any translation. Common endpoint forms
can produce repeated frames by chance; no frequency-matched null was tested.
Do not turn three transcription readings into three independent occurrences.

The agents mark several phrase repeats as known. Historical novelty of every
frame/serial example has not been established; known f21r.11 and f86v3.3
examples must not become new discoveries. No failed GDT838 reference or
minimal-pair semantic route is reopened. The raw groups, including single-character
groups, are retained as written in the source atlas.

## Reproduction

- `qh0_repeated_text_patterns_extract.py`: guarded exact triple lookup.
- `qh0_longer_repeat_extract.py`: guarded within-locus length4–6 repeats.
- `qh1_variable_text_frames_runtime.py`: recount supplied guarded projection;
  fields used are the source IDs, edition/locus, group index/count, row index,
  raw group and both separator columns. Its fixed frame inventory is explicit.
- `qh2_serial_text_patterns.py`: guarded serial census and five highlights;
  root replay reproduces the reported125/102 ABA,2/2 ABAB and14/11 near-repeat
  census. See its exact rules; these totals are not significance measures.
- `qh3_verify_examples.py`: independent guarded recount of the ten selected
  examples, producing `qh3_verified_examples.json`.

Frame counts remain separate by reading. A union of reader-specific
`(locus,index)` keys is not a physical occurrence count because indices can shift
with alternative segmentation. The summary now uses `reader_index_key_union`.
