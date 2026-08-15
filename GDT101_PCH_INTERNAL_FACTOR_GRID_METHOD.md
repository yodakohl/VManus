# GDT101 — `PCH` internal factor-grid audit

## Question

Does the postselected `PCH` PAGE_HOST family support a reusable internal
factorization, and does that factorization transfer beyond one folio or
register?

This is an exploratory formal audit. It does not assign `PCH`, any left
factor, or any right factor a semantic or linguistic role.

## Frozen source and seal

The source is `gdt062_right_family_inventory.tsv`. Every row whose page starts
with `f84r` is rejected before analysis. The sealed folio is not opened,
retained, queried, joined, scored, or targeted.

The inspected, explicitly postselected factorization is:

```
PREFIX in {EMPTY, o, y}
CORE   = pch
TAIL   in {EMPTY, e, ed, ey, d, y}
HOST   = PREFIX + CORE + TAIL
```

The prefix and tail sets were chosen after inspecting `PCH`; their apparent
fit is therefore not a preregistered discovery statistic.

## Analyses

1. Inventory all 18 exact cells, occurrence counts, folio support, register
   support, and full tokens.
2. Count the 45 possible 2x2 rectangles made by three prefix levels and six
   tail levels.
3. Apply the same fixed prefix/tail frame to every PAGE_HOST trigram occurring
   in at least 50 non-f84 source groups. Rank cores by occupied cells and
   complete rectangles. This is a descriptive postselection diagnostic.
4. Leave each physical folio out. A cell transfers only if the exact cell
   occurs on another folio. Separately flag a combination as factor-predictable
   when its prefix and tail each occur with `PCH` outside the target folio even
   if the exact cell does not.
5. Measure prefix-tail mutual information. Shuffle prefixes within exact
   register x physical-folio cells for 20,000 deterministic permutations.
   Association is counterevidence to strict independent-slot frequencies,
   though it does not erase combinatorial compatibility.
6. Bind GDT003 and count already-published hidden-folio prediction rows that
   involve `pch`. GDT003's string-baseline ceiling remains controlling.

## Interpretation rules

- Complete cells establish compatibility, not semantics.
- Exact-form cross-folio support is also available to a whole-form frequency
  model and is not an algebraic prediction gain.
- A novel cell reconstructible only from separately supported factors is a
  computational lead, not prospective evidence, because this grid was found
  after exposure.
- Prefix-tail dependence weakens a strict independent-slot theory and favors
  conditional rendering/compatibility.
- No result can override GDT003's `LIMITED/LOCAL COMPOSITION ONLY` decision or
  its failure to beat string statistics.

## Claim ceiling

At most this experiment identifies a dense postselected formal factor family
and a concrete unseen-folio combination lead. It establishes no word,
morpheme, POS, sound, language, plaintext, meaning, or translation.
