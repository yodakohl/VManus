# GDT037 — Herbal-B / Stars-Recipe shared formal register

## Question

Which exact formal vocabulary and constructions recur across Herbal Currier B and the Stars/Recipe section while remaining rare in Herbal Currier A? The aim is a ranked practical-register atlas, not another test of global section similarity and not semantic decoding.

## Source and strata

The source is the f84-free, all-reading-agreeing GDT016 physical/manual group inventory. ZL3b, IT2a, and RF1b are alternate readings, not replications.

Primary strata are Herbal-A (`section=H, Currier=A`), Herbal-B (`H,B`), Currier-B Stars/Recipe (`S,B`), and other Currier-B sections (`B/C/T,B`). The last is the required control against rediscovering generic Currier-B rendering. The single Currier-A S folio is sensitivity only.

Hand 3 overlaps Herbal-B and S. Per-feature same-hand-3 support is recorded, but complete hand control is impossible: Herbal-B also has hands 2 and 5, S is overwhelmingly hand 3, and Herbal-A is hand 1.

## Frozen feature families

The scan constructs eight machine feature families without semantic labels (the fourth conceptual class is exported at both exact and compact resolutions):

1. exact residual core;
2. observed wrapper plus exact residual core;
3. anonymous GDT016 record state;
4. exact DY-delimited state-field template and compact field shape;
5. residual closer host of a DY-closed field;
6. adjacent anonymous-state transition;
7. adjacent wrapper transition.

Fields end only at an observed `DY_RESOLUTION`; final unclosed material is explicitly marked `OPEN`.

Features require at least three occurrences and two physical folios in each target stratum. Rates use Jeffreys half-count smoothing within the appropriate group, transition, or field denominator.

## Ranking and controls

For every retained feature the atlas reports the smaller of Herbal-B-versus-A and S-versus-A log2 rate ratios, the smaller of both target-versus-other-Currier-B ratios, B/S rate imbalance, minimum target-folio support, hand-3 support, and Currier-A S sensitivity.

The transparent exploratory rank is:

`min(4,A-enrichment) + clipped(other-B specificity,-3..3) + log2(1+minimum target folios) - 0.5*B/S imbalance`.

Every target folio is then removed in turn. A `B_S_REGISTER_CANDIDATE` must remain positively enriched over both Herbal-A and other Currier-B after the worst deletion and must occur in the shared hand-3 comparison. Features enriched over A but not over other Currier-B are counterexamples labelled generic B.

This is post-selection ranking, not confirmation-grade inference. Exact cores with low DY-closure share can be nominated as formal nonclosure/content-host candidates, but no semantic function is assigned without independent grounding. f84r remains sealed.
