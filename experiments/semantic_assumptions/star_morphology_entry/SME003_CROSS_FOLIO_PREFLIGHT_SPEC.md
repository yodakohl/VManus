# SME003 cross-folio concordance — target-blind preflight freeze

Status: **FROZEN BEFORE PREFLIGHT CODE EXECUTION; REAL MORPHOLOGY FORBIDDEN**

## Distinct question

SME003 asks whether a distributed high-minus-low paragraph profile learned on
other physical folios predicts the held physical folio. This is not SME001's
question of whether any one of 84 features survives a family-corrected scan.
No pooled classifier, favorable feature selection, or weakened SME001 gate is
admissible.

The strongest later result would be an anonymous cross-folio-reproducible
paragraph-profile association under the already frozen equal-count,
top-to-bottom marker pairing. It could not establish object ownership, a ray
or tail meaning, a recipe class, a number, a root or word meaning, a language,
plaintext, or a translation.

## Evidence boundary

This preflight may read only:

- `anonymous_paragraph_matrix.tsv`, SHA-256
  `b246456b181b07e847c6d5a49b959b0346eff6a4c6febb8a543de104c505a26a`;
- `anonymous_feature_inventory.json`, SHA-256
  `088232b431b4b9746bb94a08328cb969fb7c21c6a28cd112286da40d6429fea5`.

It excludes the complete page `f106r` mechanically, leaving exactly 156 units,
468 reading rows, 12 pages, seven physical folios, three alternate readings,
and 84 anonymous features. It may not open, parse, import, hash-join, or infer
any ray, tail, core, color, or other morphology field. Every SME001/SME003
target result path must be absent before and after the run.

The exact page contract is frozen as `f104r:13`, `f104v:13`, `f105r:10`,
`f105v:10`, `f107v:15`, `f112v:13`, `f113r:16`, `f113v:15`, `f114r:13`,
`f114v:12`, `f115r:13`, and `f115v:13`. Each page must map wholly to the
physical folio obtained by removing its terminal `r`/`v`; page ordinals must
be exactly `1..page_size`; and page, folio, ordinal, and locus metadata must be
identical across readings. The output binds canonical newline-delimited
training- and held-unit digests for every fold.

## Frozen fold transform

The seven physical folios define seven leave-one-folio-out transforms. For
each held folio, edition, and feature:

1. Within every page, center the feature and every nuisance column. This
   removes page intercepts without using a target label.
2. Fit nuisance coefficients on rows from the six training folios only and
   apply them to centered training and held rows.
3. Every feature uses relative ordinal `r=(ordinal-.5)/page_size`, `r^2`,
   `r^3`; absolute ordinal `a=(ordinal-.5)/16`, `a^2`, `a^3`; odd ordinal;
   first half defined exactly as `ordinal <= page_size/2`; and relative-quarter
   indicators 1--3. On an odd-length page the unique middle row is therefore
   in the late half, matching SME001's frozen convention.
4. The 50 root-rate features additionally use centered `log1p(PARA_WORD_COUNT)`
   and its square and cube. The 34 formal features do not receive this length
   adjustment because paragraph volume is part of their admissible anonymous
   construction profile.
5. Divide residuals by their training-row root-mean-square. A feature is
   globally eligible only when this scale is finite and greater than `1e-10`
   in every held-folio/edition transform. Eligibility is therefore fixed
   without a morphology label.

For each held-folio/edition transform, form the population covariance `S` of
the eligible standardized training residuals. With `p` eligible features and
`n` training rows, freeze

```
mu    = trace(S) / p
alpha = mean(S * S)
den   = (n + 1) * (alpha - mu*mu/p)
rho   = 1                         if den <= 1e-15
        min(1, (alpha + mu*mu)/den) otherwise
C     = (1-rho)*S + rho*mu*I
W     = inverse(C), rescaled so trace(W)=p.
```

No covariance parameter is selected by synthetic power or by a target. The
preflight must stop if any transform is nonfinite, `C` is not positive
definite, `W` is not symmetric positive definite, or the eligible intersection
has fewer than 24 formal and 32 root features.

The exact feature order must equal the inventory's 34 formal columns followed
by all 32 `ROOT_ATOM_RATE__` columns and all 18 `ROOT_WORD_RATE__` columns in
their frozen inventory order. Every `PARA_WORD_COUNT` must be finite and
nonnegative before `log1p`; every nuisance matrix must be finite. Contract or
numeric failure must hard-stop before eigendecomposition or inversion and may
never emit authorizing prose.

## Later statistic already constrained

No label score is authorized by this preflight. A later separately frozen
implementation may compute, for each alternate reading, page-balanced
high-minus-low vectors `Delta_f` and the cross-folio concordance

```
T_e = mean_f( Delta_f' W_{-f,e} mean_{g != f}(Delta_g) / p ).
```

Only informative physical folios enter this average. The ray target has at
most seven independent folios and the tail target at most six; rows and pages
are never counted as independent capacity. All label-dependent directions
must be refit inside every held-folio fold and every phase assignment.

The later design must retain complete-page cyclic rotations, both independent-
page and coupled-folio phase ensembles, joint ray/tail correction, ordinal and
root-length control, common reading direction/material, folio support and
deletion gates, synthetic null/power worlds based on the actual anonymous
reading perturbations, adversarial reading disagreement, a single target join,
and a nonimporting reconstruction. It may expose no feature weights or
favorable roots.

## Exact later coordinate and reading rule

For a held folio `f`, every `Delta_f` and every training `Delta_g` in that
summand must be computed in the same `f,e` coordinate system: the same
`f`-excluded nuisance coefficients, training RMS scales, eligible feature
order, and `W_{-f,e}`. Fold-specific vectors may never be mixed directly.

The readings will not be averaged. The later primary statistic is fixed as
`R=min_e((T_e-mean_null(T_e))/sd_null(T_e))`, with population null moments,
under each phase ensemble. Joint inference takes the assignment-wise maximum
of the ray and tail `R` values. In addition to the later exact family tail,
every reading must have positive raw `T_e`, and the weakest reading must meet
the frozen material gate
`sign(T_e)*sqrt(abs(T_e)) >= .05`. This is a multivariate cross-folio RMS
concordance scale, not an individual feature effect.

## Preflight output ceiling

The only permitted preflight output is the eligible feature count and
identities, per-fold row counts, residual scales, shrinkage values,
eigenvalue/condition diagnostics, canonical little-endian float64 digests of
every standardized matrix and weight matrix, input/source hashes, invariant
checks, target-artifact absence, and a GO/STOP capacity decision. It supplies
no morphology association or meaning.
