# f2r.15 native-visual ownership correction

Decision: **CORRECT TO BOUNDARY OVERLAP; LAYER ORDER UNRESOLVED**.

The official Yale f2r image does not support the acquisition packet's strong
`DIRECT_ENCLOSURE_UNDER_PAINT` relation. The physical record manually read by
ZL3b and RF1b as `ios an on` straddles the narrow outer tip of a green-painted
leaf. Part of the record overlaps a pale green area, while the rest continues
to the right on bare parchment. The complete record is therefore not enclosed
inside the leaf.

Ordinary-light pixels do not securely determine layer order. They cannot
distinguish ink applied before the green wash from ink applied afterward or
ink remaining visible through a transparent wash. The visible relation is
best recorded as `BOUNDARY_OVERLAP_LAYER_ORDER_UNRESOLVED`, with a weaker
local leaf association retained.

This correction matters because f2r.15 was the strongest supposedly direct
visual-to-text anchor in the acquisition registry. It remains an unusual
production-layer clue, but it is not secure evidence for an under-paint
instruction and still has no contrasting Voynich-script colour record.

The glyph sequence comes only from the existing manual transcriptions; the
image was not used for OCR or rereading. This is source-bound native AI visual
inspection, not literal human annotation. No colour value, pigment action,
word, sound, language, cipher, plaintext, meaning, or translation follows.
