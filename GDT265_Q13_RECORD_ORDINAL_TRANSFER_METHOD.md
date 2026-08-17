# GDT265 — q13 record-ordinal transfer

## Question

GDT264 found that two halves of a q13 mechanical record retrieve each other,
most strongly through wrapper and right-renderer ecology.  This successor tests
the main nuisance explanation: do those fingerprints merely encode the earlier
versus later eligible record on a page?

## Panel and fold

The panel is unchanged: nine f84-free q13 pages, each with exactly two GDT227
records having at least four physical loci.  Seven pages contribute R01/R02,
f79r contributes R02/R03, and f79v contributes R03/R04.  Hold one entire page
out.  Build `EARLIER` and `LATER` feature centroids only from the other eight
pages.  Each held
record is divided by the four fixed GDT264 locus splits, and both halves are
scored independently.  For every held-page/split/view combination, jointly
assign its two records to `EARLIER/LATER` by the orientation with the larger summed
cosine score.  There are 9 × 4 × 2 = 72 assignments per representation.

The fixed representations are structure only, wrapper, right family, complete
compiler coordinates, exact raw group, exact PAGE_HOST, raw character
trigrams, and PAGE_HOST character trigrams.  IDF weights and centroids are
learned inside each held-page fold.  No n-gram crosses a source-group or host
boundary.

## Exact null

All `2^9 = 512` global worlds independently swap `EARLIER/LATER` labels within each
page.  For each held page, only the eight training-page swaps affect the fitted
centroids.  The same worlds are shared by all representations.  Report local
inclusive and max-eight p-values.

A strong wrapper result would demote GDT264 to a global record-position effect.
A null wrapper result would show that its wrapper fingerprint is page-record
local rather than a reusable first/second-record code.  Neither outcome names
a topic or translates a record.  This experiment uses only the already
published f84-free GDT227 table; it performs no new f84r access.
