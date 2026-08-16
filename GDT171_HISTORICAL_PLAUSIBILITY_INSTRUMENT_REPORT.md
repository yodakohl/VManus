# GDT171 — historical-plausibility instrument calibration report

Status: **HISTORICAL_V2_PARTIALLY_RECOVERED_BUT_COMPONENT_SENSITIVITY_LIMITED**.

GDT168 v1 remains unchanged. GDT171 replaces its 6,175 pseudo-concepts,
fixed 18/6 layout, alphabet permutations and ten complete content copies with
384 recurring lexical IDs, literal escape, real source order, variable physical
records/lines, partitioned registers, partial overlap and shared-alphabet hands.
World B is an explicit 384-row table, not a modulo cipher.

## Frequent lexical-ID recovery

| world | level | host information | held host accuracy / coverage | held full accuracy / coverage | exact host boundary (all frequent) | exact component-boundary set (compiler-marked) |
|---|---|---:|---:|---:|---:|---:|
| A lexical codebook | surface | 0.970 | 0.897 / 0.905 | 0.853 / 0.082 | 0.807 | 0.577 |
| A lexical codebook | annotation | 0.980 | 0.909 / 0.832 | 0.853 / 0.082 | 0.609 | 0.097 |
| A lexical codebook | oracle | 0.985 | 0.933 / 0.958 | 0.893 / 0.417 | 1.000 | 1.000 |
| B distributed table | surface | 0.539 | 0.217 / 0.962 | 0.938 / 0.076 | 0.300 | 0.222 |
| B distributed table | annotation | 0.855 | 0.579 / 0.894 | 0.938 / 0.076 | 0.082 | 0.039 |
| B distributed table | oracle | 0.261 | 0.054 / 1.000 | 0.967 / 0.410 | 1.000 | 1.000 |

## Diagnostic calibration

The historically plausible controls produce signals missing from v1.  The
lexical world has positive held next-host and whole-line context.  The
distributed world has a much denser compatible-operation graph, but its
whole-line context is negative.  Layout assistance makes lexical-world right
marks almost perfectly specific to record endings, while the distributed
world's lexical right/field layers confound that endpoint.

This means the normal pipeline has real partial sensitivity when the lexical
inventory is recurrent and register content is not copied wholesale.  It still
does not simply recover the encoder: exact host and full-component rates stay
well below the oracle, annotation assistance can trade host recovery for
closure precision, and literal escapes dominate the all-row corpus.  The
separate literal rows in the artifacts prevent that mechanism from being
misreported as a 6,175-entry vocabulary.

The component-boundary column is restricted to compiler-marked frequent rows;
bare-host rows are excluded so a trivially boundary-free group cannot count as
a successful decomposition.  Full precision/recall/F1 and the corresponding
literal/all-row sensitivities are retained in `gdt171_component_recovery.tsv`.

## Consequence

GDT170's zero component recovery was partly a v1 generator pathology, not a
universal parser verdict.  GDT171 is the more relevant calibration for a
bounded medieval technical lexicon with literal exceptions.  Positive held
context is compatible with a genuine lexical-ID layer; high left-right
compatibility is compatible with distributed notation.  Neither pattern alone
identifies Voynich architecture, and oracle ceilings remain non-blind.

No Voynich source or image was used. f84r was not accessed.
