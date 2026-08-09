# F77r four-state transition bridge

## Result

**PROVISIONAL post-hoc cross-page construction; not a translation.**

The f57v quality-position analysis had already fixed a local two-bit rendering:

```text
starts-ot, terminal-y
10 = HOT-position state
01 = MOIST-position state
00 = COLD-position state
11 = DRY-position state
```

Applying those unchanged structural bits to the six human-ordered labels in
the six segments of the f77r top tube gives the same sequence in ZL3b, IT2a,
and RF1b:

```text
COLD — DRY — HOT — HOT — MOIST — COLD
```

The five side openings are the boundaries between those segments. Official-
witness topology QC, consistent with the cached human description, gives four
emitting flanking openings and one non-emitting central opening.

| Opening | Adjacent f57-derived states | Drawing state | Classical pair |
|---|---|---|---|
| branch 1 | COLD + DRY | emits | EARTH |
| branch 2 | DRY + HOT | emits | FIRE |
| branch 3 | HOT + HOT | does not emit | none |
| branch 4 | HOT + MOIST | emits | AIR |
| branch 5 | MOIST + COLD | emits | WATER |

Thus all five boundaries obey **emission if and only if the structural state
changes**. The four changes instantiate each classical adjacent-quality pair
exactly once; the sole unchanged pair is the sole non-emitter.

This is the strongest current cross-page semantic-structure lead because it
explains an author-visible relation, not merely a similar spelling. It was,
however, discovered after inspecting f77r and therefore cannot confirm itself.

## Specificity and controls

With the observed multiset fixed at two COLD-position states, two HOT-position
states, one DRY-position state, and one MOIST-position state, only 4 of 180
distinct assignments to the six fixed segments pass the complete rule. Across
all `4^6 = 4,096` state sequences, 8 pass. These are descriptive exact counts,
not confirmatory p-values.

Among 184 stable consecutive six-label windows in the cached human annotation
units, f77r is the only window passing the complete classical-pair gate. One
f68r1 star-label window also passes a broader four-distinct-edge pattern, but
it includes the non-classical HOT+COLD opposition and fails the exact gate.
This look-alike remains an important control against calling every four-state
cycle semantic.

An independent implementation imports no production code and passes 28 input,
topology, state, null, window, counterevidence, and decision-ceiling checks.
Two complete audit/validation runs reproduced byte-for-byte.

## Counterevidence

The cached later visual proposal calls the four puffs, left-to-right, AIR,
WATER, FIRE, EARTH. The transition-pair construction predicts EARTH, FIRE,
AIR, WATER at those same positions: **zero of four agree**. That proposal is
explicitly marked non-role-evidence in the source atlas, so it neither selects
nor rotates the construction, but the mismatch blocks a direct element-label
gloss—especially at the red puff.

## Interpretation ceiling

Retain only this provisional statement:

> The f57-derived two-bit state system transfers without alteration to the six
> f77r tube-segment labels, where state changes coincide exactly with emitting
> openings and cover the four classical adjacent-quality pairs once.

Do not conclude that the segment labels are the words COLD, DRY, HOT, or MOIST;
that the puffs are named EARTH, FIRE, AIR, or WATER; or that `ot` and terminal
`y` mean a quality or change. Confirmation requires a second independently
annotated segmented system whose topology and test are frozen before its
Voynich strings are opened.

## Reproduction

```text
./vpy experiments/semantic_assumptions/f77r_quality_transition_bridge/audit_f77r_quality_transition_bridge.py --output experiments/semantic_assumptions/results/f77r_quality_transition_bridge.json
./vpy experiments/semantic_assumptions/f77r_quality_transition_bridge/validate_f77r_quality_transition_bridge.py --output experiments/semantic_assumptions/results/f77r_quality_transition_bridge_validation.json
```
