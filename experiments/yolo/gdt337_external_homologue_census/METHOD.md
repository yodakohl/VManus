# GDT337 method — blind external exact/topological homologue census

Date: 2026-08-18

Status: `FROZEN_AND_RUN_WITHOUT_VOYNICH_TEXT_SCORING`

## Question

Does the currently auditable medieval astronomical/computistical source frame
contain a readable exact or topological homologue whose slot order and ownership
can be fixed externally and transferred across independent Voynich physical
folios before any Voynich text or joint-tuple identity is exposed?

This is an endpoint-acquisition experiment. It is not a semantic score and it
does not ask whether a diagram “means” zodiac, planet, lunar mansion, wind,
element, degree, day, or any other named system.

## Blindness and source firewall

The candidate census may use only:

1. external library catalogues, scholarly editions and source audits;
2. the published 45-array/504-slot text-blind special-circle inventory;
3. published geometry-only capacity results for the zodiac, f69v start and
   direction, and the repeated 10+5 annular panels.

The runner must not read any Voynich surface string, source-member code,
source-family value, PAGE_HOST, HPR2 coordinate, joint tuple, parser state, or
text similarity. It opens no Voynich image. It uses a raw-selector guard on the
special-circle TSV and rejects any `f84*` page before row parsing. f84 is
forbidden.

The census frame comprises every source-audited astronomical/cosmographical
exact-topology family already registered in the repository plus the new
official British Library Add MS 25435 record. It is a complete audit of this
declared frame, not a claim to exhaust every surviving medieval manuscript.

## Eligibility gates

A subsequent joint-tuple grounding endpoint is viable only if every condition
below is true before text exposure:

1. **Readable external slots.** Every external value used by the endpoint is
   named, numbered, or otherwise readable in a reputable catalogue, edition,
   or scholarly source.
2. **Fixed external order.** The external start, direction/order, and any
   multi-band continuation are explicit rather than fitted to Voynich.
3. **Fixed external ownership.** Labels or values are assigned to individual
   slots by authorial cells, spokes, leaders, numbering, or an explicit textual
   record order.
4. **Geometry-only Voynich selection.** The target was selected without a
   Voynich string, tuple, family, or host identity.
5. **Text-blind target correspondence.** Voynich start, direction, phase,
   band continuation, and slot ownership are fixed by visible topology or a
   pre-existing human annotation—not selected by target text agreement.
6. **Independent-folio transfer.** The design contains discovery material and
   a wholly disjoint physical-folio holdout with the same identified relation.
   Alternate readings are sensitivity views, never replications.
7. **No closed-route repair.** A failed endpoint cannot be made eligible by
   renaming values, changing phase, pooling panels, or importing an exposed
   semantic interpretation.

Cardinality equality alone is insufficient. A circular count with no origin,
direction, or one-to-one slot owner cannot pass.

## Inputs

- `special_circle_text_blind_array_inventory.tsv`: 45 arrays, 504 slots, seven
  physical folios; only geometry/layout columns are retained.
- `zodiac_crosssign_phase_capacity.json`: 10 signs, 300 expected positions,
  299 labels, four physical folios, seven incompatible panel topologies.
- `f69vsd001_start_direction_result.json`: zero author-visible f69v start or
  direction devices.
- `special_circle_10_to_5_pairing_worth.json`: four 10+5 panels on three
  folios, zero author-visible two-to-one pairing devices.
- KART001's frozen A-65 and generic-medieval source manifests.
- the human-curated external FDTW metadata row for MS. Arab. c. 90.

## Outputs and decision

The producer writes the external source manifest, target topology/capacity
inventory, every audited candidate correspondence, and a viable-endpoint
freeze. The viable table is header-only when no candidate passes all seven
gates.

The only permitted decisions are:

- `ONE_OR_MORE_VIABLE_ENDPOINTS_FROZEN_UNSCORED`, or
- `NO_EXTERNAL_EXACT_TOPOLOGICAL_HOMOLOGUE_HAS_TEXT_BLIND_PHASE_AND_INDEPENDENT_FOLIO_TRANSFER_CAPACITY`.

No candidate text may be scored during GDT337, even if a candidate passes.

## Claim ceiling

GDT337 can say only whether this declared source frame contains a viable frozen
endpoint for a later grounding experiment. It cannot identify any Voynich
diagram, map an external value to a Voynich slot, assign a tuple or word, infer
a semantic role, identify a language or culture, recover plaintext, or produce
a translation.
