# IV15 dose scope audit — preserve IDEA000421

Status: bounded source correction and writer review; no target access and no
change to `research_registry/proposals/raw_trotula_weighted_dose_equal_parts.json`.

## What the cached source actually says

The complete bounded source inventory is
`TROTULA_COMPLETE_CONTENT_20260920.json` and its report
`TROTULA_COMPLETE_CONTENT_20260920.md` (report SHA256
`0fe2184cd0365f595ec5beda8f98be768bca8dadae6cbdf67e48f9b2b89b1c54`). The
native pages are printed pages 7–9 of the 1544 *Experimentarius medicinae*
copy, manifest `bsb10197839`; their hashes and viewing receipt remain in that
JSON. The owned witness does not establish pre-1420 wording or order.

The exact cached IV15 content is:

> castoreum, white pepper, costus, mint and apium, one drachm each; grind and
> mix with white or sweet wine; give two drachms in the evening.

The sentence has three distinct quantity/role zones:

1. Five dry ingredients each receive `D = one drachm`, so the **quantified dry
   ingredient subtotal** is `5D`.
2. White or sweet wine is an administration medium, but its amount is not
   stated. No mass/volume conservation rule says how much wine enters the
   preparation, whether any evaporates, or whether “two drachms” is measured
   before or after the wine is added.
3. “Two drachms in the evening” is an administration dose with a time
   argument. It cannot be converted to `2/5` of the preparation from this
   sentence alone.

The earlier raw card's `MIX total=5D` is therefore safe only when read as the
dry-component subtotal. Its `dose_fraction=2/5` is too strong unless an extra
assumption identifies the dose denominator with that dry subtotal. This audit
does not edit the raw bytes; it records the scope correction for any future
review.

IV16 supplies a useful control: “one drachm **or** two spoonfuls” is an
explicit alternative. It does not state that a drachm equals two spoonfuls.
V19 likewise gives two ingredients at `D` and myrrh at one scruple, but no
administration dose. V11 gives equal ingredient parts and a later boil with
two parts consumed, but no starting volume. These statements must not be
combined to manufacture a unit conversion.

## Smallest source-complete writer

A finite source writer can retain IV15 without filler by using typed roles:

```text
IV15_ALT(
  ingredients=[castoreum, white_pepper, costus, mint, apium],
  dry_amount_each=D,
  action=GRIND,
  medium=CHOICE(white_wine, sweet_wine),
  action2=MIX,
  administration=DOSE(amount=2D, time=EVENING)
)
```

The only safe arithmetic assertion is:

```text
dry_subtotal = D + D + D + D + D = 5D
```

The writer deliberately does not emit `final_preparation_mass`, a wine
amount, a dry-to-wet ratio, or a fraction of the preparation. If a future
source adds a wine quantity `W` and states a conserved mass model, an extended
writer could expose `final_mass = 5D + W`; IV15 itself does not authorize that
extension.

The complete neighboring alternative is retained as a disjunction:

```text
IV16_ALT(
  ingredient=dried_cumin,
  administration=CHOICE(DOSE(amount=1D), DOSE(amount=2H)),
  route=DRINK
)
```

`H = spoonful` remains an unknown positive unit relative to `D`. The writer
does not equate the alternatives. It also retains the source distinction
between preparation medium and administration amount; a future target writer
would have to realize both roles under one global rule.

## Observable rival consequences

Three fixed source interpretations differ:

| Model | IV15 meaning | Consequence if a source later states medium quantity |
|---|---|---|
| `DRY_SUBTOTAL_DOSE` | 5D dry subtotal; 2D dose measured from dry preparation before wine | dose can be compared to 5D, but wine is outside the dose quantity |
| `MIXTURE_DOSE` | 5D dry inputs plus an explicitly measured wine amount; 2D dose after mixing | dose is a fraction of the finished mixture only when wine amount and loss are written |
| `PER_COMPONENT_DOSE` | two drachms per ingredient | dry input is 10D, contradicting the ordinary total-dose reading |

The cached IV15 sentence does not contain the medium quantity needed to choose
the first two models. `PER_COMPONENT_DOSE` changes the role of “two drachms”
and is a named rival, not a silently rejected straw man. The smallest decisive
source observation would be an explicit quantity attached to the wine or an
unambiguous phrase saying whether the dose is powder or prepared liquid.

## Target binding and stopping point

The existing Trotula comparison already records exposed f82r/f83r coverage in
`TROTULA_COMPLETE_CONTENT_20260920.md`. It found no independently visible
dose, ingredient-count, medium-quantity, or evening/time binding. No new target
rows or images were opened for this audit. Consequently the source writer has
no target-owned consequence to test: assigning any f82r/f83r form to `D`, wine,
`2D`, or evening would be a new unsupported gloss.

The exact remaining debt is source-side as well as target-side: IV15 lacks the
wine quantity and dose scope; the 1544 witness may not preserve earlier wording;
and no target construction binds the typed roles. A future target test would
need a complete report-owned passage that independently writes a preparation
medium, an administration amount, and a temporal administration condition.
Without that relation, this audit stops at the typed source writer and does not
add another raw proposal.

## Root assessment before GDT1000 registration

The source correction from5D finished mixture to5D dry subtotal stands.
The per-component dose is an added unsupported rival, not a linguistically
equal ambiguity: the later administration phrase does not repeat `ana`.
The source does not license replacing the five1D inputs with five2D inputs.

The preceding requirement for independently translated target dose/medium/time
roles before any fit is stricter than the user's permitted exploratory phase.
A complete explicit shared writer may test hypothesized roles jointly. Such a
fit remains provisional and cannot confirm names or units by itself. GDT1000
uses this permission, with complete IV15/V19 source ownership, separate quantity
word formation, all exposed paragraph pairs, no old glosses and no reserve use.
It tests neither the raw2/5 assertion nor the unsupported per-component rival.
