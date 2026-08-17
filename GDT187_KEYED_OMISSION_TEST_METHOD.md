# GDT187 — diagram-keyed omission test

## Frozen prediction

GDT186 identifies a historically attested mechanism in Foxton's 1408
*Liber Cosmographiae*: a diagram or list can supply a ciphered technical
headword, while dependent prose omits that noun or renders only part of it.
The Voynich prediction is deliberately semantics-free:

> On nonsealed pages with independently inventoried labels and prose, the
> label PAGE_HOST inventory should be unusually related to the page's prose
> or paragraph-opening formal inventory, even if exact label hosts are not
> repeated verbatim.

This is not a word-meaning test.  A label need not own a nearby drawing and no
label is treated as a noun.

## Inventory

- Frozen label parses: the f84r-free GDT059 HPR2 external inventory, restricted
  to loci whose independent source-role row is `kind=L`.
- Prose: the GDT016 confirmed-prose group inventory.
- All `f84*` rows are rejected from their page/locus prefix before formal
  fields are parsed or retained.
- Eligible pages must have both inventories and belong to a
  section/Currier/hand plus exact pages-per-physical-folio block containing at
  least two folios.  This leaves 23 pages on 11 physical folios.
- Paragraph openings are complete physical lines marked `paragraph_start=1`,
  not just their first source group.

## Fixed representations and endpoints

For labels and each prose scope (`ALL_PROSE`, `PARAGRAPH_OPENING_LINES`), form
five count bags:

1. exact visible source groups;
2. source-group character trigrams;
3. exact PAGE_HOST identities;
4. PAGE_HOST character trigrams; and
5. HPR2 compiler signatures.

The score is mean weighted-Jaccard similarity over the 23 page pairs.  Raw
surface channels are adversarial controls; exact hosts test repetition;
host-character and compiler channels test broader distributed structure.

## Exact null

Permute complete label-page bundles only among physical folios with the same
section, Currier, hand, and exact number of eligible pages.  Within a mapped
folio, sorted page order is preserved.  Exhausting the four blocks gives 432
worlds.  The null preserves every label and prose bag, page count, physical-
folio bundle, register, hand, and target.  Report exact inclusive local tails
and a max-ten standardized tail over both scopes and all five representations.

Section-specific values are descriptive because their exact orbits are only
12 worlds in Pharma and 36 in Biological/Balneological.

## Decision

Call the keyed-omission prediction supported only if a PAGE_HOST or compiler
channel has max-ten `p <= .05`, is positive in both powered sections, and is
not weaker than its corresponding raw-string control.  Otherwise retain any
directional result as an exploratory route only.

The experiment assigns no label ownership, word class, Latin correspondence,
sound, language, plaintext, or meaning.  f84r is not retained, parsed, joined,
or scored.
