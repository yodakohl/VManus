# FDTW f57 homologue metadata prescreen v1

## Purpose

Use the 2026 *From Data to Wisdom* (FDTW) human-curated IIIF catalogue as a
cheap metadata gate before any image-level validation of another f57v
historical homologue.  The question is only whether the catalogue description
contains a candidate with all of:

1. a circle or wheel layout;
2. four explicit human figures, persons, heads, or personifications;
3. readable element or hot/cold/dry/moist quality content; and
4. labels or inscriptions.

This is source acquisition, not validation of a paper, decipherment, or
external translation claim.

## Public inputs

Fetch exactly the HTTPS listing
`https://ifilosofia.up.pt/proj/fdtw/iiif/manifests`.  In source order, extract
the first occurrence of every link matching the exact relative form
`fdtw/iiif/manifest/UUID`, where UUID is 36 lowercase hexadecimal/hyphen
characters.  Fetch exactly one JSON manifest for every unique UUID at
`https://iiifmanifests.ifilosofia.up.pt/api/manifests/UUID.json`.

Every request must terminate at its exact URL with status 200.  Read only the
listing HTML and manifest JSON.  Do not request thumbnails, canvases, image
services, PDFs, OCR, pixels, or linked papers.

The raw listing wrapper is dynamic and must not be hashed.  Bind instead the
stable listing projection consisting of the 263 unique UUIDs in first-source
order, each encoded as UTF-8 followed by one LF.

## Projection

For every manifest retain only source order, UUID, raw manifest SHA-256,
flattened `label`, flattened `description`, and the first metadata values for
`Manuscript number`, `Century`, `Archetype`, and `Theme`.  Flatten strings
directly, lists in order separated by one ASCII space, and dictionaries by
keys `@value`, `value`, then `en` when present, also separated by one ASCII
space.  Collapse all Unicode whitespace in projected text to one ASCII space
and strip ends.

The full projected TSV is the reusable acquisition inventory.  It is not a
semantic annotation of the Voynich manuscript.

## Exact metadata filters

Apply Unicode case-insensitive Python regular expressions to the concatenated
projected label, description, archetype, and theme:

- circle: `\b(wheel|rota|circular|circle|roundel|concentric)\b`;
- explicit people: `\b(four (?:human )?(?:figures|persons|people|heads)|personif(?:y|ied|ication)|human figures?|four men|four women|four heads)\b`;
- element/quality: `\b(element|elements|hot|cold|dry|moist|humid|calid\w*|frigid\w*|sicc\w*|humid\w*)\b`;
- readable marking: `\b(label|labels|inscription|inscriptions|marked|words?|terms?)\b`.

`metadata_candidate=1` only if all four filters match.  Separately count the
broader circle-plus-element intersection.  A zero candidate count stops before
all image inspection or full scholarly-source validation.  It proves only
that the current catalogue metadata supplies no admitted candidate; an image
or uncatalogued manuscript could still contain one.

## Decision and claim ceiling

If zero candidates exist, emit
`STOP_BEFORE_IMAGE_VALIDATION_ZERO_F57_METADATA_CANDIDATES`.  If one or more
exist, emit `CANDIDATE_METADATA_REQUIRES_SEPARATE_HUMAN_SOURCE_AUDIT` and do
not open images in this experiment.

Neither outcome identifies the f57v diagram, owns a Voynich label, or assigns
Hot, Moist, Cold, Dry, an element, a word, sound, language, cipher operation,
plaintext, meaning, or translation.
