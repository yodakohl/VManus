# GDT395 adversarial-pair protocol amendment

Status: `FROZEN_BEFORE_CORPUS_GENERATION_AND_DECODING`

The interface freeze bound the original METHOD at SHA-256
`fc8b311586a53550c701c14a706e730237275121b929c8bc8860dce589ae5f9f`.
Before any decoder was designed or exposed to a corpus, independent carrier
audit showed that the two independently designed pairs did not share the full
page/paragraph carrier envelope promised by that text. An attempted central
carrier rewrite was rejected because it damaged authentic record and scope
topology and was withdrawn before decoding.

The corrected adversarial endpoint is narrower and truth-safe. Main world
corpora remain authentic and retain every observation/oracle property. The two
critical pair comparisons use a separate **record/line-local view**:

* exactly ten complete records per world and seed;
* exact equality of record length, ordered physical-line profile, ambiguity
  count, and within-record separator histogram;
* deterministic observation-only selection requiring differences no greater
  than `0.10` for type/token ratio, top-type rate, and hapax fraction;
* a corpus-local injective fixed-width recoding of visible full-group types,
  derived directly from a salted type hash rather than corpus frequency, so
  equality and recurrence partitions are invariant, held-seed frequency does
  not enter the code assignment, and glyph-internal form is unavailable;
* page, paragraph, register, hand, and layout IDs are masked to
  `NONCOMPARABLE`; record-edge PAGE/PARAGRAPH labels become `RECORD`; and record
  and line IDs are locally renumbered;
* event order within every selected record, physical-line membership,
  within-record separators, ambiguity, event IDs, and all sealed oracle rows
  remain unchanged.

Consequently the pair view may score only record/line-local recurrence,
identity, schema/topology, and within-view relation/reference/scope endpoints.
It may not score page/paragraph, register/hand, layout, glyph-component,
morpheme, productive/fossil morphology, or genealogy claims. Those properties
are evaluated only on the ten authentic full corpora and are not used in the
adversarial pair verdict.

This amendment was driven solely by pre-decoding carrier balance and topology
audits. It does not use decoder success, oracle outcomes, Voynich data, or f84.
