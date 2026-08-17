# GDT260 — f82r component-label paragraph neighborhood method

f82r.10 is selected solely from the published human dossier: it is the only
f82r graphical label with `CONNECTED_COMPONENT` ownership evidence, described
as being on a cross-shaped drawn component. It lies immediately before the
corrected second physical paragraph, whose first line is f82r.11. The Voynich
form did not select the target.

The three readings disagree about one source separator. ZL3b has one joined
group, while IT2a and RF1b split the same seven-member sequence after member
four. GDT260 therefore tests exactly three representations in every reading:

1. the left four-member component (`orol` in the split readings);
2. the right three-member component (`dain`/`dair`);
3. the joined seven-member label.

For each representation, every same-length member-code window wholly inside a
published f82r prose group is compared by Hamming distance. A prose physical
line is positive when it contains at least one window at distance at most one.
The externally fixed target region is P2, the paragraph immediately following
the label in locus order. Conditional on the number of positive lines, the
local tail is the exact hypergeometric probability that at least the observed
number falls among P2's nine lines out of 32. A transparent Bonferroni factor
of three covers the three tested label representations. ZL3b, IT2a, and RF1b
are reading sensitivities of one manuscript, never replications.

This remains exposed YOLO hypothesis generation. The one-edit radius and
member-window endpoint were not prospectively frozen before the page was
known, and the correction covers neither that analytic choice nor later reuse
of the result. Exact identity, the complete label, and family-only recurrence
are mandatory counterchecks.

Inputs are the published f82r dossier, the f80r/f82r-only discovery projection,
and the corrected f82r paragraph coordinate. They contain no f84r row. The
prior GDT257 transient access breach is disclosed; no new f84r access occurs.
