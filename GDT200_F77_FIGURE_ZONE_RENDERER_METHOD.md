# GDT200 — f77 figure-zone renderer confound

## Purpose

Test the simplest page-local explanation for GDT198 after GDT199 rejected a
transferable figure-versus-apparatus renderer rule: the outer form may instead
track which f77 apparatus zone contains the nearby figure.

The four figure-associated labels are the complete human exact-locus set.
Human descriptions and direct inspection of official Yale canvas 1006212
(SHA-256 `9ad387ccea37cd8a25ce9602817eb19af5105c545a238203715efe454e5b24ad`)
place `f77r.1/.8` at the northwest/northeast endpoints of the upper tube and
`f77r.49/.50` beside the separate middle/lower left apparatuses.  This is an
`AI_DIRECT_VISUAL_OBSERVATION` of geometry only; no text was read from pixels.

## Exposed test

Freeze two renderer categories visible in every alternate reading:

- `STARTS_D`
- `STARTS_OT`

Count upper endpoint labels that start `d` and lower-apparatus labels that
start `ot`.  Enumerate all `C(4,2)=6` assignments of two labels to the upper
zone.  The directional tail uses the observed rule (`upper=d`, `lower=ot`);
the orientation-free tail also allows its reversal.

This pattern was noticed after all four labels and their positions were
visible.  The null quantifies local assignment freedom but cannot make the
result prospective or semantic.

## Ceiling

At most, the result identifies a page-local panel-zone renderer confound.  It
does not establish figure ownership, tube direction, stage, quality, word,
sound, language, plaintext, meaning, or translation.  f84r and all f84 rows
are excluded.
