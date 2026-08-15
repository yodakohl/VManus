# GDT036 — ch/che/sh matched-host wrapper functions

## Question

Do the observed left-edge strings `ch`, `che`, and `sh` behave only as core-specific spelling choices, or do they retain shared constructional preferences after the exact residual host is fixed?

This experiment is formal and language-agnostic. It does not assign meanings, sounds, morphemes, parts of speech, or technical functions.

## Frozen source and exclusion

The sole event source is `gdt016_group_state_inventory.tsv`: physical/manual source groups on which ZL3b, IT2a, and RF1b agree, already classified into anonymous GDT016 record states. These editions are alternate readings of one manuscript, never independent observations. The source is f84-free; the runner asserts that no `f84r` row is read into the analysis.

For every group whose observed `stripped_prefix` is exactly one of `ch`, `che`, or `sh`, the already-recorded `residual_host` is the matched core. A host is eligible when it has at least 10 wrapper occurrences, at least two wrapper types, and at least three physical folios. The thresholds are fixed before testing.

## Declared features

The wrapper outcome is three-valued: `ch`, `che`, or `sh`. The twelve feature families are:

1. anonymous record state;
2. normalized line position (`FIRST`, `EARLY`, `MIDDLE`, `LATE`, `LAST`, `SINGLE`);
3. field position induced only by GDT016 DY checkpoints;
4. preceding anonymous state;
5. following anonymous state;
6. the group's own DY closure flag;
7. preceding/following DY adjacency;
8. first/second/third-or-later field index;
9. section;
10. Currier stratum;
11. hand;
12. combined section/Currier/hand register.

Register variables are correlated metadata, not independent causal explanations.

## Tests

The first control is exact residual host. Conditional mutual information `I(wrapper; feature | host)` is compared with 5,000 fixed-seed permutations of wrapper identity within host. Local inclusive p-values and maxT p-values across all twelve declared feature families are reported.

For each of the eight non-metadata construction features, a stricter nuisance pass conditions on the joint `exact host × section–Currier–hand register` cell and permutes only inside that cell. This asks whether line/state/DY effects merely inherit register ecology. The corresponding held-folio predictor starts from a host×register prior; the unseen-host predictor starts from a register-only prior.

The predictive diagnostic is a deliberately small shared-effect model. Training estimates an exact-host wrapper prior with Dirichlet-1/2 smoothing. For each feature value and wrapper it estimates a single host-adjusted multiplicative residual, shrunk by adding five expected and observed events. It is evaluated two ways:

- leave one physical folio out, measuring gain over the exact-host prior;
- leave one residual host out, measuring gain over a global wrapper prior on a completely unseen core.

The second pass is the crucial guard against merely memorizing particular cores. The model is diagnostic, not claimed globally optimal.

## Decision ceiling

Positive transfer can support only shared positional/contextual construction functions beyond host-specific spelling. It cannot name those functions. Strong exact-host dependence rejects a freely interchangeable prefix slot; strong register effects remain confounded with section, Currier, hand, and scribal ecology. f84r remains sealed.
