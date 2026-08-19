# GDT361 pre-review canvas correction

The first public freeze (`714639e5d3d1d9c5917194ec97f5e2b64e0082e738fd618068d65fe00a37b0f3`)
incorrectly identified Yale canvas `1006253` as f102v2. The cached human
catalogue and the folio image establish that `1006252` is f102v2; `1006253` is
the adjacent f102v1 surface.

This was corrected after the full correct canvas had been opened, but before:

- any crop-level GDT361 CONTACT/CLEAR_GAP/UNCERTAIN call was recorded;
- any GDT361 visual observation artifact existed;
- any formal family for prospective loci `f102v2.11`–`.16` was queried.

The target unit, seven loci, exclusion of pre-exposed `.10`, six scored loci,
AQ/AQA predicate, predicted direction, null, and scoring rule are unchanged.
The correction removes pristine image blinding but does not select a target or
formal rule from its observed state. The corrected freeze binds the exact
superseded freeze hash and the correct official image hash.
