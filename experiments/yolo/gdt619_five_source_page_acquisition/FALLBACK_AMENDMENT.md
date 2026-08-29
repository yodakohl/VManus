# GDT619 canonical adjacent-pair amendment

Published: 2026-08-29

Status: `SUPERSEDED_BY_PUBLIC_STAGE1_RESOLUTION`

## Concrete primary result

The publicly authorized canonical scan-26 request succeeded without redirect:
443,716 bytes, SHA-256
`2121ec99849a7aac5d19dd10779b0d503bbb1e0a6220915375b0688891d202f3`,
fully decoded at 1200x1790. Manual inspection finds no visible `Balsamus`.
The central-left plant drawing instead carries the clear label `Borax`; the
lower-right bovine drawing is labelled `Bos`. The registered observation is
therefore `VISIBLY_ABSENT`. No OCR, image classifier, captioner, embedding, or
botanical-similarity method was used.

This supplies a concrete contextual clue for the failed locator. Wagner Appendix 1,
already bound by PDF SHA-256
`8f57e7aaee4fe049ecf3fbf201ba2bf13bd6c446438ed59098afe2d28ee7a4fe`,
places `Balsamus` at Clm f10v and `Borax` at the immediately following f11r.
The visible label is therefore consistent with scan 26 being f11r and scan 25
being the already preregistered negative-one Balsamus candidate. This is a
post-observation consistency clue, not a page identification or selected shift.

The legal basis for the adjacent requests is the original mechanical rule—one
primary `VISIBLY_ABSENT` observation authorizes both neighbors—not the
post-observation `Borax` identification. That historical crosscheck is context
only. Shift selection still depends solely on `Balsamus` rubric visibility on
the two adjacent scans.

## Exact adjacent-pair requests

The saved manifest fixes scan 25 at 1707x2466 and scan 27 at 1707x2628. This
amendment derives the server-size candidates by the same floor rule exposed by
the observed scan-26 canonicalization:

1. scan 25: `/full/1200,1733/0/default.jpg`;
2. scan 27: `/full/1200,1847/0/default.jpg`.

The two literal URLs must be requested in that order, with no redirect follow,
retry, manifest refetch, width-only request, or other scan. Both responses must
fully decode at their exact registered dimensions. A redirect or any mismatch
stops immediately.

Before either GET, an offline command must match the public pre-fallback state
SHA-256 `81d23efa...2503`, journal SHA-256 `e2e76380...eda6`, exact scan-26
image hash, saved manifest, request history, observation, and complete private
packet. The cumulative BSB cap is now ten: manifest, consumed width-only
request, canonical scan 26, canonical scans 25/27, and five future Stage-B
pages. Stage B remains forbidden until a public Stage-1 resolution.

## Decision and claim ceiling

After both images are manually read, exactly one `VISIBLE` plus one
`VISIBLY_ABSENT` selects delta -1 or +1 under the original rule. Any ambiguous,
double-visible, double-absent, redirect, transport, or decode outcome stops.

The adjacent pair subsequently resolved exactly as registered: scan 25 is
`VISIBLE` with the illustrated label `Balsami.`, while scan 27 is
`VISIBLY_ABSENT` and visibly labels `bos agrestis`. The selected global delta
is therefore `-1`. `STAGE1_RESULT.md` and
`artifacts/STAGE1_RESOLUTION.json` publish the complete result and five
literal Stage-B URLs. No running source entry or Voynich target has been
transcribed, and no Voynich sign, word, plant, plaintext, or meaning is
assigned. `f84` and `f84r` remain forbidden.
