# GDT144 — corpus-wide relation retrieval sensitivity

## Question

Does the GDT140 relation signal retrieve the human-paired target from all
comparable Herbal A/hand-1 pages, rather than only distinguish the five frozen
targets from one another?

This exposed post-hoc sensitivity uses the already published
`gdt112_o_ot_units.tsv`, a f84r-free set of unique page×PAGE_HOST×O/OT-frame
units, plus the f84r-free GDT137 Herbal page inventory.  It does not reopen the
global HPR2 source.  The representation is therefore deliberately partial:
only PAGE_HOSTs attested under O or OT are present, and occurrence frequency is
not retained.

## Fixed sensitivity family

Eligible candidates are all pages in the GDT137 inventory with Currier A and
hand 1 that have at least one GDT112 O/OT unit.  For each covered GDT140 source
page, exclude itself and any page on the same physical folio.  Score candidate
targets by set Jaccard under four declared views:

1. exact PAGE_HOST;
2. boundary-marked PAGE_HOST character trigrams;
3. exact O/OT-frame plus PAGE_HOST;
4. O/OT-frame plus boundary-marked PAGE_HOST trigrams.

The f17v→f96v relation is an explicit capacity exclusion because f96v has no
O/OT unit.  All other four relations are scored without deletion.

For aggregate inference, standardize candidate similarity separately for each
source page and average the four true-pair z scores.  Generate 100,000 fixed-
seed worlds by sampling four distinct eligible target pages, respecting each
source's self/physical-folio exclusion.  Report local tails and the maximum of
the four standardized representation statistics.

## Ceiling

Use `O_OT_PAGE_HOST_CORPUS_WIDE_RELATION_RETRIEVAL_SUPPORTED` only if at least
three of four true targets rank in the top decile and the shared max-four tail
is at most .05.  Otherwise use
`O_OT_PAGE_HOST_CORPUS_WIDE_RELATION_RETRIEVAL_NOT_SUPPORTED`.

This can only test a partial O/OT PAGE_HOST set representation.  It cannot
establish or refute every PAGE_HOST representation, botanical truth, identity,
semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning,
or translation.
