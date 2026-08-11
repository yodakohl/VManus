# Translation-anchor acquisition registry v1

## Purpose

Build a compact routing registry for the closest surviving human-evidence
routes to a Voynich translation anchor.  The registry prevents already
exhausted panels from being scored again and states the exact new observation
that would reopen each route.

This is an acquisition artifact, not a manuscript hypothesis test.  It may
summarize published human observations and completed local results, but it may
not inspect a new manuscript association, fit a model, validate an external
decoder claim, or assign a Voynich string an English gloss.

## Mandatory gates

An anchor family is `ADMISSIBLE_UNUSED_TRANSLATION_ANCHOR` only if all six
binary gates equal one:

1. `provenance_traceable_human_source`: the observation has a named,
   inspectable human source and is not OCR, automated vision, or an external
   decoder output;
2. `author_visible_one_to_one_ownership`: an author-visible relation assigns
   one current Voynich text locus to one value or referent without relying on
   modern proximity, clockwise order, or a guessed start;
3. `readable_contrasting_values`: at least two values are independently
   readable and vary in the admitted panel;
4. `independent_physical_folios_ge_5`: the admitted relation is present on at
   least five physical folios, treating ZL3b, IT2a, and RF1b as alternate
   readings rather than replications;
5. `unique_current_locus_mapping`: every admitted source record has one
   unambiguous current physical-locus mapping; and
6. `untouched_confirmation_available`: a folio-held confirmation set remains
   unused by discovery, route selection, and prior target scoring.

Failure of any gate forbids a lexical target.  Gate count is a routing aid,
not a probability, confidence, or evidence weight.

## Frozen evidence scope

The builder may read only:

- `ACTIVE_EXPERIMENT_LEDGER.tsv`, the authoritative claim registry;
- `CLOSED_ROUTE_FAMILIES.tsv`;
- the current human exact-locus, label, and page annotation TSVs;
- the completed COL001, SCP001, zodiac-attribute, F69M001, and F68CL001
  reports named in the builder.

Ledger rows are selected by exact experiment name, so adding this experiment's
own later row does not invalidate the evidence.  The three annotation tables
and five completed reports are SHA-256 bound.  The builder must verify the
reported f57v label topology directly from the current human annotation
tables, including the four figure-near labels at 01:30, 04:30, 07:30, and
10:00.

No manuscript image, OCR, automated vision, pixel coordinate, legacy parser
root or role, proposed plaintext, historical-language fit, or DANI/external
decoder validation may enter.

## Candidate families

The declared families are the nearest extant routes, not an exhaustive list
of imaginable future discoveries.  Each row binds one authoritative ledger
outcome, its six gate values, its decisive blocker, and one concrete reopen
condition.  The output order is descending gate count, then ascending UTF-8
bytes of candidate ID.

The special-circle scope must include the already exposed f57v role phase,
f67r/f68r labelled-homologue no-find, f68r2 Sun-ring cleartext stop, and f69v
ordered-28-coordinate nonconfirmation.  The registry must not reopen those
routes merely because they are diagrammatically distinctive.

## Outputs and decision

Emit:

- a TSV with every candidate and all six gates;
- canonical JSON binding the input hashes, exact ledger outcomes, annotation
  controls, gate totals, and decision; and
- a compact Markdown acquisition report.

The decision is `NO_ADMISSIBLE_UNUSED_TRANSLATION_ANCHOR_ACQUISITION_MAP_READY`
unless at least one row passes all six gates.  Under this v1 evidence scope,
such a pass would be an implementation stop requiring a new preregistration;
the builder is not authorized to score it.

## Claim ceiling

The registry identifies evidence gaps and acquisition priorities only.  It
does not establish a word, part of speech, morpheme, sound, language, cipher
operation, plaintext, meaning, or translation.  In particular, it does not
gloss the f57v figure-near labels as Hot, Moist, Cold, or Dry, or `f2r.15` as
GREEN.
