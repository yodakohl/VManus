# DIRECTIONPLACEMENT001 prescore control report

Date: 2026-08-09

## Status

**PASS — one frozen target invocation authorized, target unrun.**

The validated source panel was reduced without reading a Voynich string to 16
source-order-balanced east/west pairs (32 loci) on six physical folios. The
published masked panel contains A/B sides but no direction column. An
independent source reconstruction passes 12/12 pairing checks, including one
EAST and one WEST source row per pair.

The target-blind text build binds exactly 96 manual-transcription rows: 32
loci times ZL3b/IT2a/RF1b. All are label-kind `DIAGNOSTIC_NONPROSE` rows with
exact page and code agreement. The frozen support and within-pair-variation
rules retain 13 formal features: 4 literal within-token fragments, 3 parsed-
root forms, and 6 structural-role forms. These are feature identifiers, not
English glosses.

All 65,536 synchronized pair swaps are enumerated. Fifteen registered controls
pass, including folio equal weighting, exact two-sided complement ties,
inclusive tails, alternate-reading disagreement collapse, token-length-only
cancellation, pair-constant cancellation, distributed cross-context
robustness, rejection of a one-folio signal, mutated panel guards, finite
family orbits, and target absence.

A nonimporting implementation independently reconstructs the bindings,
32-locus/96-row contract, feature list, feature matrices, full orbit, family
quantiles, synthetic controls, mutation guards, and target-absence state in
20/20 checks.

## Prescore corrections

The first control implementation described its cross-context fixture too
strongly: it checked that f68/f88 were present but did not call the actual
structural gate. That fixture was replaced before validation and before target
access; the final distributed fixture passes the gate function and the
one-folio fixture fails every structural subgate.

The first independent-validator invocation then stopped before writing an
artifact. Its disagreement expression used a deprecated NumPy call form, and
NumPy boolean values were not JSON serializable. No observed direction or
target score was read. The independent disagreement construction was repaired
with an explicit three-reading stack and check values were converted to scalar
booleans. The repaired validator passes 20/20.

## Claim ceiling

The controls contain no target result and no semantic finding. A later pass
could establish only placement-associated morphology, which could still be a
layout or scribal effect. It cannot alone establish an EAST/WEST word,
ownership, a lexeme, plaintext, language, or translation.

## Reproduction

```bash
./vpy experiments/semantic_assumptions/directional_label_placement/build_masked_pair_panel.py
./vpy experiments/semantic_assumptions/directional_label_placement/validate_masked_pair_panel.py
./vpy experiments/semantic_assumptions/directional_label_placement/run_directional_label_placement.py --mode controls
./vpy experiments/semantic_assumptions/directional_label_placement/validate_directional_label_controls.py
```
