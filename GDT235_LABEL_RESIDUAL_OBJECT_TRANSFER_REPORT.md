# GDT235 — label residual to visible object-class transfer

## Result

**LABEL_RESIDUAL_OBJECT_CLASS_NOT_TRANSFERABLE_SECTION_DOMINATES**

Removing the transferred GDT233 graphical-label prefix does not expose a
cross-folio visible-object dictionary.  On 703 non-f84, family-covered human
label annotations from 23 physical folios, exact residual lookup covers 323
held-folio rows and predicts 156 correctly (`.483`).  The section-matched
majority predicts 233 of those same rows (`.721`), a `-.238` accuracy delta.

The comparison is not rescued by keeping the whole family or by using only the
transferred prefix:

| representation | covered | feature correct | feature accuracy | matched section accuracy | delta |
|---|---:|---:|---:|---:|---:|
| RAW_FAMILY | 311 | 155 | .498 | .733 | -.235 |
| STRICT_RESIDUAL | 323 | 156 | .483 | .721 | -.238 |
| TRANSFERRED_PREFIX | 293 | 164 | .560 | .765 | -.205 |

The endpoint is deliberately coarse: `PLANT`, `WATER_OR_APPARATUS`,
`ASTRONOMICAL`, `FIGURE_ONLY`, or `OTHER_LABEL`.  These are source-bound atlas
classes, not word meanings or authorial ownership claims.

## Section-held sensitivity

Exact families and residuals have small aggregate gains over a global majority
when an entire section is held out (`+.123` and `+.077`).  That apparent gain
does not transfer to the q13/B material that motivated the test: on covered
q13 rows, raw family, residual, and prefix lookup each make **zero** correct
object-class predictions (41, 39, and 35 covered rows respectively).

This combination is diagnostic.  Exact family material recurs across broad
catalogue classes, but its class association is dominated by manuscript
section/register ecology.  It is not a stable object-name layer that can be
read across the manuscript.

## Consequence for the working theory

GDT233 remains evidence for a partial graphical-label rendering/compiler
layer.  GDT234 showed that removing that layer destroys most within-unit formal
similarity; GDT235 now shows that the remaining exact residual does not recover
even a broad transferable object class.  The current architecture is therefore
better represented as:

`GRAPHICAL_LABEL_RENDERING + REGISTER_BOUND_OPAQUE_RESIDUAL`

than as:

`LABEL_MARKER + OBJECT_WORD`.

This is a real narrowing of the theory.  It blocks reading BACA-like label
families or their stripped tails as water, plant, astronomical object, figure,
or apparatus terms.  It does not imply that labels lack content; it says that
exact residual identity is not the transferable content key in the present
human atlas.

## Claim ceiling

The experiment predicts only coarse visible annotation classes.  It establishes
no label ownership, object name, word, morpheme, sound, language, plaintext, or
translation.  No f84 row was retained, joined, or scored, and no new f84 access
occurred.
