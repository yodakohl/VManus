# GDT181 — hybrid technical-compiler translation theory

## Purpose

GDT181 is an abductive theory-generation checkpoint.  It does not run another
selector tournament and it does not call the manuscript translated.  Its job
is to choose the strongest explicit generator compatible with the current
structural, historical-control, semantic, and negative evidence, then expose
exactly what that generator can and cannot translate.

The three compared theory classes are:

1. compressed or heavily abbreviated natural language;
2. predominantly semantic/technical notation;
3. a hybrid in which an address/content layer is compiled through technical
   record, register, and diagram-state notation.

All comparison grades are transparent abductive grades (`0=poor`, `1=partial`,
`2=good`), not probabilities or confirmatory statistics.  The evidence was
already exposed before the grades were assigned.

## Frozen inputs

Only named public results are synthesized.  No transcription table, image,
or sealed formal target is opened by this experiment.  The executable page
reading is reconstructed from the retained GDT179 and GDT180 TSV/JSON
artifacts.  Broader architectural constraints come from the named reports
hash-bound in `gdt181_result.json`.

The three manual transcriptions remain alternate observations of one
manuscript.  Agreement across them is robustness, never replication.

## Leading generator

The leading surface theory is a **page-conditioned hybrid technical
compiler**:

```text
DOCUMENT      := PAGE+
PAGE          := PAGE_PROFILE ADDRESS_INVENTORY RECORD+
RECORD        := ENTRY_STATE? FIELD (CHECKPOINT FIELD)* CLOSE?
FIELD         := WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?
CHECKPOINT    := DY_CLASS
CLOSE         := B3_CLASS

DIAGRAM_LABEL := LOCAL_SELECTOR? LOCAL_ADDRESS LOCAL_STATE_EDGE?
```

`PAGE_HOST` is an opaque address/content candidate.  It is not assumed to be a
word, root, morpheme, number, or concept code.  `WRAPPER`, `INNER_D`,
`POSITION_FRAME`, `RIGHT_FAMILY`, `DY_CLASS`, and `B3_CLASS` are formal
compiler coordinates.  Their exact linguistic or notational functions remain
unknown.

The diagram-label production is licensed only where an independently defined
page schema supplies a finite state inventory.  It does not export local bit
values to prose or to unrelated pages.

## Executable local decoder

For f57v/f77r only, the retained exposed theory uses a two-coordinate
four-state square.  The coordinate reference is register-conditioned:

```text
N1 / f77: 00 COLD, 01 MOIST, 10 HOT, 11 DRY
D1:        00 HOT,  01 DRY,   10 COLD, 11 MOIST
```

On f57 N1 and the f77 segment labels, coordinate 1 is the shallow predicate
`surface starts with ot`; bit 2 is `surface ends with y`.  On f57 D1, bit 1
is `an ok component is present`; bit 2 remains terminal `y`.  These are
overlapping surface predicates, not asserted morpheme boundaries.  The English
quality names identify positions in the independently frozen classical
quality square.  The register-dependent lookup is essential: the first
coordinate denotes Fire incidence in N1/f77 and Water incidence in D1.  No
complete source group is translated as an English word.

The f77 transition reading is then deterministic: adjacent state changes are
classified by their classical incident element, and the unchanged HOT--HOT
boundary is a hold.  This decodes an abstract process topology, not a named
substance, apparatus, recipe, or operation.

## Translation algorithm

1. Reconstruct manual physical groups and source separators; never replace
   them with cleaner pseudo-boundaries.
2. Parse only licensed compiler coordinates and retain the full surface.
3. Identify a finite external page schema without using the Voynich string to
   choose it.
4. Fit or apply a local state code only inside that schema.
5. Translate schema positions and relations; render every unresolved
   `PAGE_HOST` as an opaque address such as `ADDR[f57:N1:NE]`.
6. Promote an address to a lexical/content value only after repeated,
   independently owned referent evidence or a readable homologous table.
7. Require a frozen transfer before exporting a local selector or state edge
   to another page family.

This algorithm is deliberately capable of partial translations.  An opaque
address is a reported unknown, not a license to invent an English word.

## Falsifiers and scope

The theory must preserve, rather than explain away:

- GDT003's very low absolute hidden-cell precision and the failure of the
  named `q` plus right-edge subgroup against string baselines;
- the fact that real medieval abbreviation generates many rectangles and
  reusable edge operations;
- GDT160's broad LEFT×RIGHT incidence excess without GDT161 compact stable
  operation classes;
- the failure of exact PAGE_HOST identity, host neighborhoods, and complete
  external-referent atlases to transfer semantics;
- the failure of the Q20 readable-recipe role projection;
- the post-hoc, one-folio, proximity-owned nature of f57;
- the exposed and nontransferred nature of f77;
- stronger global nonsemantic source coding than any semantic decoder.

The theory weakens if a fresh schema-equivalent diagram rejects the local
state predictions, if compiler coordinates cannot be separated from content
on a readable homolog, or if a simpler source process predicts all licensed
semantic endpoints equally well.

No f84r access is authorized or performed.  GDT181 creates no f84r
prediction.
