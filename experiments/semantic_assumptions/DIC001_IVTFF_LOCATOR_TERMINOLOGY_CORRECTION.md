# DIC001 IVTFF locator terminology correction

Date: 2026-08-10.

The frozen DIC001 code selects consecutive numeric prose loci where the latter
locator begins `+P`. Its event set and all numerical results are unchanged.
However, the reports called these “continuation-line resets,” which is more
specific than the source metadata allows.

The official *IVTFF format*, version 2.0.2, section 6.4/Table 8 defines `+` as a
locus “generally below the previous item.” It separately defines `*` as the
start of the line below at the left margin, `=` as the same line separated by
white space, and `@` as unrelated/not easily described (and mandatory for the
first page item). Section 6.9 says paragraph starts/ends are the separate `<%>`
and `<$>` comments and that paragraph decisions are made by the transcriber.

Primary source:
<https://voynich.nu/software/ivtt/IVTFF_format.pdf>

Therefore the publication-safe DIC001 reference class is **consecutive
below-locus prose transitions**, not continuation paragraphs, authorial
sentences, or a known discourse state. The confirmed result says drawing
interruptions have local edge shape more like those between-locus transitions
than same-locus ordinary spaces. It supports keeping a structural segmentation
break at the drawing, but not calling it a new sentence, paragraph, clause, or
picture-owned label. No score, gate, p-value, target row, or artifact is
changed by this terminology correction.
