# GDT612 reconstructed execution contract and chronology

This is **not a formal preregistration**. It reconstructs the contract of a
developmental scratch run from the unchanged sources, seeds, mappings and
complete full-run hash manifest. Inputs and the final full-run implementation
were frozen after train-only smoke fits, but no externally sealed numerical
calibration gate existed, the final evaluator is not provably pre-Held, and the
target phase was allowed to run after the defective calibration failed.

## Bound inputs

- GDT605 64-merge table;
- GDT606 guarded rows and 98-unit train/held sequence artifact;
- GDT608 directed merge tree;
- GDT609 exact `model_v1.json` capacity;
- hash-pinned Caesar Latin, Dante Old Italian and five MHG4SNA texts already
  bound by GDT604.

No f84/f84r selector, new page, image, workshop gloss, target key, target
plaintext or target translation may enter. The inherited physical-folio split
is 68 train and 23 held.

## Frozen implemented capacity

- 34 primitive roles exactly: 18 literal, 4 syllabic, 3 prefix, 3 suffix,
  2 connector, 2 context-abbreviation, 1 whole-form, 1 null/layout;
- all 64 merges compose in directed left/right order by default;
- at most eight exact merge overrides and at most four whole-form overrides;
- null leaf mass at most 3%;
- `qok` cannot receive a whole-form override;
- role-specific output candidates and prefix/suffix/context placement penalties;
- square-root weighting of train chunk types;
- 60,000 deterministic simulated-annealing proposals per fit.

## Frozen runs

- synthetic planted Latin code: seeds 7001–7006;
- target Latin real seeds 1101–1106 and destroyed seeds 1191–1193;
- target Old Italian real seeds 2101–2106 and destroyed 2191–2193;
- target MHG real seeds 3101–3106 and destroyed 3191–3193.

Only prepared train chunks and the applicable reference pack enter the C++
fitter. The fitter source must not mention Held tables. A separate evaluator
then decodes all 9,838 held chunks on all 23 folios.

These hard buckets, mandatory null, heuristic transitions, word candidates and
lexicon bonus are properties of the simplified decoder. They do not implement
the exact soft-capacity FST in GDT609's bound `model_v1.json`.

## Reconstructed evidence rule

A concrete target output requires exact agreement across all six real starts
for the same primitive role+output, complete unit output, or complete source
record/start/end/ordinal word span. A positive real-minus-destroyed score or
dictionary hit alone is not an output assignment because those reference words
also define the candidate pool.

The post-run oracle audit is decisive: the planted truth ranks last of seven
keys under the exact objective, and five truth items are unobserved in train.
The control and objective are invalid. Target fits are therefore only archived
diagnostic stress outputs. No post-Held repair of the search objective,
capacity, candidate lists, iteration count or seeds is allowed inside this run.
