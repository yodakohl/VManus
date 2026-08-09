# SME001 target-source sequence capacity

## Decision

**PASS — complete-page ray and tail sequences frozen; text features remain unjoined.**

The anonymous matrix excludes one paragraph on f106r because IT2a lacks a physical line retained by ZL3b/RF1b. Removing only that entry would splice two nonadjacent morphology states and corrupt the page's run structure, so the entire 14-entry page is excluded before association scoring. The target-source panel retains 156 intact entries on 12 pages / seven physical folios.

Seven-vs-eight rays retains 149 entries (83 vs 66); every page and all seven folios vary internally. Both odd/even strata remain informative on seven folios, and early/late strata on six/seven. One-vs-two tails retains 155 entries (133 vs 22), with internal variation on eight pages / six folios. Its odd/even and early/late strata retain five/four and four/five informative folios respectively. The one tail-less marker and rare six/nine-ray markers stay in the frozen sequences as ignored third states rather than being recoded.

No text feature value was read or joined. This capacity pass supplies no ray/tail function, root association, meaning, lexeme, plaintext, language, or translation.

## Reproduction

```bash
./vpy experiments/semantic_assumptions/star_morphology_entry/build_sme001_target_source_binding.py
```
