# F69C001: f69r six-fragment circular word-likeness test

Status: **PRESCORE REGISTRATION — TARGET UNOPENED**

## Question and claim ceiling

The six manually transcribed center pieces on f69r form an author-visible
circular sequence. This experiment asks only whether some dihedral ordering of
those six pieces is unusually compatible with manuscript-internal character
transitions learned from ordinary prose words.

A positive result may support only this statement: **the six pieces admit an
unusually ordinary-word-like circular order under the frozen model**. It may
not identify a start, handedness, sound, word, root, lexeme, language,
plaintext, direction name, or translation. A negative result closes only this
specific word-likeness model.

## Input provenance

- Text source: the cached manual ZL3b, IT2a, and RF1b transcriptions.
- Training rows: prose rows (`kind=P`) only.
- No OCR, automated image analysis, embeddings, captions, or plant guesses.
- The target geometry and six readings come only from the existing manual
  locus/cross-transcription records. They must not be read or scored by the
  calibration runner.
- All f69 rows are excluded from calibration and target model training.

## Frozen model

For each reading independently, fit one add-0.5 order-2 character Markov model
to lowercase ASCII prose words. A word `w` contributes the transitions in
`^^w$`; the score is the sum of log conditional transition probabilities
divided by `len(w)+1`. The prediction alphabet is the fixed 27-symbol set
`a`--`z` plus `$`.

For any six distinct chunks, score all `6! = 720` labeled linear assignments.
Assignments are grouped under rotation and reversal into exactly 60 dihedral
orbits. An orbit receives the maximum score of its 12 orientations. Rank is
tie-inclusive: one plus the number of *other* orbit scores greater than or
equal to the observed score. Thus rank 1 requires a unique top orbit.

For every scored item, training excludes:

1. the item's complete physical page;
2. every lowercase surface produced by all 720 chunk assignments; and
3. every f69 page.

This prevents exact candidate lookup. No alternative order, smoothing value,
normalization, corpus kind, or tie rule may be selected after calibration.

## Prescore ordinary-word calibration

Calibration creates only synthetic chunk puzzles from ordinary seven-letter
prose words; it has no access to the f69r target chunks.

For each eligible word occurrence and reading:

1. Require a lowercase ASCII surface of length seven on a non-f69 prose page.
2. Hash `reading|page|locus|word_index|surface` with SHA-256.
3. Let the first eight hash bytes modulo six select one of the six adjacent
   character pairs. Keep that pair as a digraph and the other five characters
   as singleton chunks, in original word order.
4. Require all six chunk strings to be distinct.
5. Retain the two lowest-hash eligible occurrences per physical page, then the
   lowest 128 retained occurrences overall.

The true orbit is the dihedral orbit of original chunk order. A deterministic
pseudo-nontrue control orbit is selected by the next eight hash bytes modulo
the other 59 orbits. Report complete trial/page counts, true inclusive ranks,
and pseudo-control inclusive ranks.

Calibration passes only if **every reading** satisfies all of:

- at least 96 trials from at least 40 physical pages;
- at least 35% of true orbits have inclusive rank 1 of 60;
- median true inclusive rank is at most 3;
- at most 8% of pseudo-nontrue orbits have inclusive rank 1.

The calibration runner must emit aggregate artifacts only and must neither
contain nor print target strings or target locus identifiers. A separate
nonimporting scalar validator must reconstruct the eligible samples, all 60
orbits, ranks, controls, gates, and absence of a target artifact before target
access is authorized.

If calibration fails, record and publish the failure and do not score f69r.

## Frozen target test, conditional on calibration pass

Only after the calibration artifacts have passed independent reconstruction
may a separately committed target runner bind the six manual target pieces.
ZL3b/RF1b and IT2a keep their documented alternate reading in the same chunk
position; the three transcriptions are alternate readings, not independent
manuscripts.

Within each reading, standardize all 720 orientation scores. For each common
labeled orientation take the minimum of the three reading-specific z-scores;
for each of the 60 common dihedral orbits take the maximum of its 12 combined
orientation scores. The target result is provisional only if all frozen gates
pass:

- one unique combined rank 1 of 60 (`p = 1/60` under the exact orbit null);
- the target orbit ranks at most 3 in each individual reading;
- in the six leave-one-chunk-out tests, at least five target orbits rank at
  most 2 of 12 and none ranks worse than 4 of 12;
- a deliberately misaligned-reading fixture and a deterministic random-orbit
  fixture both reject; and
- a separate nonimporting implementation reproduces every input hash, score,
  orbit, rank, deletion, fixture, gate, and decision.

Even a complete pass remains a structural word-likeness result under one
manuscript-internal model. It is not a translation.

## Immutability rule

After this registration is committed, any implementation correction must be
documented before target access and may only make the code conform to this
text. Changing a gate, sample rule, model, score, orbit definition, or claim
ceiling creates a new experiment ID and may not reuse F69C001 as confirmation.
