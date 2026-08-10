# LRG006 target-blind A1-member calibration

Status: `FROZEN_TARGET_FREE_CALIBRATION_V2`

V1 stopped because 3/8 one-section adversaries passed when favorable noise in
the inactive section reached `.098`--`.180`. All intended distributed plants
had a weaker-section signed effect of at least `.277352`. Before target access,
V2 therefore makes exactly one disclosed change: the signed-effect minimum in
each of B and P is raised from `.04` to `.20`. No world, statistic, assignment,
null, other threshold, or decision rule changes.

The future target is the binary exact all-reading A1 feature on the 677-row,
69-cell masked panel. The statistic is the label-minus-prose feature mean
inside each cell, averaged equally over cells within each of 13 folios and then
equally over folios. The 8,192-assignment null preserves every cell's label
quota. The p-value is two-sided, `(1 + count(|null| >= |T|))/8193`.

Orient all robustness gates by the observed sign. A pass requires p<=.01,
absolute z>=3, absolute effect>=.08, at least 10/13 folios in direction, signed
B/P effects each>=.20, signed odd/even effects each>=.04, section and parity
weaker/stronger ratios each>=.35, every deletion>=.04, and
concentration<=.30.

Calibration uses only the opaque panel and quotas. Synthetic binary features
have approximately the observed aggregate prevalence but no source member or
role association. In 64 null worlds and eight worlds each, require 0/64 null,
8/8 distributed positive-full, negative-full, positive-reduced, and
negative-reduced, plus 0/8 one-folio, one-section, one-parity, folio-random,
and cell-constant adversaries. Missing rows, quota drift, constant metadata,
nonfinite values, or assignment drift hard-stop.

A pass authorizes only a separately committed/frozen binary A1 target after
clean reconstruction. It supplies no sound, spelling normalization, word,
part of speech, function, meaning, plaintext, or translation.
