# GDT253 — renderer/residual position calibration method

## Question

GDT252 noticed, after exposure, that `okalal` on f70v1 and `okalam` on
f72r1 share the source-family construction `AQAB+AB` and occupy catalogue
slot 4/10.  GDT253 asks whether this is exceptional after searching the full
frozen ten-slot inventory.

## Frozen universe

The universe is every formally covered locus in the eight previously
human-inventoried ten-slot arrays whose family has a GDT233 transferred prefix.
No visual category, slot, renderer, or residual is added.  The renderer
signature is the ordered source-native STA member-code prefix corresponding to
the transferred family prefix; the right component is the already published
strict family residual.  Results are computed separately for ZL3b, IT2a, and
RF1b.  Alternate readings are sensitivities of one manuscript, not samples.

The primary statistic is the largest number of distinct physical folios on
which any renderer/residual pair occupies the same catalogue slot.  This
maximizes over every eligible renderer, residual, and slot, so the noticed
`okal+AB` pair receives no privileged status.

## Nulls

Two fixed 65,536-world nulls are used for each reading:

1. `INDEPENDENT_RENDERER_RESIDUAL_WITHIN_ARRAY` independently permutes the
   observed renderer signatures and residuals over the eligible positions
   within each array.  It preserves array coverage, positions, individual
   renderer frequencies, individual residual frequencies, and folios, while
   destroying their specific pairing and position conjunction.
2. `WHOLE_PAIR_POSITION_WITHIN_ARRAY` permutes intact renderer/residual pairs
   over the eligible positions within each array.  It tests positional
   concentration conditional on the observed pair inventory.

Inclusive Monte Carlo p-values use `(1 + exceedances)/(1 + worlds)`.  They are
exploratory max-search diagnostics, not confirmation: the source universe and
the `AQAB+AB` observation were already exposed, and catalogue slot indices are
not proven authorial degree coordinates.

No f84 input is read, retained, joined, or scored.
