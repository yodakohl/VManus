# GDT1377 — Bind the missing context of the f18v boundary case

## Decision note and prospective scope

GDT1376 leaves the ordered key A=sh, B=cph locally possible only because
f18v.8 G002 is the first retained group. The actual G001 was not read there.
This test binds that concrete omitted context; it does not repeat the census.
Budget: 25 minutes including preparation, implementation, independent review,
validation and publication. No source-language fitting or word meanings.

Use the existing GDT915 SOURCE_EVALUATION caches only: ZL3b primary, IT2a and
RF1b predeclared sensitivities, each separately reported. They are alternative
readings of one physical site, not three replications. Read only f18v.8 P-kind
groups at original indices 1,2,3 after selecting the line by its metadata.
The 631 text allowlist admits f18v. No images, raw TSV query, new admission,
f84/f84r, f116v, f1r body or reserves. This is previously exposed project text,
not a historically untouched confirmation sample. Cache hashes are taken
from the existing GDT915 manifest before opening target payload.

## Fixed gates

Require a unique selected line per edition, matching page/locus/kind/edition,
source_group_count >=3, exactly one group at each of indices 1,2,3, and unique
coherent source IDs. G002 and G003 must be exactly `sh` and `cphoy`, as in1376.
Both shared seams must be DEFINITE_SPACE on both sides. Do not require the
leftmost separator of G001 to be definite: its outer context remains open.

Parse G001 literally and completely using the unchanged working units
`a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh`.
Unknown symbols, entities, annotations, empty strings, missing rows, uncertain
seams or mismatched fixed witnesses give UNSCORABLE, not a contradiction.
Use dynamic segmentation to require exactly one full parse; the working code
is uniquely decodable, but not prefix-free. No normalization or corrections.

## Consequence fixed before reading G001

The middle `sh` has one unit, and `cphoy` has more than one. Thus the output
sh|cph obligation can only be rescued by an actual left cph|sh seam. If the
last unit of G001 differs from cph, report FIXED_KEY_EXCLUDED_AT_BOUND_CONTEXT.
If it equals cph, report REQUIRED_RESCUE_PRESENT: the particular obstruction
is absent, not a confirmed key, full-stream preimage or meaningful source.
If any gate fails, report UNSCORABLE with the actual failing gate(s).
Do not select another reader after seeing the primary, loosen parse/seam
requirements, assume a reset at a line boundary, or repair the writing rule.

Independently check the implication by reverse-all-BA then forward-once on
the three-group window with the same two-unit open padding as1376. When the
left rescue is present, other obligations can still block the entire window;
the declared status refers only to the fixed middle obstruction. For an
excluded case, even maximally favorable outside padding cannot rescue it.

## Dependencies and limits

The fixed 22 working units, original visible groups as source words, one
simultaneous mandatory swap and the particular ordered key remain assumptions.
GDT1376's published 462-key counts are frozen and not recomputed here.
Closing this one survivor would not refute every metathesis key or phonetics.
If unscorable, retain the uncertainty and stop this context test; do not launch
an annotation repair or another missing-input census. If excluded, close this
specific key under this newly bound evidence. If rescued, retain compatibility
only. In all outcomes, meaningful decoding still needs a justified source
representation and discriminating consequences beyond image capacity.
