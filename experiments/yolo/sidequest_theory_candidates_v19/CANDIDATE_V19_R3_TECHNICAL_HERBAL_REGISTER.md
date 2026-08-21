# Candidate V19 R3 — technical source-register reconstruction

## Result

The four Herbal pages can be read as a compact article register with one active pictured OWNER, an inherited preparation BATCH, a CURRENT PORTION and short material bookings. All 100 events and all 66 exact cards receive concrete defaults. The 55 singleton cards do not require 55 semantic inventions: they occupy eleven operational drawers.

The most important correction to V18 is exact card `d665560...`: it occurs on f11r and f56r beside visibly different plants, so `local-name-D6655` cannot be a literal plant name under the one-card/one-default rule. I select **of the pictured simple itself**, a page-bound OWNER pointer. This is a genuine contradiction-driven revision, not substring inference. A second Herbal-local correction changes f56r `cheeckhody` from a biological `outlet` reading to **bind it in place overnight; close**, because no apparatus or outlet is visible or required in the Herbal article.

## Register model taught to a scribe

1. The drawing silently establishes OWNER; the first booking may name or describe it.
2. A material/part card loads PART; a medium card loads MEDIUM.
3. A preparation card transforms OWNER/PART into BATCH.
4. AIIN recalls the usual measure; Y points to the current portion.
5. CHO/SHO advances to the next material booking; it does not itself identify root, wine or leaf.
6. WITH/SAME-BATCH cards preserve BATCH across a new operation.
7. A close commits only the current substep; a sentence and article may continue across physical lines.

This is learnable without modern database machinery: it is the ordinary memory discipline of a recipe/register clerk using repeated abbreviated whole formulas.

## Visible freeze and historical family guesses

The four drawings were inspected and frozen before article assignment in `V19_R3_VISIBLE_PLANT_FREEZE.tsv`. Exact species identification is not required. The primary working families are twin-tubered blue composite (f10r), mat-forming violet-like simple (f11r), broad-leaved water-edge simple (f55v), and many-headed thistle-like simple (f56r). Their broader fallbacks are retained in the freeze.

This register is historically ordinary in shape even though none of its card meanings is established. The early-fifteenth-century illustrated Herbal [Codex Bellunensis](https://www.english.cam.ac.uk/research/plantlife/digitised-manuscripts/) and the c.1440 [Sloane 4016 *Tractatus de herbis*](https://wellcomecollection.org/works/mcfn4abu) show that illustrated simples books belong in the period. The related *Circa instans* tradition organizes entries around qualities, names/synonyms and medicinal action, while the Egerton 747 compilation even contains a substitution list for unavailable ingredients ([British Library catalogue](https://searcharchives.bl.uk/catalog/032-001983805)). Those comparisons license the compact article inventory; they do not identify any depicted species or Voynich card.

## Economy

- visible events: 100/100
- exact Herbal card types: 66/66
- recurrent types: 11/11 with one fixed default each
- singleton comparisons: 55/55 with two concrete rivals each
- operational drawers: 11
- explicit contextual silent arguments: pictured OWNER; active BATCH; afflicted PLACE in outward applications
- invented one-off diseases: 0
- invented one-off exotic ingredients: 0

## Failure conditions

This reconstruction weakens if another authorized page forces `d665560...` to be a stable named substance rather than a picture pointer, if CHO/SHO occurs where no following material booking exists, or if the f11r double-straining sequence proves to be purely descriptive. The defaults remain in force until a better complete article deck replaces them.

## Files

- `V19_R3_VISIBLE_PLANT_FREEZE.tsv`
- `V19_R3_HERBAL_CARD_DICTIONARY.tsv`
- `V19_R3_100_EVENT_INTERLINEAR.tsv`
- `V19_R3_SINGLETON_ALTERNATIVES.tsv`
- `V19_R3_COMPLETE_HERBAL_ARTICLES.md`
- `build_v19_r3_herbal_register.py`

f84 and f84r were not accessed.
