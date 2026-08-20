# GDT392 source-access correction

The pre-image freeze stated that zero “Voynich surface or formal rows” were
read. That combined statement was too broad.

The frozen source inventory is a human visual catalogue rather than a formal
projection, but its complete rows include local comments and occasional
diplomatic glyph notes. The freeze loader materialized all 504 rows. After all
14 canvases had been directly reviewed, a source-comment search displayed some
of those rows while the six visible start-only boundaries were attributed.

The corrected access statement is:

- zero formal-family, PAGE_HOST, joint-tuple, or renderer rows were opened;
- no formal identity or score selected an array or supplied a direction;
- all 504 source catalogue rows were materialized, and some diplomatic notes
  were displayed after visual review;
- the comments helped attribute already visible start-only boundaries and
  identify “clockwise” as editorial transcription order;
- no formal score was run; and
- no f84 content was opened, parsed, retained, displayed, or scored.

The complete selection, six start-only cases, zero direction markers, zero
eligible edges, capacity failure, and claim ceiling are unchanged. The
original freeze bytes remain in Git history and are bound by
`gdt392_access_correction.json` rather than silently rewritten.
