# GDT306 — disjoint q post-DY entry test

Status: **Q_POST_DY_ENTRY_TRANSFERS**.

The entire 98-event panel and all 39 matching cells were committed before the preceding-group endpoint was read. Every exact surface is disjoint from GDT303 and GDT305.

| variant | cells/events | post-DY NONE/q/delta | exact p | line-start delta | line exact p |
|---|---:|---:|---:|---:|---:|
| `PRIMARY_BASE_CELL` | 39/98 | 0.168/0.359/+0.191 | 0.023763020833 | -0.066 | 0.183680555556 |
| `WITHIN_FOLIO` | 11/22 | 0.000/0.273/+0.273 | 0.125000000000 | +0.000 | 1.000000000000 |
| `EXACT_GROUP_COUNT` | 11/23 | 0.091/0.273/+0.182 | 0.312500000000 | +0.091 | 1.000000000000 |
| `WITHIN_FOLIO_EXACT_GROUP_COUNT` | 5/10 | 0.000/0.400/+0.400 | 0.250000000000 | +0.000 | 1.000000000000 |

## Interpretation

The frozen primary and sensitivities all point toward a q-conditioned post-DY transition. The primary effect is evaluated independently of same-group q parsing by reading only the immediately preceding physical group. Physical line start is kept separate.

This is a prospective, exact-surface-disjoint replication/localization of the post-DY `qo...` wrapper ecology already reported by GDT024 and GDT061. It strengthens generalization beyond their frequent forms; it does not create a new compiler state or reopen their host-transition negatives.

## Gates

- `primary_delta_positive`: **PASS**
- `primary_exact_p_le_0_05`: **PASS**
- `within_folio_delta_positive`: **PASS**
- `exact_group_count_delta_positive`: **PASS**

## Claim ceiling

Formal q-conditioned post-DY transition only; no grammar semantics sound language plaintext meaning or translation. No f84 row was opened, parsed, retained, joined, or scored.
