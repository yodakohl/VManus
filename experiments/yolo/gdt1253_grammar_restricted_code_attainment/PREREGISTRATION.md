# GDT1253 — grammar-restricted code capacity

Question: does adding one code entry and a fixed source restriction suffice
for complete formal coverage, despite free ambiguity? This addresses an exact
capacity boundary, not a proposed word meaning or a natural-language decoder.
The native <=22predecessor is inherited under its stated unit/group premises;
it is neither recomputed nor extended to every conceivable script.

Construction over n visible symbols: give each its singleton source symbol,
and add B encoded xy for any distinct x,y. Forbid only the adjacent source
pair Xx Xy. Decode every xy as B, every other symbol as its singleton source.
Because x!=y, occurrences of xy cannot overlap. In a legal source expansion,
an xy not inside B could only cross the forbidden Xx Xy boundary. Thus
expansion and this decoder are mutual inverses. Every output word has exactly
one legal source parse. Free parsing remains ambiguous: B and Xx Xy coincide.

This needs n+1entries, no new visible symbol, dictionary, token state or escape.
No source value or physical sign interpretation is selected. The prohibition
is invented, not recovered linguistic knowledge. Choosing it solely to make a
code work is not evidence for a historical language. Wordwise bijection still
preserves whole-source-word frequencies;1202fixed-source failures stand.

Tiny binary teaching version A=0,B=01,C=1 is checked against an independently
implemented exhaustive parse enumeration with forbidden AC, on all nonempty
binary words through length8. Legal source strings through length6 are checked
for exact roundtrip; illegal AC is explicitly rejected. All length proof above
is the justification, finite cases are software checks only. No native W read,
no fitted table/pair, image or source corpus. Local registration before execution.

Registered UTC: 2026-10-07T09:18:47.415358+00:00
