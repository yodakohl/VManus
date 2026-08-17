# GDT199 — the f77 renderer switch does not transfer

Status: **F77_RENDERER_SWITCH_DOES_NOT_TRANSFER_TO_ARCHIVED_LABELS**.

The complete non-f77 annotated inventory contains five single-group labels
with either exact GDT198 payload.  4 have an unambiguous archived proxy
class and receive a frozen prediction; only **1/4** matches.

| locus | class | surface | frozen prediction | result |
|---|---|---|---|---|
| `f73v.23` | FIGURE_ONLY | `otedy` | `d|D0|OT` | MISS |
| `f75v.54` | APPARATUS_ONLY | `otedy` | `NONE|D0|OT` | HIT |
| `f75v.56` | APPARATUS_ONLY | `qotedy` | `NONE|D0|OT` | MISS |
| `f82v.2` | FIGURE_ONLY | `otedy` | `d|D0|OT` | MISS |


The decisive miss is `f73v.23`: it is figure-only in the archived human
atlas, but its `e+DY` payload uses bare `OT` (`otedy`), not the f77-derived
figure renderer `d+OT` (`dotedy`).  The apparatus-only hit and miss are both
on f75, so they cannot supply independent replication.  The remaining row is
retained as an other context and is not forced into a class.

Thus GDT198 remains a real local surface relation but not a transferable
visual-class renderer rule.  The reusable fact is only that opaque `e+DY` and
`ch+DY` payloads recur under multiple outer forms.  No ownership, role, word,
sound, language, plaintext, meaning, or translation follows.  f84r and every
f84 row were excluded.
