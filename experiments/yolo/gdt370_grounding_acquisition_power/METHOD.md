# GDT370 prospective grounding-acquisition power design

Status: **FROZEN BEFORE SIMULATION**.

## Question

How large must a future provenance-clean visual grounding panel be before a
stable visual↔formal relation can survive the exact failure mode seen in
GDT368–369: an impressive post-selection dependency that reverses across
arrays or disappears under held-folio transfer?

This is a synthetic design calibration. It opens no new Voynich transcription,
formal row, annotation, image, or f84 material and assigns no meaning.

## Fixed simulated acquisition family

Each simulated panel contains balanced three-state visual observations nested
in physical arrays and folios. One binary formal predicate is potentially
associated with the ordered visual state; 80 binary distractors make a fixed
81-candidate search family, matching GDT368's three endpoints × 27 unique
masks.

The grid is fixed before simulation:

- physical folios: 4, 6, 8, 10, 12;
- arrays per folio: 1 or 2;
- cells per array: 6 or 9;
- 256 deterministic trials per design/scenario;
- two entire folios are always untouched validation folios;
- candidate selector cost: `log2(81)` bits.

The one potentially associated predicate has base prevalence 0.35 and a
logistic ordered-state coefficient:

- `NULL`: beta 0;
- `WEAK`: beta 0.5;
- `MEDIUM`: beta 0.9;
- `STRONG`: beta 1.3.

Every predicate also receives independent folio and array prevalence shifts.
Distractors receive the same prevalence heterogeneity but no visual-state
effect. In `STABLE` worlds the coefficient has one direction everywhere. In
`REVERSING` worlds its direction is independently balanced across folios. The
random generator and ordering are fixed by seed `37020260819`.

## Discovery and validation

Only discovery folios are used to:

1. rank all 81 predicates by the smoothed in-sample reduction in binary
   codelength from three visual-state rates relative to one prevalence rate;
2. freeze the winning predicate; and
3. estimate its Jeffreys-smoothed state-specific and state-blind rates.

The selected predicate is then scored on the two untouched folios. A trial
passes only when:

- aggregate held gain minus `log2(81)` is positive; and
- raw held gain is positive on **both** untouched folios.

For calibration, the simulator can see whether the selected predicate was the
planted one. A successful detection requires both correct selection and the
held pass. A wrong-predicate pass is counted separately.

## Prospective acquisition gate

A design is adequate only if all three predeclared conditions hold:

- `MEDIUM/STABLE` successful-detection rate is at least 0.80;
- `NULL` any-pass rate is at most 0.05; and
- `MEDIUM/REVERSING` any-pass rate is at most 0.10.

Among adequate designs, choose the smallest total cell count, then fewer
folios, fewer arrays per folio, and fewer cells per array. If no tested design
passes, report that explicitly rather than relaxing a threshold.

The recommended real acquisition must additionally have complete physical
arrays, visual-state mobility inside multiple arrays, a fixed topology-aware
null suited to those arrays, and at least two untouched physical folios.

## Claim ceiling

GDT370 can specify acquisition capacity and quantify false-lead risk only. It
cannot establish a Voynich association, semantic role, object identity, word,
morpheme, language, plaintext, meaning, or translation. f84 is ineligible.
