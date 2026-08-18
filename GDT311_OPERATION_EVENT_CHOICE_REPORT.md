# GDT311 — held-folio operation event choice

Status: **OPERATION_EVENT_CHOICE_TRANSFERS_ON_LICENSED_PAIRS**.

The exact pair license is supplied to every model. The score asks only whether training-folio external context improves source-versus-target choice on deterministic unseen folios.

| operation | test events (+) | FULL gain bits/event | null-centered | AUC | max-12 p | class |
|---|---:|---:|---:|---:|---:|---|
| `wrapper:ch>s` | 150 (48) | +0.29473 | +0.17107 | 0.915 | 0.000122055413 | HELD_EVENT_CHOICE_TRANSFER |
| `wrapper:d>s` | 262 (51) | +0.08743 | +0.05756 | 0.787 | 0.000122055413 | HELD_EVENT_CHOICE_TRANSFER |
| `wrapper:NONE>q` | 694 (394) | +0.07413 | +0.05969 | 0.761 | 0.000122055413 | HELD_EVENT_CHOICE_TRANSFER |

## Frozen component models

| operation | position | prior-DY boundary | register | full |
|---|---:|---:|---:|---:|
| `wrapper:ch>s` | +0.24217 | +0.19582 | +0.14157 | +0.29473 |
| `wrapper:d>s` | +0.06927 | +0.07565 | +0.03041 | +0.08743 |
| `wrapper:NONE>q` | +0.02418 | +0.05175 | +0.04435 | +0.07413 |

## Interpretation

External context improves held source/target choice for `wrapper:ch>s`, `wrapper:d>s`, `wrapper:NONE>q`. This supplies a low-capacity stochastic choice rule after an exact pair is licensed, not a productive unseen-host grammar.

## Claim ceiling

Stochastic formal operation choice on already licensed exact pairs only; no unseen license morphology category semantics sound language plaintext meaning or translation. No f84 row was opened, parsed, retained, joined, or scored.
