# GDT083 — HPR layer-localization synthesis

Status: **YOLO representation stress test and synthesis**

Test page-local predictability over all 15,592 non-f84 HPR groups for four
representations: raw token, pre-HPR residual host, PAGE_HOST, and compiler-only
signature.  In every whole-physical-folio-held fold, fit a register baseline,
then a register×WRAPPER model, then an online same-page model.  Score every
group on a physical line before updating from that line.  Scan wrapper
shrinkage `{8,16,32,64,128,256,512,1024}` and page shrinkage from the same grid
plus `NO_PAGE`.  Report raw and per-event page gains; do not compare absolute
codelengths across unequal vocabularies as if they were the same outcome.

This internal signal is not itself semantic.  Synthesize it with the already
published, folio-excluded GDT068 archived external-axis comparison and GDT073
cross-section stress test.  The hypothesis requires PAGE_HOST to improve over
raw/residual representation for page vocabulary, compiler-only to fail on
external axes, and any broad external interpretation to remain provisional if
it fails cross-section transfer.

No new external labels or images are opened.  f84r remains excluded and sealed.
