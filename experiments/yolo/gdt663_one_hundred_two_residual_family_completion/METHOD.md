# GDT663 method

## Question

Can the 105 V39 one-hole lines be completed by one internally consistent
mixture of productive compounds, learned recipe words, measures and
entry/label forms, without assigning any target position a generic work-word
placeholder?

## Inputs

- GDT662 V39 glossary, dictionary, line coverage, completed and one-hole
  passages, target-occurrence audit and the 105-row newly exposed frontier.
- The same exact 179-page panel used by GDT662.
- ZL3b token rows and the ZL3b/IT2a/RF1b line table, materialized only through
  `./vmanus-exp query-tsv` with explicit page allow-values and both `f84` and
  `f84r` forbidden before row materialization.

## Method

1. Route-check the 102-form target set against earlier experiments.
2. Have three independent readers construct complete cards: a practical
   fifteenth-century apothecary, a mixed codebook compositor and a passage
   reader concerned with usable German recipe prose.
3. Prefer the smallest compositional family that accounts for a form. Keep a
   learned whole where decomposition would merely smuggle in an unsupported
   substring value. Every form receives a default and an explicit rival.
4. Preserve V39 structural token glosses unchanged outside the 102 targets.
   Apply concrete German renderer substitutions only in the separate passage
   column; in particular practical `ol` becomes `Grundansatz` rather than the
   inherited structural meta-description.
5. Treat free `l` separately from bound initial `l-`. For every `l` position,
   search the two alternate readings for an actually attested adjacent join.
   A visible `o|l -> ol`, `qo|l -> qol` or `l|X -> lX` receives an
   occurrence-scoped merge card. Outside such joins, free `l` receives the
   learned weight-siglum default `Pfund`; bound `l-` remains the inherited
   Holzdrogenkopf.
6. Rebuild all 4,128 lines, all complete passages, all one-hole passages and
   the working dictionary. Verify that all non-target token projections are
   byte-stable, then replay every generated result file in a temporary
   directory.

## Decision rule and claim ceiling

Pass when all 1,105 target positions and all 105 frontier rows are concrete;
the target counts agree with the guarded source; no generic work filler or
structural `ol` meta-gloss enters practical prose; every alternate-reader
`l` merge is visibly attested; non-target token gloss/source/scope projections
remain identical; and the independent validator plus byte replay pass.

The result is an aggressive working translation, not established plaintext.
`alkal=Laugensalz`, `sol=Salz`, free `l=Pfund`, `ylg=Holzgefäß`, `sg=Rückstand`
and `deeeese=ruhen lassen` are deliberately concrete low-confidence cards.
They may remain until a sibling form or future page makes them impossible or
a replacement explains more material. No language, phonetics, exact plant,
disease, new page, new image, `f1r`, `f84` or `f84r` is claimed.
