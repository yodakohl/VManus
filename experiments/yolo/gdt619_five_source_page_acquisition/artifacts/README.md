# GDT619 artifacts

- `REGISTERED_REQUEST_PROFILE.json`: deterministic two-stage manifest,
  thumbnail, full-page, request-governance, rights, provenance, and fail-stop
  contract.
- `REGISTERED_VALIDATION.json`: offline registration validation.
- `STAGE_A_REDIRECT_STOP.json`: compact record of the first execution stop,
  the pre-recovery state/journal hashes, and the one newly authorized literal
  canonical-primary URL.
- `STAGE_A_PRIMARY_OBSERVATION.json`: canonical scan-26 request evidence, two
  agreeing manual rubric readings, the `Borax.`/`Bos.` labels, historical
  crosscheck, and hash-bound canonical adjacent-pair amendment.

Four developmentally fetched official metadata responses are represented only
by their exact URL, byte count, and SHA-256; their response bytes are not
retained here. There is no thumbnail, full-page image, PDF, crop, running-entry
transcription, or Voynich material in the repository. The only source readings
are the two contextual scan-26 labels `Borax.` and `Bos.`. The later Stage-A
manifest response is not stored here;
its byte count and hash match the registered metadata binding. The width-only
scan-26 request stopped before redirect follow-up and before any image body was
read or saved. `../REDIRECT_AMENDMENT.md` defines the narrow recovery. A future
`STAGE1_RESOLUTION.json` requires its own public material pass before Stage B.

`src/acquire_stage_a.py` is code, not an acquisition artifact: import and
self-test perform no network request and write no response file.
The decoder runtime is pinned by `../requirements.txt` to `Pillow==10.2.0`.
The successfully inspected scan-26 JPEG remains private and is represented
publicly only by byte count, dimensions, request metadata, and SHA-256.
