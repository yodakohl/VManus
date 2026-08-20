# GDT396 qualification result method

Status: `POST_QUALIFICATION_DESCRIPTIVE_OUTPUT_FREEZE`.

This document freezes only how the already completed qualification result is
serialized and described.  It changes no decoder, score, gate, route, seed,
world, surface, representation, or confirmation rule.

## Authoritative execution lineage

`src/run_v2.py` supersedes only the obsolete `score-qualification` dispatch in
`src/run.py`.  It requires the validated V2 correction lineage and invokes
`qualify_decoders_v2.py`; all other stages delegate to the frozen runner.

The three-decoder/two-method-family panel rule in `SCORING_DESIGN.md` and
`PREQUALIFICATION_INSTRUMENT_CORRECTION.md` is authoritative.  The older
two-decoder sentence in `DECODER_QUALIFICATION_SPEC.md` is preserved as
superseded text.  The current result is invariant because there are zero
decoder-suite-qualified routes under either threshold.

The frozen architecture implementation lacks the registered paired 95%
interval check.  This is disclosed as instrument debt, not repaired after
outcome exposure.  Every architecture qualification cell already fails the
point gates in all five seeds, so adding the missing interval cannot turn any
cell positive and cannot affect the stop.

## Published matrices

The exact 117,100-row scorer output is published losslessly as deterministic
gzip.  Its irreducible row remains:

`property × world × surface × representation × decoder × seed × method_variant`.

A route matrix serializes all 1,350 primary event routes.  A compact property
table applies this fixed descriptive precedence:

1. any supported route that fails the frozen W10 veto gives
   `SEMANTICS_LIGHT_FALSE_POSITIVE`;
2. every other scored positive-control endpoint gives
   `CURRENT_DECODER_INSTRUMENT_FALSE_NEGATIVE`, because no decoder passed the
   full suite and the endpoint therefore never reached confirmation; lack of a
   pre-suite route is not promoted to a claim that the property itself is
   unidentifiable;
3. actual lexical meaning was never an endpoint and is separately
   `REQUIRES_EXTERNAL_GROUNDING`.

Where the qualifier's deterministic tie-break records `FULL_GROUP` despite
zero pre-suite decoder support, the compact table reports `NO_SELECTION`.
This avoids presenting an unsupported tie default as an evidence-backed
representation choice; the exact raw selection remains preserved in the route
matrix and qualification JSON.

These are calibration diagnoses, not confirmation claims.  None can license a
Voynich experiment because no decoder passes the required recurrent-relation
suite and no property has a qualified confirmation panel.

Two further frozen-gate implementation debts are outcome-invariant and remain
disclosed rather than repaired post hoc: architecture qualification omitted
its paired-interval conjunct (all 40 architecture seed cells already fail the
point gates), and morphology qualification omitted boundary-F1 and used mean
rather than per-status AP (no morphology route passes before the suite).

## Stop

Confirmation corpora, claims, oracles, and scores must remain absent.  New
decoder versions would require a future qualification and confirmation seed
block; seeds `3961000..3962004` may not be reused.  No synthetic ontology may
transfer to Voynich.  Voynich rows, `f84`, and `f84r` remain forbidden.
