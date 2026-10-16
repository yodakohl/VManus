# GDT1393 method

The frozen proposed recovery algorithm follows six separate source-prior
beams, one for each unchanged GDT1390 model. This experiment computes only its
first ten steps, before any of the eighteen old control matrices restricts a
next character. The result is a necessary capacity check, not complete recovery.

At depth i, extend each retained prefix by all27 character residues. Add the
original source table's log probability at context length min(3,i). Keep the
best65,536 prefixes, breaking exact score ties by ascending base27 prefix code.
A fixed-length base27 code preserves lexicographic ordering, including leading
spaces. Separate beams preserve the complete-message component convention;
they are not a per-character mixture. The later proposed complete-candidate
score would still be the unchanged normalized1390 mixture, but is not computed.

The primary implementation uses partial selection followed by explicit score
and lexical tie resolution. The independent validator uses full lexical sorting
of every candidate frontier. Both use the public source tables and the same
IEEE double addition order along each prefix. Small source-free examples are
checked against exhaustive enumeration. No truth guides beam construction.

For each control, form the23-column row from the difference of adjacent
22-unit packet-count vectors, followed by1 for the shared offset. Initial
previous packet counts are zero. The preceding diagnostic determines exact
image cardinalities over Z/27; an independent affine-module update verifies
that each first-ten extension has27 choices. Thus there are no hidden early
modular restrictions that might remove rivals before truncation. Surjectivity
modulo27 also provides lifts of modulo3 kernel directions; valid-key feasibility
cannot remove a ten-character prefix.

After code/input locking and beam generation, a separate output seal binds
all six arrays and compact summaries. Only then is the historical1390 truth
read for the exact ten-character membership comparison. Previously public
controls remain exposed; this order does not turn them into independent data.

A missing positive prefix cannot re-enter any of these fixed beams. One such
case is enough to stop full implementation under the original all-twelve
recovery criterion. A different width, traversal, proposal score, channel-aware
early filter, or revisiting of discarded candidates is outside this claim.
