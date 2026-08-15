# GDT105 — universal PAGE_HOST edge grammar

## Outcome

**UNIVERSAL_FINAL_CHARACTER_RENDERER_GRAMMAR_DOMINATES_EXACT_PAGE_HOST**

Across all 15,592 groups on 94 physical
folios, register-only renderer prediction costs 21,564.840 held bits. The
final PAGE_HOST character costs only 6,003.283, gaining
15,561.557 bits. It beats final-two
(6,527.640), exact PAGE_HOST (11,617.194),
first character (19,270.293), and length
(19,573.731). The direction holds in every leave-register-out
target.

This is not a PCH-specific fact. After all 331 PCH groups are removed
from training, final-character prediction scores them in
124.613 bits,
versus register prevalence 519.964; exact PAGE_HOST cannot transfer and
backs off to 519.964.
GDT102's attractive PCH tail rules are therefore an instance of a universal
host-edge grammar.

The HPR2 generator should be revised from an opaque PAGE_HOST to
`CONTENT_ADDRESS + EDGE_STATE`, where EDGE_STATE strongly licenses DY,
RIGHT_FAMILY, B3, or bare closure. This improves formal factorization but does
not show that CONTENT_ADDRESS has meaning. Because the parser itself removes
renderer material, some edge predictability may be structural by construction;
the external-content question must be retested after edge stripping.

All roles remain UNASSIGNED. f84r was absent and untouched.
