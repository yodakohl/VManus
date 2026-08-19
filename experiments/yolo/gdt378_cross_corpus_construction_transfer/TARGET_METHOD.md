# GDT378 target stage — frozen anonymous multi-resolution transfer

## Input and seal

The only Voynich input is the already published f84-free
`gdt327_joint_tuple_interlinear.tsv` (8,448 groups, 288 records, 91 physical
folios). The scorer must reject any page, locus, or physical-folio value with
prefix `f84` before retaining a row. It may not read a global transcription or
another table that contains f84.

The four fitted comparator signatures in
`gdt378_secondary_transfer_signature_freeze.json` are immutable. The failed
HEAD model is ineligible. Comparator endpoint names are provenance labels only;
Voynich outputs use `CMP_FUNCTION_01`–`04` and remain `UNASSIGNED`.

## Four charged resolutions

1. `ATOMIC_JOINT_TUPLE`: one GDT327 joint-tuple ID; wrapper variation is
   marginalized exactly as licensed by the frozen formal object.
2. `SOURCE_GROUP`: an opaque hash of `(joint_tuple_id, observed_wrapper)` for
   one physical source group. No substring, glyph, PAGE_HOST, or coordinate is
   exposed separately.
3. `FIELD_CONSTRUCTION_SPAN`: an opaque hash of the ordered SOURCE_GROUP IDs in
   one `(page, record, physical line, field)` span.
4. `GRAMMAR_SLOT_POSITION`: five predeclared field-slot families:
   from-start class `1/2/3/4+`; from-end class `last/penultimate/antepenultimate/earlier`;
   relative field quartile; closure `DY/B3/LINE_END/OTHER`; and the fixed
   from-start×closure cross. No slot is named for a linguistic function.

Records are `(page, record_ordinal)`. Input row order is the physical order;
fields are keyed by `(page, record_ordinal, locus, field_ordinal)` and preserve
their source-group order.

## Leakage-safe scoring

Each physical folio is held out in turn. Within-register opaque-identity
frequency, cross-record recurrence, predecessor/successor diversity and mean
position are learned from non-held folios only. Record-local order, equality,
return distance, boundaries and neighboring-record set overlap are observable
test inputs. Frozen comparator coefficients and normalization are then applied
unchanged. A within-record-rank signature is ranked only inside the current
record.

The strong placement baseline is learned on non-held folios and conditions on
section, register, Currier, hand, record-length bucket, record-ordinal quartile,
physical-line position, within-field position, unit-length bucket and
closure class, plus the training-only opaque-ID recurrence bucket. A fixed hierarchy backs off only by
dropping hand, then Currier, then section; it never uses candidate outcomes
from the held folio. The scored residual is frozen-signature score minus this
placement expectation.

For recurring candidate IDs, a training-only shrunk candidate residual
(`n/(n+16)`) predicts the held residual. The main transfer diagnostics are
held squared-error gain over placement, fraction of eligible held folios with
positive gain, mean residual, threshold exceedance, cross-folio consistency,
and cross-register consistency.

## Power, search and null

A candidate is powered only with at least 12 events, three physical folios,
and two registers. Promotion requires:

- positive total held-folio gain over placement;
- positive gain on at least 60% of its eligible held folios;
- positive mean placement residual;
- positive mean residual in at least two thirds of its physical folios;
- positive mean residual in at least two registers; and
- inclusive maxT p <= .05.

The 4,096-world null shuffles frozen scores within physical-folio × section ×
register × Currier × hand × record-length × record-position × line-position ×
within-field-position × unit-length × recurrence strata. Candidate membership,
frequency, folio coverage, layout opportunities and sizes remain fixed. One
world maximum charges all four signatures, all four resolutions, every powered
candidate, all five slot families, and both positive and negative tails. Null
mobility is reported; a low-capacity null cannot promote a result.
The frozen capacity minimum is 256 mobile events and 10% of the scored events
at that resolution; both must be met.

## Claim ceiling

At most this stage may nominate an anonymous, recurrent constructional slot or
span whose frozen comparator-structural score transfers across folios and
registers. It cannot establish UNTIL, OR, polarity, exclusion, function word,
HEAD, verb, predicate, action, POS, sound, language, plaintext, meaning, or
translation.
