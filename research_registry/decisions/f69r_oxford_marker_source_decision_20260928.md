# f69r / Oxford MS 17 marker check — pre-image decision

2026-09-28, before opening the Oxford fol. 40v pixels. This is a bounded source-only follow-up, not a manuscript target test or a wind-name assignment.

Prior evidence: the f69r–Oxford comparison records a strong 12-wind structural family, 45 versus 46 outer cups, but distinct written-register counts (Voynich 22 radial and 16 outer versus Oxford 12 named winds); see ledger row `f69r_stjohn_ms17_wind_homologue_audit`. GDT1067 proves an exact 180-degree polarity ambiguity under the already known class geometry. The f69r catalogue describes one decorated break near 2 o'clock; it has not been established whether the Oxford cup ring has a unique author-visible break or corresponding asymmetry. The old source comparison report path is absent in this checkout, so this is an explicitly exposed follow-up, not blind confirmation.

Decision question: does Oxford St John's College MS 17 fol. 40v display a unique interruption, gap or marker in its cup ring that could be paired with the *already described* f69r decorated break independently of the 12/16 color classes? If yes, retain only a possible phase anchor and require a separately established owner relation before any directional word test. If no, close this non-class phase route. Neither outcome licenses cardinal names or resolves source-versus-destination polarity by itself.

Smallest test: one whole official Bodleian IIIF fol. 40v image (manifest `66a78997-ab65-4059-a9d3-d08a0bba067c`, canvas index 90, label `fol. 40v`), native visual inspection of the entire ring. Record source URL, dimensions and hash; do not inspect any new Voynich image, crop, OCR, or change transcription. Budget 25 minutes including acquisition, report, checks and publication. If the source image cannot be retrieved/seen within the budget, record missing data and stop.

Dependencies/assumptions: historical f69r description is prior exposure and a coarse observation, not a pixel-verified fresh owner map; Oxford is an analogue, not proven ancestor; the 45/46 count may reflect copying, decoration or unrelated execution. f84/f84r and reserves remain closed.

## Acquisition outcome

The official manifest loaded (HTTP 200, 376 canvases) and identified `fol. 40v` as canvas index 90, 5242×7520, image service `https://iiif.bodleian.ox.ac.uk/iiif/image/3eb15bab-6706-4807-ae7d-621f172e5396`. Three requests to that exact official service failed before any image bytes were obtained: whole image width 2000 (45-second read timeout), width 1000 (20-second read timeout), and `info.json` (8-second read timeout). The web reader also reported the 1000-pixel rendition inaccessible. There is no native visual observation or marker finding. **Decision: MISSING_SOURCE_IMAGE; no phase anchor and no wind-name test.** A reachable official fol. 40v rendition would change the missing input, but repeating the same request without it does not.
