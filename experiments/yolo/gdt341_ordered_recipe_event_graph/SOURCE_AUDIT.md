# GDT341 source audit — parallel medieval recipe witnesses

GDT341 reuses the six public, hash-frozen CoReMA TEI collections from GDT176:
1,136 complete recipes and 27,568 editor-annotated elements. The provenance,
dates, URLs, licences, and byte hashes remain bound by
`gdt176_source_freeze.json` and `gdt176_corema_collection_manifest.tsv`.

The source-only census finds:

- 1,115 records with exactly one normalized editor title;
- 268 title groups represented in at least two collections;
- 706 records in those cross-collection title groups;
- 657 cross-collection pairs that also share at least two editor concept IDs;
- all 657 pairs have different normalized full-surface hashes.

The positive rule therefore captures wording-distinct witnesses rather than
byte-identical duplication. It remains an editor-semantic homology definition,
not an inference from graph similarity.

The previously inspected example “Fake morels, raisins and almonds” occurs as
`b4.86`, `gr1.148`, and `w1.89`. Its witnesses preserve the ordered process of
preparing raisins, pounding, combining almonds, adding sweetener/spice,
shaping, and inserting a stem-like item, while exact wording, opener/closer,
and annotation count vary. Other powered groups include blanc manger, almond
cheese, gingerbread sauce, choux pastry, fish preparations, purees, sauces,
and roasted/stuffed dishes.

GDT341 does not expose those names to the graph. They are held truth labels
used only after ranking. Likewise, hidden operation/material/state/application
transitions are used only to assess whether a retrieved pair retains readable
event architecture.

No new image interpretation is required: GDT340 already established from four
official CoReMA facsimiles that complete recipe blocks vary in length, line
wrapping, rubrication, and closure. GDT341 uses the public TEI record and
containment structure, not OCR or automated image analysis. No Voynich record,
tuple value, illustration, or f84 artifact was consulted for this source
census or graph design.
