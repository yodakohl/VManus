# GDT340 source audit — readable complete recipe records

## Primary scholarly source

GDT340 reuses the frozen GDT176 CoReMA panel: six dated German recipe
collections (`b4`, `b6`, `br1`, `bs1`, `gr1`, `w1`), 1,136 complete recipes
and 27,568 editor-annotated elements. The cached TEI bytes and their SHA-256
hashes remain those in `gdt176_source_freeze.json` and
`gdt176_corema_collection_manifest.tsv`.

CoReMA is the *Corpus of Medieval German Recipes*, published through GAMS at
the University of Graz. Its public API describes hyperdiplomatic and
semantically detailed TEI layers. Relevant public entry points are:

- <https://gams.uni-graz.at/archive/objects/context:corema/methods/sdef:Context/get?mode=api>
- <https://gams.uni-graz.at/o:corema.b4.recipes>
- <https://gams.uni-graz.at/o:corema.br1.recipes>
- <https://gams.uni-graz.at/o:corema.gr1.recipes>
- <https://gams.uni-graz.at/o:corema.w1.89>

The source's semantic tags distinguish titles/openers, instructions,
ingredients, tools, closers, serving and household tips, time expressions,
dietetics, alternatives, and references. GDT340 uses those tags only to
construct complete-record oracle bits after its form-blind observation layer
has been built.

## Qualitative event-structure audit

The same titled preparation, “Fake morels, raisins and almonds,” occurs as
`b4.86`, `gr1.148`, and `w1.89`. The three witnesses differ in wording,
spelling/abbreviation, element count, opener/closer realization, and some
surface detail. Nevertheless, the source annotation and readable text preserve
the same high-level sequence:

1. introduce/select raisins and almonds as materials;
2. clean and pound the raisins;
3. add and pound almonds with them;
4. add sugar and ginger;
5. shape the intermediate mixture by analogy with a pear;
6. insert an almond/stem-like item;
7. optionally close with a serving/readiness expression.

The ontology therefore survives genuine wording variation at the event level,
while the exact words and the presence of opener/closer material do not.

`br1.42` and `br1.43` provide a second qualitative pattern. Both are complete
apple preparations and reuse a prior stuffing reference, but one includes a
serving/application passage and the other adds a batter/frying continuation.
They share MATERIAL and OPERATION structure while differing in optional
APPLICATION and RESULT/CONDITION realization. This is precisely why GDT340
models optional record-level event axes instead of assigning universal field
positions.

These examples were chosen from the external corpus before Voynich tuple
scoring. They demonstrate ontology readability; they are not statistical
replications and do not enter model selection separately from the full six
collections.

## Direct external facsimile inspection

The following observations are
`AI_DIRECT_VISUAL_OBSERVATION_EXTERNAL_COMPARATOR`. They concern visible layout
only. No OCR, text recognition, embeddings, segmentation, or automatic image
classification was used.

| source | official IIIF canvas | inspected image | SHA-256 | neutral observation |
|---|---|---|---|---|
| W1 fol. 011v | `o:corema.w1.011v` | 1200×1670 JPEG | `68c5c874bb0728a5ddf40f0ad49d6d04654cc4e65d2dcd172e7448e534b9be7f` | ruled page; several variable-length blocks; red headings and enlarged initials mark record starts |
| B4 fol. 086r | `o:corema.b4.086r` | 1200×1929 JPEG | `c0e4ab48bf61ba31f52ed0f7c2f93b8c5e4476a251096c2f59072f9ec1a2498f` | dense continuous writing; rubricated headings and enlarged initials segment variable blocks |
| Gr1 fol. 048r | `o:corema.gr1.048r` | 1200×1521 JPEG | `fdcb32a817a1f69580fc227cdf92ee88fe827d0b47c3210e13339cd2bd4e3b82` | multiple variable recipe blocks; modest gaps and initial cues; ordinary line wrapping within records |
| Br1 fol. 236v | `o:corema.br1.236v` | 1200×1800 JPEG | `a72cc78de70f63b0f6f31916088118da8dfca70c70eafba2ba9a36ea7ca5b55` | three variable blocks; marginal headings and paragraph/initial starts |

These pages show that a semantic event schema can survive different scribal
layout and abbreviation while record boundaries and event wording vary. The
visual facts do not imply that Voynich records are recipes.

## Provenance and exclusions

- Source bytes: `.gdt176/corema/{b4,b6,br1,bs1,gr1,w1}.recipes.xml`, already
  hash-frozen and public.
- Oracle inventory: `gdt176_corema_recipe_inventory.tsv` and
  `gdt176_corema_role_oracle.tsv`.
- The Nuremberg letter books and Ste1 are abbreviation controls, not complete
  recipe-semantic scoring folds here; their already established lesson is that
  wording and expansion may vary without destroying record structure.
- No Voynich illustration, label, token, host, tuple value, or f84 artifact was
  used to derive this ontology.
