# GDT1078 preregistration — same-folio challenge to GDT1077

GDT1077's registered same-rest, same-section/hand r/l versus next-initial
association passed (ZL3b 87/117 informative cells), but different r/l
instances of one rest can sit on different physical folios. Page topic or
word-pair reuse could create the contrast. GDT915/916 tested a different
next-terminal relation and remain unchanged. Unknown here is whether the
GDT1077 direction remains when rest and physical leaf are both fixed. A
positive would strengthen the written-context grammar priority; failure
would confine it to cross-page mixtures. No result can establish phonetic
sandhi or a meaning.

Freeze GDT1077 `EVENTS.tsv` SHA256
`b94d3bdc25a084b0ec25e24a2357363ab0bce05da409c89f2f252fde5687e1b1`.
Use every event in it, with no new page, image, raw source query, base,
initial class or resegmentation. Group separately by `(reader, rest, folio)`;
section/hand are inherited from that physical source. A mixed cell is
informative only when r and l each occur at least twice. Count the fixed
next-initial `{a,e,i,o}` fraction after each ending and its r-minus-l
difference, retaining all cells and exact zeroes. Primary ZL3b gate:
at least **20 informative cells on 10 different physical folios**,
at least **two-thirds** of informative cells strictly r-higher, and equal-cell
mean difference at least **0.05**. Ties count against the proportion.
IT2a/RF1b are alternate-reader sensitivity.

As a positional diagnostic, split the same frozen events by whether the
left group is source-group 1 or source-group ≥2. Within each subset, repeat
GDT1077's rest/section/hand eligibility (r and l each ≥3 occurrences on
≥2 physical folios) and report direction/mean; these subsets cannot rescue
or replace the same-folio primary gate. All event/cell counts are reported,
not selected examples. No p-values: the full project search and page/lexical
dependencies are not controlled. Earlier exposure of the data remains.
Budget 30 wall minutes from implementation through validation/publication;
stop expansion rather than alter thresholds or add a new decoder.
