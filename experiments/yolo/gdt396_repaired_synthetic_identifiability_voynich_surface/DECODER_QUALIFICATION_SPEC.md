# GDT396 decoder qualification specification

Status: `REGISTERED_BEFORE_QUALIFICATION_DATA_GENERATION`.

Qualification measures whether a decoder can use the V2 interface. It is not a
scientific result and contributes no confirmation observations.

## Chronology

1. Decoder authors may iterate on development seeds `3960000..3960004` and separate
   public API fixtures.
2. Decoder source hashes are frozen.
3. Blind qualification seeds `3961000..3961004` are decoded once; claims are frozen.
4. Qualification oracles are opened by the scorer. No decoder is repaired or
   rerun after seeing qualification results.
5. Only qualified `(decoder, property, representation, surface)` routes may
   enter confirmation. A failed version requires new decoder and future seed
   blocks, never reuse of `3961000..3962004`.

## Partition anti-degeneracy and recovery

For a recurrent truth partition, all must hold in at least four of five seeds
and two meaningful world families under each surface:

- resolved coverage `>= .80`;
- at least three predicted nonsingleton clusters;
- singleton-event fraction `<= .60`;
- largest cluster fraction `<= .75`;
- predicted/truth co-clustered-pair count ratio in `[.25, 4]`;
- NMI `>= .50`, ARI `>= .30`, and pair-F1 `>= .40`.

This rejects singleton-everything and one-cluster-everything without weakening
the scientific gate.

## Ranked relations and references

Eligibility requires at least 30 positive opportunities and three relation
types, query coverage `>= .60`, MRR `>= .35`, Hits@1 `>= .20`, nDCG@5
`>= .45`, and MRR lift `>= .10` over the strongest frozen observation-only
candidate baseline in four of five seeds. Any subtype alignment is learned on
development only and frozen before qualification.

## Scope

All submitted intervals must be structurally valid. Coverage must be `>= .60`,
median interval IoU `>= .50`, exact span recovery `>= .25`, and IoU lift
`>= .10` over the best of full-record, anchor-only, and frozen fixed-window
baselines.

## Productive versus fossil morphology

Coverage must be `>= .60`; boundary F1 `>= .50`; productive/fossil macro-F1
`>= .60`; AP `>= .50` for each supported status; false morphology discovery
rate `<= .10` in a no-current-morphology control. A claimed productive
component must recur across at least three complete surface types and two
training records; productive/fossil sets must be disjoint; at least half of
resolved component spans must be proper substrings.

## Recurrent relation and architecture suite

Every decoder must also:

- recover an easy equality partition;
- recover one simple recurrent relation;
- emit schema-valid relation, reference, scope, and morphology claims;
- distinguish at least one meaningful control from W10;
- achieve deterministic byte-identical reruns.

Eligibility is per endpoint, representation, and surface—not all-or-nothing.
At least two independent qualified decoders from distinct method families are
required for a confirmation statement. Model brand is not a vote quota.

## Multi-constraint detector

The multi-constraint architecture detector uses five independently measured
signals: recurrent partition recovery, cross-record/context stability, ranked
relation/reference lift, scope or productive-morphology lift, and record-schema
lift beyond record length. A positive requires three signals including one of
the last three.

It is compared with a development-selected scalar from the frozen set:
repetition rate, type-token ratio, unigram entropy, mean group length, or record
length variation. On qualification, the multi-constraint detector requires
leave-family-out balanced accuracy `>= .70`, MCC `>= .35`, W10 false-positive
rate `<= .10`, and balanced-accuracy lead `>= .10` with a paired 95% interval
excluding zero.

## Independence

Primary decoders are authored in isolated Sol contexts and may not inspect
sibling implementations or outputs. They share schema validation only—no
algorithmic or learned utility. Decoder hashes and attestations are frozen
before qualification. Historical blindness is an attested provenance fact;
runtime schema, path, state, and output checks remain mechanical.
