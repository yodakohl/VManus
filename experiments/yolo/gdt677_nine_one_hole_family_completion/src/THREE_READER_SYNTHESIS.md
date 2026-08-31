# GDT677 three-reader synthesis

Three deliberately different readers were given the same nine surfaces and all
twenty exact occurrences.

1. A late-medieval recipe copyist / stem compositor prioritized reuse of the
   current visible component inventory. This reader preferred a nominal
   `ykcho`, `lo+sair`, and a locally licensed portion-I middle in `taiky`.
2. A practical medicine preparer prioritized complete executable line sense.
   This reader preferred action `ykcho`, result `kchody`, `lo+sair`, and a
   cold-to-lightly-reheated state for `taiky`.
3. A historical apothecary reader compared the proposed information types with
   antidotaries, books of degrees, weight registers, drug lists and recipe
   miscellanies near the target period. This reader preferred action `ykcho`,
   reader-split `los+air`, and a less numerically specific learned `taiky`.

The final synthesis does not average these proposals. It selects the reading
that explains the most already-visible structure with the fewest new rights:

- `ykcho` is the action **hieraus einen heiß-trockenen Ansatz bereiten**.
  Existing `y-` already has the high-confidence anaphoric-imperative role before
  process heads. All four occurrences tolerate the action; `f56r.6` therefore
  changes from `NOMINAL_REGISTER` to `MIXED_RECORD`. The nominal reading remains
  the explicit strongest rival.
- `kchody` is the paired result **fertiggestellter heiß-trockener Ansatz**.
  The contrast between initial `y` and terminal `dy` now predicts instruction
  versus finished preparation instead of assigning two unrelated wholes.
- `losair` defaults to **zweite Fraktion des Drogenholzpostens** because RF1b
  visibly splits `los air`, and both split members already have exact cards.
  Unsplit `lo+sair` = **Holzabsud mit Samenfraktion II** remains an equally
  compositional but reader-weaker rival.
- `taiky` is **kalt angesetzte Charge, leicht angewärmt**. Only outer `t` and
  terminal `ky` are treated as transparent. Internal `ai` stays opaque and
  receives no productive dictionary right.

The other five decisions converged across all three readers:

| surface | final working meaning |
|---|---|
| `ltaiin` | Holzdroge, kalt auf Stufe III |
| `oltaiin` | Holzdrogenansatz, kalt auf Stufe III |
| `olchain` | Holzdrogenansatz, trocken auf Stufe II |
| `lolkaiin` | Holzstoff, heiß auf Stufe III |
| `aror` | eine Portion der ersten Drogenfraktion |

All nine cards are exact-whole defaults. Their component analyses predict
explicit sister contrasts, but they do not silently assign substrings in new
words. The twenty occurrence decisions in `OCCURRENCE_CONTEXT_SPECS.tsv` are
the manual semantic input; the builder checks their coverage, reader support,
token preservation and renderer consequences.
