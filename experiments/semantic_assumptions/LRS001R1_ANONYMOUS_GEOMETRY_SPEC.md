# LRS001-R1 anonymous calibration geometry specification

Date frozen: 2026-08-10

This artifact exposes only the record geometry needed for target-blind
synthetic calibration.  It is derived once from the frozen strict capacity
universe, then synthetic calibration must consume this artifact rather than
reopening real `family_surface` context/target pairs.

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

Page-inventory controls in calibration are limited to the same complete
5--12-group prose universe and must exclude the entire current record.

The artifact is geometry, not evidence of a schema, word, field, meaning,
plaintext, or translation.
