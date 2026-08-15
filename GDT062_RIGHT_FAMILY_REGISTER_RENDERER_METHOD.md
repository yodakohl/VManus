# GDT062 — RIGHT_FAMILY as register-conditioned rendering

Status: **YOLO exploratory generative test**

HPR2 predicts that `AIIN/AIR/AIN/AR/AL` are renderer/register choices
conditional on PAGE_HOST rather than an independent content channel.  GDT062
tests the first half of that claim directly: does the manuscript register
improve held-folio prediction of RIGHT_FAMILY after PAGE_HOST, wrapper, O/OT,
inner-D, DY/B3 state, line position, and scribal hand are already known?

The outcome is the six-way family `NONE/AIIN/AIR/AIN/AR/AL` on all 15,592
strict groups in the f84r-free GDT016 inventory.  Use the same HPR2 parser and
O/OT licensing as GDT059.  Fit hierarchical Dirichlet-1/2 categorical codes:

1. global RIGHT_FAMILY prevalence;
2. compiler nuisance context;
3. nuisance + PAGE_HOST;
4. nuisance + PAGE_HOST + five-way register.

All scoring leaves the complete target physical folio out.  The primary host
is exact PAGE_HOST and the primary nuisance includes catalogued hand.  A
PAGE_HOST edge/length shape and a no-hand model are fixed sensitivities.  The
main effect is model 4 minus model 3 on unseen folios, reported overall, by
register, and on cases whose host key occurs in training.

Positive held gain supports register-conditioned rendering.  It cannot show
that RIGHT_FAMILY lacks semantic information; that separate external-content
negative-control claim already failed in GDT059.  No suffix meaning,
morphology, POS, sound, language, plaintext, or translation is assigned.  f84r
remains sealed.
