# GDT356 method: LJS 443 work attribution and key-capacity audit

## Question

Which catalogued work contains the LJS 443 diagram subseries isolated by
GDT354–355, and does current scholarship provide a folio-specific value/order
key that licenses a later alignment?

This is an external-source audit. It does not score or inspect a Voynich target.

## Exposure

`POST_GDT355_EXTERNAL_SOURCE_ATTRIBUTION_AUDIT`. The external diagram family
was already selected. The result is provenance repair and source narrowing,
not blinded confirmation.

## Frozen sources

1. Penn Libraries' official JSON catalogue record for LJS 443.
2. The official OPenn TEI record already bound in GDT355.
3. Gor Galstyan, “The Commentary of the Armenian Calendar by Yovhannēs
   Sarkawag,” *Banber Matenadarani* 33 (2022), pp. 425–445.
4. Grigor Broutian, “Persian and Arabic Calendars as Presented by Anania
   Shirakatsi,” *Tarikh-e Elm* 8 (2009), pp. 1–17.
5. The content-bound GDT355 result.

Remote bytes are represented by URL and SHA-256. No downloaded PDF, catalogue
JSON, TEI, or facsimile is vendored.

## Mechanical attribution

Use the modern foliation in the Penn contents note.

- Hakob Ghrimetsʻi commentary: 3r–54v.
- Hovhannēs Vardapet/Sarkawag commentary: 145v–212r.
- Anania Shirakatsʻi astronomy: 213r–244r.
- The narrow GDT355 subseries: 209r, 209v, 210r.

The three narrow pages therefore fall inside the Hovhannēs commentary range.
This range containment is an attribution to the catalogued work, not a claim
that Hovhannēs personally drew this copy's diagrams.

## Feature audit

For each tempting identification, record one of:

- `SUPPORTED_WORK_LEVEL`
- `SUPPORTED_SYSTEM_LEVEL_NOT_FOLIO_KEYED`
- `UNSUPPORTED_FOLIO_LEVEL`
- `CONTRADICTED_BY_RANGE`

A feature enters a later alignment only if scholarship fixes the exact Penn
folio's values, ownership, order, start, and direction. Generic discussion of
the work's calendar systems is not sufficient.

## Decision rule

Return `WORK_ATTRIBUTION_NARROWED_FOLIO_KEY_STILL_ABSENT` if the containing work
is identified but no source fixes the narrow pages' slot values and order.

## Seals and claim ceiling

No Voynich image, transcription, source group, formal representation, or f84
material may be accessed. The ceiling is attribution of the external pages to
a catalogued work and a bounded inventory of documented system-level
possibilities. It is not a lunar-table identity, semantic key, source-copying
claim, language identification, plaintext, or translation.
