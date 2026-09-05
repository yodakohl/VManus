# Independent pre-score design review: initial continuation control

Status: DESIGN_RECOMMENDATIONS_BEFORE_FEATURES_OR_SCORES. This review used only
`VOYNICH_CURRENT_ROUTE.md`, `docs/visual_writing_order/PROPOSAL.md` and its source
metadata. The reviewer did not inspect manuscript pixels, extract features,
search public approaches, or inspect continuation outcomes. The experiment's
final preregistration, not this advisory document, must specify the executed
algorithm and thresholds. Any adoption or departure should be explicit there.

## The precise first question

Does a frozen image-only measurement identify a withheld geometric continuation
of an apparently continuous row better than matched alternatives and explicit
image/background/morphology baselines? This is an instrument-control question.
The continuity of the original historical writing act is not ground truth;
only the geometric row and location of the withheld patch are known.

A successful artificial-cut control would not establish historical production
order, reading order, temporal direction, the identity of a word, or that the
signal specifically measures transient pen/ink state. It must not authorize a
split-block target measurement automatically.

## Minimum defensible extraction and comparison

1. Freeze image identities, hashes, native dimensions, admitted page crop,
   row/crop selection, omitted interval, windows, eligibility thresholds and
   calibration/held-row allocation before seeing feature performance. Native
   service dimensions should be independently checked. No AI reconstruction,
   rescaling to invent stroke interiors, or use of neighboring unadmitted pages.
2. Use local paper-normalized RGB optical density on comparable stroke cores:
   log((paper_channel + 1)/(ink_channel + 1)). Estimate paper around the same
   component with a fixed ring or local background rule. Use only a fixed band
   of near-vertical stroke tangents and widths; insufficient cores are missing
   data, not zero ink. Freeze component, tangent, width and exclusion rules.
3. Keep physical stroke width, tangent angle, core occupancy, component size,
   and local paper summaries as morphology/background nuisance features.
   Width and angle can be relevant physically, but their raw variation is
   also heavily influenced by glyph composition. They are not themselves a
   demonstrated transient-state clock.
4. Fit any residualization and scaling on calibration rows only. A deliberately
   small predeclared linear/ridge regression is preferable to broad model
   selection. Summarize residual RGB optical density per window. Rank candidates
   with one frozen squared standardized residual-distance metric. No raw XY,
   row identifier, page identifier, pixel texture embedding, or patch-edge
   matching may enter the state metric.
5. Compare the true right-side window to other-row windows at the same X range
   on the same page. Match candidate quality and available stroke support.
   Report the nuisance-only baseline on exactly the same queries. Candidate
   count and tie handling must be fixed and explicit; chance differs by count.
6. Also require a same-row distant-window comparison before describing the
   feature as local/transient. Same-row true versus other-row decoys alone can
   identify stable row-wide ink, glyph composition or background. Spatial
   distance differs in this second comparison, so success still cannot isolate
   time; it can only rule out the simplest constant-row signature.
7. Include a paper/background-only negative control and a fixed synthetic
   competence check that implants known locally correlated residual values,
   plus a fixed text-independent null. These test plumbing and artifact
   sensitivity. They do not supply historical ground truth. An easy synthetic
   success cannot rescue a failed manuscript control.
8. Publish every eligible held query and retained/failed quality gate, including
   failures and ties. Repeated anchors sharing row/windows are one row cluster;
   three transcriptions would not create independent image evidence.

## Operational thresholds and their interpretation

One possible conservative initial operational gate, proposed before any scores,
requires at least 24 held rows distributed over at least two admitted pages,
with at least four candidates per query and one fixed primary query per row.
Require at least 10 percentage points of top-one retrieval improvement over
both candidate-count chance and the stronger nuisance-only baseline, positive
lift on each page, and consistent same-row distance discrimination. These
thresholds are suggested design choices, not established power calculations.
If the final scope cannot support them, declare capacity insufficient or freeze
a separately justified smaller control before scoring; do not choose thresholds
from observed accuracy. A smaller control can establish basic measurement
feasibility but carries correspondingly less evidential weight.

Candidate-label permutations are not automatically a valid causal test:
true and decoy labels are defined by image geometry and may not be exchangeable.
If permutations are retained, label them operational retrieval-null references,
state the exchangeability assumptions, cluster overlapping rows correctly, and
do not present a small reference probability as proof of pen continuity.
Independent held pages and explicit artifact baselines matter more than the
nominal number of patches.

## Fixed exits

- SOURCE_OR_EXTRACTION_CAPACITY_STOP: native provenance, adequate comparable
  stroke support or required held/candidate capacity is absent. Stop this
  implementation; do not reduce quality rules after seeing outcomes.
- CONTROL_FAIL: the frozen residual metric does not exceed the predeclared
  retrieval gates, or its apparent success is reproduced by nuisance controls.
  No split-block ranking, chronology claim or post-hoc alternate ink metric.
- CONTROL_LOCAL_CONTINUATION_ONLY: the frozen retrieval and artifact controls
  pass. This establishes usable image association on the admitted artificial
  cuts under the working row-continuity assumption. It does not name its
  physical cause or imply direction. Real pen lifts, different gap widths and
  split-block layouts require a separately registered transfer control.

In particular, the original proposal's request for directed trajectory evidence
has not been satisfied by symmetric nearest-distance matching. Such a detector
can at most support adjacency. Temporal direction requires separately calibrated
asymmetry with independent historical or experimental ground truth.
