# GDT619 source-image request preregistration

Registered: 2026-08-29

Current status: `STAGE_A_WIDTH_ONLY_REDIRECT_STOP__CANONICAL_PRIMARY_REGISTERED`

Original registration status: `PROFILE_REGISTERED__NO_IMAGE_REQUEST_EXECUTED`

## Dependency and access boundary

This request profile follows public GDT618 commit `c0266e78` and binds the
corrected GDT618 source-plan SHA-256
`2df86904b38212ba37ea3d0dcb0def241600e6f900c94bcb44d87ecd9f969502`.
The registration builder performs no network request. Four official BSB
metadata responses were developmentally fetched before this profile was
completed and are bound by URL, byte count, and SHA-256 in the request profile:
the Clm 28531 v3 manifest, the Cod.icon.222 v3 manifest and METS record, and the
Clm 4623 v3 manifest. No thumbnail, source-page image, Voynich page, target
feature, or transcription was opened. `f84` and `f84r` remain forbidden.

## Frozen source-page deck

The only future full-page source requests are:

1. Latin 6823 f25v / Gallica f58 and Clm 28531 f10v (`Balsamus`);
2. Latin 6823 f44v / Gallica f96 and Clm 28531 f35v (`Cerfolium`);
3. Latin 6823 f85v / Gallica f178 and Clm 28531 f80r (`Liquiritia`);
4. Latin 6823 f42r / Gallica f91 and Clm 28531 f46r (`Cucurbita`); and
5. Latin 6823 f57v / Gallica f122 and Clm 28531 f48v (`Diptamus`).

Latin 6823 remains the sole future scoring-text witness. Clm 28531 remains a
separate locator and manual-reading control and may never repair Latin 6823.

## Two-stage Clm contract

Stage A re-requests only the exact official Clm 28531 Presentation API v3
manifest and requires the already bound 261,778 bytes and SHA-256
`6f25dbd8a0baff9a681e8c486a9a883ed704671c155a7cfd81775e9f2a235fd3`.
Its 316 canvases implement the metadata-derived physical-order formulas
`recto=2n+5` and `verso=2n+6`: f10v=26, f35v=76, f80r=165, f46r=97, and
f48v=102. The model is II+154 leaves plus four cover/mirror scans; Wagner's
post-disorder foliation note requires physical bound order.

One primary Image API v3 calibration thumbnail is fixed at scan 26 using
`/full/1200,/0/default.jpg`. Its observation is exactly `VISIBLE`,
`VISIBLY_ABSENT`, or `AMBIGUOUS_OR_UNREADABLE`. `VISIBLE` confirms shift zero.
Only `VISIBLY_ABSENT` authorizes both fallback requests, scan 25 followed by
scan 27. Exactly one `VISIBLE` plus one `VISIBLY_ABSENT` selects global shift
-1 or +1. Ambiguity, transport/decode failure, zero matches, or two matches
stop without another request. No other scan, neighbor search, OCR, automatic
classification, or botanical picture similarity is permitted.

Stage A must then publish `STAGE1_RESOLUTION.json`, including the manifest hash,
calibration branch, global shift, thumbnail log and hashes, manual rubric observations,
five canvas IDs, five service IDs, and five literal BSB Stage-B URLs. Stage B is
forbidden until that artifact is public.

## Frozen Stage-B requests

Stage B may request exactly five manifest-advertised BSB Image API v3 bodies
with `/full/max/0/default.jpg` and exactly five manifest-bound Gallica Image API
1.1 native resources: f58, f96, f178, f91, and f122 with
`/full/full/0/native.jpg`. It may make no network crop. Any later local reading
crop must retain source hash, source dimensions, zero-based rectangle, and
crop hash.

All requests use one concurrent connection, `Accept-Encoding: identity`, no
redirect following, no retries, no HEAD, no `info.json`, and at least four
seconds between BSB requests. A redirect, quota response, ambiguous mapping,
missing rubric, unexpected IIIF identity, or unregistered URL stops the pass.
Every intent is fsynced before its request; successes, timestamps, defined
delays, transport/decode failures, and failure bytes remain in a private
outside-repository journal. Thumbnail responses are capped at 5,000,000 bytes.
An auto-releasing advisory private-directory lock and fsynced `IN_FLIGHT` state make requests
exactly once: any unresolved attempt permanently refuses a resend. Failure-body
preservation applies only to complete within-cap bodies rejected by decode or
semantic validation, not HTTP errors, redirects, wrong media, or over-cap data.
The Stage-1 draft requires full reread/rehash/revalidation of the manifest and
all branch thumbnails and exposes complete per-thumbnail request/response,
decode, timing, hash, and linked manual-observation evidence without private
filesystem paths.
Only a fresh directory or one bearing the exact atomically created GDT619
ownership marker is accepted. Separate post-manifest and post-scan-25 phases
resume solely at scan 26 and scan 27; any URL already represented by an intent
or success journal row is refused before sending.
JPEG success requires Pillow verification plus a complete decoded pixel load;
truncated/SOF-only streams stop. The supplied path and every component must be
non-symlinks, and parent directories are fsynced after file creation and every
atomic state replacement.
`requirements.txt` pins `Pillow==10.2.0`, and validation requires that imported
version exactly. A newly created private directory is followed immediately by
an fsync of its parent directory entry.

The exact Clm body dimensions are 1707x2547, 1707x2563, 1707x2624,
1707x2576, and 1707x2587. Every service must be `ImageService3`, profile
`level2`. Top-level `/rights`, `/requiredStatement`, and `/provider` are
preserved verbatim; `/rights` is
`https://creativecommons.org/publicdomain/mark/1.0/`.

## Claim ceiling

Registration licenses only a future source-image acquisition. It verifies no
locator, reads no source text, opens no Voynich material, and supplies no
Voynich sign, word, language, plant, plaintext, or meaning.

## Post-registration Stage-A correction

The first execution fetched the exact registered manifest and then received a
BSB redirect from the registered scan-26 width-only request to the literal
size `1200,1790`. The no-redirect handler stopped before a follow-up request;
zero image body bytes were read or saved. The original request remains a
failed, permanently nonrepeatable intent.

The separately public `REDIRECT_AMENDMENT.md` and
`artifacts/STAGE_A_REDIRECT_STOP.json` bind the pre-recovery state and journal
hashes and authorize only a new request to the literal canonical scan-26 URL.
The saved manifest must be reused offline. Redirects, retries, fallback images,
Stage B, source reading, and Voynich access remain forbidden by this amendment.

## Post-correction primary observation and adjacent pair

The canonical scan-26 request succeeded at 1200x1790, 443,716 bytes, SHA-256
`2121ec99849a7aac5d19dd10779b0d503bbb1e0a6220915375b0688891d202f3`.
Two manual readers agree that the required `Balsamus` rubric is visibly absent;
the page instead labels the central plant `Borax.` and the lower animal `Bos.`.
Wagner's bound appendix places `Balsamus` at f10v and `Borax` at f11r.

The separately public `FALLBACK_AMENDMENT.md` and
`artifacts/STAGE_A_PRIMARY_OBSERVATION.json` therefore authorize the original
adjacent-pair branch at literal canonical sizes: scan 25 at 1200x1733, then scan
27 at 1200x1847. Both must be acquired and manually read before a delta can be
selected. The cumulative BSB cap becomes ten; Stage B remains forbidden.
