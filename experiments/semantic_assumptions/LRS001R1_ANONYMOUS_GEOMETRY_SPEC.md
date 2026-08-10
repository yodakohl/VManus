# LRS001-R1 label-free pseudonymous calibration geometry specification

Date frozen: 2026-08-10

This artifact exposes only the record geometry needed for target-blind
synthetic calibration.  It is derived once from the frozen strict capacity
universe, then synthetic calibration must consume this artifact rather than
reopening real `family_surface` context/target pairs.

The identifiers are deterministic hashes of public row IDs and the metadata
can reidentify public manuscript rows.  "Pseudonymous" here means only that no
real class identity or group content is present; it is not a privacy or
information-security anonymity claim.  `supported_class_target` is itself a
real surface-derived eligibility bit, although it does not reveal which of the
66 classes a row has.

For every group in every complete 5--12-group `CONFIRMED_PROSE` record, store
hashed group and record IDs; the frozen physical-folio split; page, folio,
section, Currier, hand, code and kind; exact record/drawing geometry; group
symbol count; whether the group is a CORE member of the 66-class TRAIN-supported
target inventory; and whether its TEST record belongs to a strict movable
donor cell.  The strict cell is the eight-field LRS001-R1 key.

The artifact must contain no `family_surface`, STA member code, EVA,
transcription token, root, role, English gloss, image, OCR, or automated-vision
field.  Synthetic family-block matrices and synthetic labels must be generated
only from domain-separated hashes of the anonymous IDs.  Real target/context
associations remain forbidden until a separately frozen calibration passes and
a one-time target is registered.

The opaque synthetic class layout is fixed by target symbol count as
`{1: 3, 2: 8, 3: 23, 4: 19, 5: 10, 6: 3}`.  It carries no real class names.
Calibration may read only this TSV, its manifest, the calibration
preregistration, calibration core, runner, and later clean-room validator.
It may not read/import the capacity JSON, source atlas, split source, geometry
builder/validator, parser, or any transcription/content artifact.

Page-inventory controls in calibration are limited to the same complete
5--12-group prose universe and must exclude the entire current record.

The artifact is pseudonymous geometry, not evidence of a schema, word, field, meaning,
plaintext, or translation.
