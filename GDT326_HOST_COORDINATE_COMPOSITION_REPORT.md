# GDT326 — held-folio host×coordinate composition

Status: **HOST_COORDINATE_TUPLE_REMAINS_LEXICALIZED**.

The target is a full coordinate combination never observed with that host in training. All 315 target events satisfy this criterion on 76 held physical folios.

| model | folio-balanced bits/event | folio-equivalent gain | selector-paid | event gain | positive folios | top1 | top3 | max-four p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| REGISTER_TABLE | 4.676345 | +0.000 | +0.000 | +0.00 | 0/76 | 50/315 | 103/315 | 1.00000000 |
| HOST_TABLE | 5.815917 | -86.607 | -88.607 | -364.01 | 18/76 | 0/315 | 38/315 | 1.00000000 |
| HOST_FACTORIAL | 5.779215 | -83.818 | -85.818 | -328.73 | 19/76 | 2/315 | 38/315 | 1.00000000 |
| HOST_FACTORIAL_REGISTER | 6.000779 | -100.657 | -102.657 | -380.56 | 10/76 | 6/315 | 44/315 | 1.00000000 |

All host-conditioned models lose heavily to the register table on combinations not previously observed with that host. Separate component frequencies do not rescue them. The current executable unit must therefore remain the joint PAGE_HOST×coordinate tuple rather than an independently reusable PAGE_HOST payload.

This does not prove that the tuple is a linguistic lexeme; `lexicalized` here means formally memorized as a joint compatibility state.

## Claim ceiling

Held-folio opaque-host renderer-coordinate factorization only; no word morpheme category meaning sound language plaintext or translation. No f84 row was opened, parsed, retained, joined, or scored.
