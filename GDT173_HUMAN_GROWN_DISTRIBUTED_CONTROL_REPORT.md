# GDT173 — B2 human-grown distributed control report

Status: **B2_DISTRIBUTED_IDENTITY_PARTIALLY_RECOVERED_WITHOUT_FACTORIAL_COMPATIBILITY**.

B2 alone was added. GDT172 lexical A and factorial B were not regenerated or
modified. B2 uses an explicit irregular 384-row reversible lookup with 32
unequal families, optional fields, 11 exceptions and six listed S2 family
variants on the exact GDT172 source/layout schedule.

## Recovery

| level | host information | held host accuracy / coverage | held full accuracy / coverage | exact true host |
|---|---:|---:|---:|---:|
| surface | 0.720 | 0.268 / 0.931 | 0.933 / 0.078 | 0.616 |
| annotation | 0.911 | 0.689 / 0.843 | 0.933 / 0.078 | 0.186 |

The sealed oracle is exactly reversible, but blind recovery is partial. Exact
component recovery on frequent lexical-ID rows is:

| system (surface) | exact host | exact left | exact right | exact boundary set |
|---|---:|---:|---:|---:|
| lexical A | 0.794 | 0.799 | 0.811 | 0.794 |
| factorial B | 0.303 | 0.802 | 0.416 | 0.238 |
| human-grown B2 | 0.616 | 0.729 | 0.710 | 0.534 |

Annotation-assisted B2 exact host/left/right/boundary-set recovery is
0.186 / 0.519 /
0.316 / 0.149.
Full span and boundary precision/recall are retained in
`gdt173_component_recovery.tsv`; the complete A/B/B2 comparison is in
`gdt173_three_system_recovery.tsv`.

## Diagnostic fingerprint

| system (surface) | compatibility / p | NEXT gain | WHOLE_LINE gain | record-end precision |
|---|---:|---:|---:|---:|
| lexical A | 0.197 / 0.7990 | 23495 | 7976 | 0.290 |
| factorial B | 0.875 / 0.0020 | 13495 | -1034 | 0.111 |
| human-grown B2 | 0.278 / 0.9863 | 17319 | 2663 | 0.141 |

B2 does **not** reproduce factorial B's dense, low-null compatibility graph.
It retains strong positive surface NEXT_HOST and positive surface WHOLE_LINE
context, while annotation assistance keeps NEXT_HOST positive but turns
WHOLE_LINE slightly negative (-489.9 bits).
The complete two-level fingerprint, including substitution, short-host and
register-alignment diagnostics, is in `gdt173_three_system_fingerprint.tsv`.

## Consequence

Distribution of identity across several explicit fields is insufficient by
itself to create factorial-B compatibility. The unchanged instrument recovers
some B2 identity and context, but not its full component architecture. B2 is a
synthetic human-grown control, not a historical reconstruction or Voynich
model. No Voynich source or image was scored and no f84 material was accessed.
