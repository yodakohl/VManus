# GDT201 — the f77 zone renderer fails on comparable f83r

Status: **F77_ZONE_RENDERER_FAILS_COMPARABLE_F83_PANEL**.

The unmodified f77 rule makes four predictions on the previously fixed f83r
panel and gets **0/4** correct:

| locus | visual zone | predicted | observed |
|---|---|---|---|
| `f83r.45` | ARCH_END_NEAR_FIGURE_AND_TUBE | STARTS_D | `chtorol` (OTHER) |
| `f83r.46` | ARCH_END_NEAR_FIGURE_AND_TUBE | STARTS_D | `olsaiin` (OTHER) |
| `f83r.50` | LOWER_STRUCTURE_OUTLET_NO_LOCAL_FIGURE | STARTS_OT | `sasoldal` (OTHER) |
| `f83r.51` | LOWER_STRUCTURE_OUTLET_NO_LOCAL_FIGURE | STARTS_OT | `darolsy` (STARTS_D) |


All three readings agree on the relevant initial class.  The internal
`sasoldal`/`saroldal` disagreement at `f83r.50` therefore does not affect the
failure.

GDT200 remains an exact description of four f77 labels, but not a transferable
upper/lower apparatus renderer.  Together with GDT199, this removes visual
class and panel zone as general explanations of the f77 `d`/`ot` split.  The
outer forms remain page/register-conditioned compiler material with no decoded
role.  No ownership, direction, stage, word, sound, language, plaintext,
meaning, or translation follows.  f84r and every f84 row were excluded.
