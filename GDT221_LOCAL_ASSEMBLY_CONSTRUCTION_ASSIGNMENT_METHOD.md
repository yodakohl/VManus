# GDT221 — local assembly construction assignment

## Question

Do complete label-construction profiles align with independently human-defined
local prose blocks?  This tests the full-record alternative left open by
GDT220; it does not search another terminal key or word meaning.

Two pages have two catalogue-defined assemblies without using f84:

- f75v: labels by the top pond versus labels by the lower pond, compared with
  prose above the top pond versus prose to the right of the lower pond;
- f83r: the two upper labels/text block versus the two lower labels/text block
  of the southwest figure.

The exact source-bound locus sets are frozen in
`gdt221_assembly_manifest.tsv`.  f75v.22/.23 and f83r.50 lack eligible rows in
the existing strict label inventory and remain visible as exclusions.

## Representations

Use exactly three previously established source-display views:

1. `RAW_CHAR3` — multiset of boundary-marked token trigrams;
2. `PAGE_HOST_CHAR3` — multiset of boundary-marked residual-host trigrams;
3. `SOURCE_FAMILY_CHAR3` — multiset of boundary-marked source-family
   trigrams.

For each page and representation, form a 2×2 weighted-Jaccard matrix between
top/bottom label bags and top/bottom prose bags.  The assignment lead is

`sim(top_label,top_text)+sim(bottom_label,bottom_text)` minus the swapped sum.

The primary score uses only prose lines whose observed HPR2 group count equals
their declared source group count.  An all-available-row sensitivity is
reported but cannot rescue the primary.  The exact null independently swaps
the two prose blocks on each page: four worlds.  Report local and max-three
inclusive tails.

Individual labels are also ranked against the two prose blocks.  This is a
diagnostic: ties receive no credit and no post-hoc threshold is selected.

## Decision

Transfer requires a positive primary page lead on both folios and max-three
`p<=.05`.  Anything weaker is at most a page-local construction resemblance.
No label, host, family, or state receives a key value or meaning.  f84r and
every f84 row are excluded before retention.
