# GDT694 — closing the 22 residual fraction cards

## Outcome

GDT694 closes the explicit remainder left by GDT693. All 22 inherited exact
cards containing the renderer word *Fraktion* now use the selected indexed
material-share head. Across the complete fixed edition the count changes as
follows:

| channel | V66 | V67 |
|---|---:|---:|
| token positions | 22 *Fraktion*-bearing words | 0 |
| rendered lines | 22 *Fraktion*-bearing words | 0 |
| *Anteil*-bearing words, token channel | 57 | 79 |
| *Anteil*-bearing words, line channel | 56 | 78 |

Exactly 22/479 token positions and 17/51 lines change. The other 457 token
glosses remain byte-identical. The output remains on the same 36 pages, with no
f84/f84r access.

## What improved beyond replacing one noun

The useful result is a tighter compositional account, not the zero count by
itself.

`char` and `chair` now form the direct local pair *trockener Drogenanteil I /
II*. `saraiin` becomes *drei Teile des Samenanteils I*. Commands keep their
actions: `fdar` is *Blütenanteil I abmessen* and `qochar` is *trockenen
Drogenanteil I nehmen*. Long bodies keep their learned heads: `polairy` uses
`POL+AIR+Y`, not an invented free `P+OL`; `losair` follows RF1b's actual
`LOS|AIR` boundary.

Three cards are expressly not made productive. `arl`, `lldar` and `chear`
receive normalized whole-form glosses only. This is the intended mixture of
learned technical words and reusable components: German output may share the
head *Anteil* without pretending that every occurrence proves the same free
segmentation.

## Corrected high-risk forms

The three manual perspectives converged on several corrections:

- `okeeodar`: the previous phrase combined an *Auszug* block with
  *abgemessen*, spending one written `d` twice. V67 selects *Anteil I des
  vollständig erhitzten Auszugs* and keeps *abgemessener Anteil I des
  vollständig erhitzten Ansatzes* as the alternate bracket.
- `araram`: RF1b writes `ar aram`, while GDT680 explicitly avoided an
  unsupported doubling. V67 renders *Drogenanteil I; davon ein Maß*. The
  stricter recursive rival—*ein Maß des Unteranteils I des Drogenanteils I*—is
  preserved in the apparatus.
- `chdar`: I belongs to the R-index. The main is now *abgemessener trockener
  Drogenanteil I*, without reusing I as an added initial stage.
- `chear`: the exact whole remains nonproductive. GDT639 pays only for a bound
  `CH+E` dry shell, so V67 reads *trockener Drogenanteil I* and does not invent
  an independent E-stage.
- `l|karchees`: the line renderer consumes both written units once as
  *vollständig getrocknete Charge aus Anteil I der erhitzten Holzdroge*.

These decisions leave the strongest alternatives visible rather than hiding
them behind a fluent sentence.

## Example lines

The f10r.2 inventory now contains the clean I/II pair:

> Eine abgemessene Portion bis zur Mittelstufe trocknen; eine Portion
> Krautansatz; trockener Drogenanteil I; trocken-kalt am Gradanfang;
> Ansatzcharge; trockener Drogenanteil II; nachgekühlter Trockenstoff im
> Ansatz; heißer Ansatz am Anfang des Grades; Qualitätsgrad III des erhitzten
> Ansatzes; bis Mittelstufe gekühlte Zubereitung, abgeschlossen.

The RF1b-bound quantity at f86v6.25 ends:

> … fertig getrocknete Blütenmasse; heiß, Grad III; Drogenanteil I; davon ein
> Maß.

The corrected f86v6.4 span reads:

> … abgemessener trockener Drogenanteil I; vollständig getrocknete Charge aus
> Anteil I der erhitzten Holzdroge; Anteil I des heißen Holzansatzes; ein Maß
> Rohdroge I.

The artifact working edition prints all 51 lines, not only these changed
examples.

## Preservation and validation

All 113 inherited verb ordinals retain their exact presence/absence profile;
110 contain the exact listed form before and after V67, and three retain their
already inflected/non-exact surface profile. All six inherited local
Holzauszug rivals remain byte-identical. The two earlier quantity spans and the
new wood-charge span are disjoint.

The independent validator passes 21 checks. It reconstructs V66 and V67 from
their token channels, confirms all critical main/rival decisions, checks input
and output hashes, and byte-replays all twelve generated files in a clean
temporary directory.

## Next route

The nominal vocabulary is now terminologically uniform enough to stop another
head-renaming loop. The next pass should freeze all 479 V67 token glosses and
three spans, then improve only clause realization: distinguish inventory/list
lines from executable procedure lines and supply grammatical objects and
carry references without inventing new nouns, verbs, pages or substring
values. The test is whether the resulting paragraph reads as a practicable
sequence while every token decision remains traceable to V67.

V67 remains a working theory, not recovered plaintext.
