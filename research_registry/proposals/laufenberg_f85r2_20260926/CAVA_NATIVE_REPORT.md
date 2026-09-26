# Cava full-leaf native audit: access failure, no native result

2026-09-26. Status: **ACCESS_FAILURE_BEFORE_NATIVE_INSPECTION**. This separately authorized follow-up did not obtain viewable pixels from the specified complete leaf. It therefore adds **zero native feature or ownership observations**.

The selected object was the original JPEG explicitly linked by the already known [Commons metadata record](https://commons.wikimedia.org/wiki/File:Cava_de%27_Tirreni,_Biblioteca_dell%27Abbazia,_cod._3,_fol._203r.jpg), labelled by its uploader as Cava Cod. 3, fol. 203r. The frozen source-identification packet’s published fol. 199r citation and unresolved crosswalk remain unchanged.

| Acquisition action on the same object | Actual result |
|---|---|
| Reopen known Commons metadata record | Browser access error; retained prior metadata supplied its already observed original-file link |
| Follow that original-file link | Browser timeout |
| Download original JPEG using the linked URL, without tracking parameters | HTTP 403; no file written |
| Browser open of the same untracked URL | Access error; no image returned |
| Equivalent literal URL for the same filename | HTTP 403; no file written |
| Follow metadata’s explicitly offered 1280-pixel rendering | Browser returned only an image URL/text stub; no pixels exposed |
| Download that same linked rendering | HTTP 403; no file written |
| Inspect browser result representation | Text string only, no image content block |

Original asset: [linked original JPEG](https://upload.wikimedia.org/wikipedia/commons/7/7a/Cava_de%27_Tirreni%2C_Biblioteca_dell%27Abbazia%2C_cod._3%2C_fol._203r.jpg). The fallback was a display-size rendering of this identical leaf, not another source. No authentication, access-control bypass, viewer reverse-engineering or source substitution was attempted.

**Unexecuted observations:** matching the full leaf to Obrist’s three-subject description; establishing the page’s orientation and whole arrangement; reading central, quadrant and circumference writing; comparing the four portraits; and checking the quality connections directly. No one of these is scored absent, false or verified. Published readings from the prior packet must not be relabelled native evidence.

No source image was downloaded, viewed, cropped, enhanced or OCR-processed in this follow-up. No adjacent manuscript or target pixels/data were opened. The earlier Persée composite was not reopened. The original three-file source-identification packet remains byte-frozen. The exact missing input is a readable copy of this already selected complete JPEG, not a replacement manuscript or another comparator. This access failure provides no new evidence about the diagram’s contents or correspondence to any target.
