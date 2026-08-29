# GDT617 artifacts

- `REGISTERED_SOURCE_BINDINGS.json`: prospective six-response allow-list,
  identities, sizes, hashes, rights notices, and downstream gate.
- `source_freeze/`: exact official catalogue/manifest responses only. No
  canvas or image resource is fetched.
- `source_freeze/SOURCE_ACQUISITION.json`: deterministic exact-six request log,
  redirect audit, and derived zero canvas/image/target counters.
- `source_freeze/SOURCE_HASHES.tsv`: compact raw and binding hashes.
- `REGISTERED_VALIDATION.json`: local registration and source-freeze checks.

The three IIIF manifests contain links to institution-hosted images. Those
links are metadata; GDT617 does not dereference them.
