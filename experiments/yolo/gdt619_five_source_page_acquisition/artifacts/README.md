# GDT619 artifacts

- `REGISTERED_REQUEST_PROFILE.json`: deterministic two-stage manifest,
  thumbnail, full-page, request-governance, rights, provenance, and fail-stop
  contract.
- `REGISTERED_VALIDATION.json`: offline registration validation.

Four developmentally fetched official metadata responses are represented only
by their exact URL, byte count, and SHA-256; their response bytes are not
retained here. There is no thumbnail, full-page image, PDF, crop, transcription,
or Voynich material. A future `STAGE1_RESOLUTION.json` requires its own public
material pass before Stage B.

`src/acquire_stage_a.py` is code, not an acquisition artifact: import and
self-test perform no network request and write no response file.
The decoder runtime is pinned by `../requirements.txt` to `Pillow==10.2.0`.
