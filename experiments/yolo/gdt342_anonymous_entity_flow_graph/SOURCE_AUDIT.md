# GDT342 source audit — normalized entity-flow capacity

GDT342 reuses the six public, hash-frozen CoReMA recipe collections from
GDT176. Their provenance, dates, URLs, licences, source bytes, and oracle-table
construction remain bound by `gdt176_source_freeze.json` and
`gdt176_corema_collection_manifest.tsv`.

The source-only oracle has 1,136 complete records and 13,612 non-title elements
with an editor concept ID. Of those records:

- 1,134 contain at least one concept-linked element;
- 989 contain a concept repeated within the record;
- 983 contain a concept repeated across distinct instruction/exterior fields;
- the median record has 10 concept-linked elements, eight distinct concepts,
  two repeated concepts, and two cross-field concepts.

Concept-linked rows are confined to source categories such as ingredient,
tool, and dish. GDT342 does not retain those categories. Rows without a concept
ID become unique local singletons rather than being silently dropped or
identified from their wording.

The external parallel truth is unchanged from GDT341: 1,115 single-title
records, 688 records participating in 657 cross-collection parallel pairs, and
zero positive pairs with identical normalized source surfaces. GDT342 changes
only the observable representation used for ranking.

The graph receives no editor title, English label, concept name, global
concept ID, source word, character, semantic role, or word length. A local
anonymous entity symbol is meaningful only inside one record. The global
concept and raw-word models are explicit comparator controls, not parts of the
candidate graph.

No image inspection, OCR, or automated vision is required. No GDT327 row,
Voynich tuple value, target outcome, illustration, or f84 artifact was opened
for this audit or freeze.
