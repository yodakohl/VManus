# GDT619 Stage-A redirect amendment

Published: 2026-08-29

Status: `STAGE_A_WIDTH_ONLY_REDIRECT_STOP__CANONICAL_PRIMARY_REGISTERED`

## Observed stop

The first execution of the public GDT619 Stage-A profile successfully fetched
the exact registered Clm 28531 manifest: 261,778 bytes, SHA-256
`6f25dbd8a0baff9a681e8c486a9a883ed704671c155a7cfd81775e9f2a235fd3`.
The next GET used the registered scan-26 width-only URL. BSB answered with a
redirect to the size-canonical Image API v3 URL ending
`/full/1200,1790/0/default.jpg`. The registered redirect handler stopped before
the follow-up request. No image response body was read or saved, no JPEG was
opened, and no rubric was inspected.

This is a request-profile correction, not a locator or semantic result. The
old width-only URL retains its durable failed intent and is permanently
retired.

## Narrow correction

`artifacts/STAGE_A_REDIRECT_STOP.json` binds the complete compact failure
record, the pre-recovery state and journal hashes, and the one newly authorized
literal URL. The manifest may not be fetched again. Recovery is a separate
offline operation and must first prove all of the following:

1. the saved manifest rehashes and revalidates against the registered bytes;
2. the private journal and state match the published pre-recovery hashes;
3. sequence 1 is the unique manifest success;
4. sequence 2 is the unique old-URL intent and redirect failure;
5. the redirect detail contains the exact old and new URLs;
6. no image, failed-body, or Stage-1 draft file exists; and
7. no other network success or request intent exists.

Only after that no-network recovery may a new command issue sequence 3 to the
literal canonical scan-26 URL. Redirect following and retries remain disabled.
The new response must be a fully decoded 1200x1790 JPEG. This amendment
authorizes no fallback URL and no Stage-B request.

If the canonical scan-26 rubric is `VISIBLY_ABSENT`, the state machine stops at
`STOPPED_CANONICAL_PRIMARY_VISIBLY_ABSENT__FALLBACK_REQUIRES_PUBLIC_AMENDMENT`;
the original scan-25/27 transition is unavailable. The old direct/fallback
request caps of 7/9 remain historical properties of the original profile. The
current canonical-visible direct path has a cumulative cap of 8 BSB requests:
manifest, consumed width-only redirect request, canonical thumbnail, and five
future Stage-B pages. No current fallback-path cap exists because that path is
forbidden.

## Claim ceiling

The pass establishes one stable source-manifest response and one pre-body URL
canonicalization. It verifies no source rubric or locator, opens no Voynich
material, and assigns no Voynich sign, word, language, plant, plaintext, or
meaning. `f84` and `f84r` remain forbidden.
