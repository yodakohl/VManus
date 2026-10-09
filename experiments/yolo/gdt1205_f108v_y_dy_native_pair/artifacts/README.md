# GDT1205 artifacts

- `REGISTRATION_LOCK.json`: contract, admission and prior-source hashes fixed before pixel access.
- `CANVAS_METADATA.json`: exact official Yale 108v canvas projection, not the full manuscript manifest.
- `SOURCE_IMAGE.json` / `REGION_IMAGES.json`: source URLs, times, hashes, dimensions and native rectangles.
- `OBSERVATION.json` / `OBSERVATION_SEAL.json`: one informed visual observation and its frozen digest.
- `RESULT.json` / `RUN_RECEIPT.json`: deterministic application of the preregistered decision.
- `VALIDATION.json`: source/provenance/schema/reduction PASS, not palaeographic validation.
- `REGISTRY_REVIEW.json`: append-only assessed review; zero native word meanings.

The original photograph and two registered regions are under `../runtime/`. They are one source, not independent confirmations. `../src/fetch_source.py` can reacquire only these pinned files if missing. No OCR or image generation was used.
