# GDT1062 preregistration — public plant-label source positions

Registered 2026-09-28 before opening the target Voynich text. The pinned
Schechter `04-plant-identifications.md` at commit
`71f2f3c91e9113d285ab21e024f1dd70c1f43c44` (SHA-256
`66d9b8771595d1a48817978b336b2bbf857509dff853cd8665b462062e2a1216`)
claims that the first word of each listed herbal folio is a plant-name label
decoded by a separate positional cipher. The complete 26-row source table has
23 pages in the existing text allowlist; f1v, f54r and f57r are excluded before
Voynich source access. `src/claims.tsv` fixes all 23 admitted page/EVA/plant
claims, with no case selection based on target observations.

## Decision note

Unknown: whether the 23 published EVA strings are actually first prose words
on their named pages in the three current readings. GDT1059 already establishes
`kooiin` as an f2v and f29v exact head but cannot select a botanical meaning;
the previous GDT1061 public decoder had unaligned quoted source lines. Thus
literal source-position alignment is the smallest adequate gate before any
botanical assessment. If many strings align, retain only those as sourced
candidate labels for a separate visual and semantic test. If they do not,
the table's claimed first-word plant decipherment lacks its stated input
position on those pages. Neither result alone identifies a plant or validates
the positional cipher.

Compare each of all 23 admitted page/label pairs with the **first group of the
first P locus** in each of ZL3b, IT2a and RF1b. Also report exact occurrences
anywhere on the same page, including P versus L locus kind, to distinguish a
wrong first-position claim from an absent string. Preserve exact spelling and
group boundaries; no normalization beyond pre-existing `*_clean` source
columns, no fuzzy or prefix matches. Report every claim and each reader,
including mismatches, and the full source table's three access exclusions.
Readers are alternate transcriptions of one manuscript, not three independent
witnesses. Pages, plant visual IDs and meanings have historical project exposure;
this is not blind botanical confirmation. In particular the known f29v
`kooiin` counterpart remains a lexical-stability obligation for any f2v
`BORAGO` reading. No new image or f84/f84r/reserve access.

Budget: 10 min source pinning, 15 min comparison code, 10 min validation and
interpretation, 10 min publication; stop expansion at 45 min. No p-value or
confirmed word from source alignment alone.
