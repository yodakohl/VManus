# GDT198 — two local opaque payloads bridge f77 label classes

Status: **LOCAL_PAYLOAD_REUSE_LEAD_NOT_ABOVE_ROLE_ASSIGNMENT_NULL**.

Two of the three all-reading-stable figure-associated labels share the same
renderer-stripped HPR2 payload as one of the six tube-state labels:

| figure label | tube label | shared payload | surface change |
|---|---|---|---|
| `dotedy` (`f77r.8`) | `otedy` (`f77r.3`) | `e|NONE|DY1|B30` | add outer `d` wrapper |
| `otchdy` (`f77r.49`) | `dchdy` (`f77r.6`) | `ch|NONE|DY1|B30` | `d` wrapper versus `OT` frame |

The southwest figure label supplies a weaker third resemblance: ZL3b writes
`otolaiin | o`, while IT2a/RF1b join `otolaiino`; its initial `otol` equals the
fourth tube label, but the reading-dependent boundary prevents an exact
payload comparison.

This is a coherent local compiler pattern: opaque payload can remain stable
while its left rendering changes with visual label class.  It is not strong
enough to identify a role.  Across all 84 assignments of three figure roles to
the nine stable labels, 20 achieve at least the observed two cross-class
matches (**p=0.238095**).  Neither matched pair shares a complete surface or
full HPR2 tuple, and all human ownership is proximity-only.

The best abductive use is therefore narrow: retain `e+DY` and `ch+DY` as two
page-local opaque values reused across diagram contexts.  Do not call them
DRY, MOIST, figures, substances, or operations.  No word, sound, language,
plaintext, meaning, or translation is established. f84r and all f84 rows were
excluded.
