# GDT031 Herbal Currier A/B record architecture

GDT031 compares only pages catalogued as Herbal (`section=H`) in the frozen
f84r-free GDT016 inventory. The source inventory supplies anonymous record
states; existing human page annotations supply only page type, illustration
profile, text-line count, paragraph count, label presence, and special layout
flags. No new visual observation is made.

The primary sensitivity matches Currier-A and Currier-B pages within the same
human illustration profile (`ALPHA`, `MIXED`, or `UNCLASSIFIED`). `BETA` has no
Currier-A capacity and is excluded. Within each profile, the maximum possible
number of pairs minimizes this frozen cost:

`|prose lines| + 2|paragraph starts| + 4(label-presence mismatch) +
2(special-layout flag mismatches)`.

Pairs with cost above four are excluded by a fixed caliper. A global matching
then maximizes pair count while allowing at most one page from each physical
folio on either side, minimizes total cost, and breaks ties lexicographically.
The resulting eight independent-folio pairs contain two ALPHA, two MIXED, and
four UNCLASSIFIED pairs. The latter match absence of a catalogue profile, not
affirmative visual identity. A four-pair classified-only sensitivity is
reported separately.

Five primary page-level axes are tested in the B-minus-A direction with exact
paired sign flips and five-test Bonferroni correction:

1. mechanically compiled nonempty fields per line (`DY`-closed fields plus a
   nonempty open tail, or one field on a checkpoint-free line);
2. conditional adjacent DY chaining;
3. singleton closed-field fraction;
4. open-tail continuation after a DY-bearing line;
5. direct QJB/QKB/LJB/LKB rate minus insertional QJAB/QKAB/LJAB/LKAB rate.

Additional line and Q/L summaries are descriptive. All Currier-A Herbal pages
are hand 1, whereas B pages are hands 2/3/5; the experiment cannot distinguish
Currier from hand. It tests within-section architecture, not authorship,
language, meaning, or translation. f84r is not opened, retained, or scored.
