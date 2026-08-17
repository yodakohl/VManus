# GDT180 — f77 process-translation synthesis report

Status: **PROVISIONAL_F77_QUALITY_STATE_PROCESS_READING**

## Best current reading

The six labelled compartments across the f77r top structure form a provisional
quality-state process:

```text
COLD --EARTH transition/output--> DRY
DRY  --FIRE transition/output-->  HOT
HOT  --HOLD / no output-->        HOT
HOT  --AIR transition/output-->   MOIST
MOIST--WATER transition/output--> COLD
```

This synthesis does not introduce a new glyph rule.  It composes GDT179's
page-local f57 state decoder with the already retained f77 segment and opening
inventory.

## Segment reading

| Step | Locus | ZL3b / IT2a / RF1b | Frozen bits | Provisional state |
|---:|---|---|---:|---|
| 1 | f77r.2 | `olkchs` / same / same | 00 | COLD |
| 2 | f77r.3 | `otedy` / same / same | 11 | DRY |
| 3 | f77r.4 | `otork` / same / same | 10 | HOT |
| 4 | f77r.5 | `otol` / same / same | 10 | HOT |
| 5 | f77r.6 | `dchdy` / `dchdy` / `dch y` | 01 | MOIST |
| 6 | f77r.7 | `soral` / same / same | 00 | COLD |

The surface strings are diplomatic observations, not proposed plaintext.
Their shared coarse states survive all three readings.

## Transition reading

| Boundary | State pair | Classical incidence | Visible output |
|---:|---|---|---:|
| 1 | Cold + Dry | Earth | yes |
| 2 | Dry + Hot | Fire | yes |
| 3 | Hot + Hot | none / hold | no |
| 4 | Hot + Moist | Air | yes |
| 5 | Moist + Cold | Water | yes |

The four changing boundaries instantiate each classical adjacent-quality pair
once.  The one unchanged boundary is the one non-emitter.  This supports a
technical transition diagram more coherently than six unrelated object names.

The most economical abductive interpretation is that the labels specify
coarse states and the side structures mark state-changing operations or
outputs.  The duplicated Hot state is then a hold, continuation, or repeated
stage.  The exact physical substance and operation remain unknown.

## Why this is useful

This reading explains at once:

- why two distinct complete groups can share the same state (`otork`, `otol`);
- why the same coarse state can recur at both ends with unrelated surfaces;
- why four openings emit and the central one does not;
- why the four changes cover Earth, Fire, Air, and Water exactly once;
- why whole-form similarity is not the governing signal.

It also suggests a division between a compact state/compiler layer and a
larger content/address layer, consistent with the manuscript-wide structural
work without pretending that the latter has been read.

## Counterevidence

The result is post-hoc.  It has not transferred to a second frozen segmented
system.  A cached visual proposal ordered the four visible puffs as
Air–Water–Fire–Earth, which agrees with this transition order at zero of four
positions.  The proposal is not qualified role evidence, but it prevents
calling the puffs named elements.  Complete-form f57↔f77 identity is also poor,
and the f67v1 attempt to make emission-if-change universal failed.

Accordingly, `otedy` is not translated as “dry,” `dchdy` is not translated as
“moist,” and no branch is translated as a material.  These are provisional
diagram states and transition classes only.

## Novel predictions

1. A second independently owned same-system segmented diagram should emit only
   where adjacent coarse states differ.
2. A readable legend for the four emitting boundaries should order the
   corresponding classes Earth–Fire–Air–Water, with no class at the central
   repeated-Hot boundary.
3. Independent evidence should treat steps 3 and 4 as the same coarse state
   with different content or stage identity.
4. The two ends should remain the same coarse state despite different complete
   groups.

## Conclusion

GDT180 supplies a second provisional semantic scaffold: the f77r top diagram
is best read as a six-stage quality-state process with four element-class
transitions and one non-emitting Hot hold.  It is substantially more concrete
than “record-like text,” but it remains a page-local, exposed theory.  It does
not yet identify a lexical item, operation, substance, language, sentence, or
manuscript-wide plaintext.  f84r remains sealed.
