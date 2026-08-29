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
- `STAGE1_RESOLUTION.json`: canonical manifest, three-thumbnail request and
  manual-observation evidence, selected delta `-1`, and the five literal Clm
  Stage-B page identities and URLs.

Four developmentally fetched official metadata responses are represented only
by their exact URL, byte count, and SHA-256; their response bytes are not
retained here. There is no thumbnail, full-page image, PDF, crop, running-entry
transcription, or Voynich material in the repository. The source readings are
limited to the calibration labels described in `../STAGE1_RESULT.md`. The later Stage-A
manifest response is not stored here;
its byte count and hash match the registered metadata binding. The width-only
scan-26 request stopped before redirect follow-up and before any image body was
read or saved. `../REDIRECT_AMENDMENT.md` defines the narrow recovery. The
public Stage-1 packet now satisfies the Stage-B publication gate; Stage B
remains unexecuted.

`src/acquire_stage_a.py` is code, not an acquisition artifact: import and
self-test perform no network request and write no response file.
The decoder runtime is pinned by `../requirements.txt` to `Pillow==10.2.0`.
The three successfully inspected calibration JPEGs remain private and are
represented publicly only by byte count, dimensions, request metadata, and
SHA-256.
