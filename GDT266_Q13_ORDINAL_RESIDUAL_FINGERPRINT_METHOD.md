# GDT266 — q13 ordinal-residual record fingerprint

## Question

GDT264 found a within-page record fingerprint and GDT265 found a large,
borderline wrapper-based earlier/later-record effect.  GDT266 removes that
global ordinal mean before asking whether two halves of the same record still
retrieve one another.

## Fold and residualization

Use the unchanged nine-page, eighteen-record, f84-free GDT227 panel.  Hold one
physical page out.  On the other eight pages only:

1. learn TF-IDF weights for a fixed representation;
2. normalize each full training record;
3. compute separate `EARLIER` and `LATER` centroids.

For each held record half, form its normalized TF-IDF vector and subtract the
matching training-fold ordinal centroid.  The residual query must retrieve its
other residual half against the competing record on the same page.  Candidate
identity is never supplied; ordinal is used only for nuisance subtraction.

The four fixed GDT264 locus splits and both A→B/B→A directions yield 144
predictions per representation.  The fixed family is structure-only, wrapper,
right family, complete compiler, raw exact groups, exact PAGE_HOSTs, raw
character trigrams, and PAGE_HOST character trigrams.  No n-gram crosses a
group or host boundary.

## Null and identifiability audit

The 4,096 deterministic shared null worlds swap candidate identities within
page and split after residualization.  Report local inclusive and max-eight
p-values.  This is exploratory because the residual test was designed after
GDT264–265, but its transform, feature family, and null are fixed before the
score.

The score is reportable only if nuisance subtraction makes the true and decoy
candidates ordinal-exchangeable.  The panel fails that condition: every true
mate has the same ordinal as the query and every within-page decoy has the
opposite ordinal.  Subtracting a mean does not remove class-specific covariance
or shared negative coordinates in sparse vectors.  A large residual score can
therefore still be an ordinal-geometry effect.  The candidate-swap null does
not repair this because it swaps the scientific identity after the ordinal-
matched geometry has already been constructed.

Consequently the numerical run is retained as a diagnostic and the experiment
must stop as `UNIDENTIFIABLE` unless a same-page same-ordinal decoy exists.  No
such decoy exists in the frozen binary panel.

No surviving score may nominate content on this panel.  The experiment reads
only the already published f84-free GDT227 interlinear and performs no new
f84r access.
