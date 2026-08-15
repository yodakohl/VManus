# GDT061 — DY post-boundary renderer/host attribution

Status: **YOLO exploratory component ablation**

GDT060 found that DY versus non-DY predicts the following PAGE_HOST under
complete-folio holdout, while one- and two-character summaries of the
preceding host do not combine productively with DY.  GDT061 asks whether that
post-boundary signal is actually independent host selection or leakage from
the already known renderer architecture after DY.

Use the complete, f84r-free GDT060 boundary inventory.  Predict the complete
right-hand string with fixed order-2 character models under:

- `BASE`: no boundary or following-renderer conditioning;
- `DY`: previous boundary is DY/non-DY;
- `RENDERER`: following group's frozen HPR2 compiler signature;
- `RENDERER_DY`: both.

Renderer controls are nested:

1. following outer wrapper only;
2. wrapper plus O/OT local frame;
3. full compiler signature: wrapper, carrier-conditioned inner D, O/OT frame,
   right-family, following group's own DY state, and B3.

The primary representation is PAGE_HOST with the full compiler.  Raw surface
and residual-root strings under the same full compiler are strong string
baselines.  Every model is learned without the target physical folio; a
leave-complete-register-out sensitivity is also run.  Conditional models have
a fixed eight-event hierarchical prior.  No parameter is selected on an
external annotation.

The primary quantity is `RENDERER_DY` gain over `RENDERER`.  A positive value
means post-DY host information remains after the following renderer is known;
a nonpositive value attributes the apparent host signal to renderer ecology at
this resolution.  This test assigns no role, gloss, word, morpheme, POS, sound,
language, plaintext, meaning, or translation.  f84r remains sealed.
