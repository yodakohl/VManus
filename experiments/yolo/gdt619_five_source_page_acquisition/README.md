# GDT619 — five source-page acquisition profile

Status: `PROFILE_REGISTERED__NO_IMAGE_REQUEST_EXECUTED`

GDT619 registers, but does not execute, a two-stage request plan for exactly
five Latin 6823 scoring pages and five Clm 28531 control pages inherited from
GDT618. Clm canvas identity is fixed by the metadata formula to scans
26/76/165/97/102 and checked with one `Balsamus` thumbnail at scan 26; only
scans 25/27 are available as an off-by-one fallback. Stage B remains
locked until a separate public `STAGE1_RESOLUTION.json` binds its five literal
BSB URLs.

The registered BSB side is consistently Presentation API v3 plus Image API v3;
all five full-page URLs are manifest `full/max` bodies. An offline-testable
Stage-A state machine supplies the only authorized future network path.

Four already accessed official metadata responses are byte-bound, but no source
image, source transcription, Voynich page, target feature, or semantic
assignment is present. See `PREREGISTRATION.md`,
`METHOD.md`, and `artifacts/REGISTERED_REQUEST_PROFILE.json`.
The JPEG decoder runtime is pinned in `requirements.txt` to `Pillow==10.2.0`.
