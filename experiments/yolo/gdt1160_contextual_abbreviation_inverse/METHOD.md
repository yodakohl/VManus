# GDT1160 — contextual recovery of ambiguous historical expansions

## Question and decision

Does surrounding written text improve selection among real editorial expansions
of the same exact retained marked group? Does one fixed small neural architecture
earn additional complexity over a linear contextual competitor?

GDT155 tested site lookup and character backoff, GDT157 forward abbreviation
generation. GDT832 already shows contextual value in a synthetic mixed channel,
but its co-lemma factor adds none. GDT835/995 resolve known wrong synthetic maps
through writing constraints; those errors are not the present endpoint. Here
several expansions share the same retained marked source representation.
GDT001 already implemented a GRU for source-symbol prediction; this is not the
project’s first neural experiment. That language-model/null task did not perform
this supervised human-source expansion inverse.

A positive can select a supervised ranking component for later finite candidate
tasks. A negative stops this fixed architecture. Neither outcome supplies a
Voynich candidate lattice, language, spelling channel or translated word. No
automatic decoder restart or architecture repair follows.

## Source and admission

Only three frozen GDT155 TSVs enter: blinded diplomatic lines, blinded sites and
aligned editorial expansions. Their SHA256 values are in SPEC.json. Human-edited
Nuremberg council letterbooks 2–5 contain 48,337 lines in 3,176 complete records.
The source audit and attribution remain GDT155_MEDIEVAL_ABBREVIATION_SOURCE_AUDIT.md.
No images, HTR predictions, automated vision, external pretrained model, Voynich
transcription or reserve is an input. f84 and f84r remain sealed.

All source labels have previous project exposure. These held-book partitions
measure procedural transfer, not fresh analyst blindness. Four related books
are not four independent historical traditions. The editorial placeholder `¤`
does not retain a native abbreviation-sign inventory; ambiguity here is not a
demonstration of original graphical homography.

## Fixed panel and legal alternatives

Preserve case, long-s, Unicode and marker position. A site is eligible only when
its marked span equals its entire containing whitespace group and that group
has exactly one marker. No filtering on gold expansion length is permitted.
This yields 118,843 source sites. In each leave-one-book-out partition a type
qualifies if at least two different expansions each occur at least five times
on at least three distinct training pages. Its candidate domain retains ALL
training-attested expansions, including rarer alternatives. No held answer
enters eligibility, the domain or a predictive feature.

All held occurrences of qualified types enter: 3,043 / 4,870 / 4,763 / 8,836.
The 171 held truths absent from their training domains remain errors. This
panel differs from GDT155's normalized whole-source recovery denominator;
its reported 93.7% is not the baseline for this experiment.

## Inputs and models

Order all physical lines within each complete source record and their written
whitespace groups. At every site take up to eight groups on each side, crossing
lines but never records. Exclude offset zero. Neighbors remain diplomatic,
including other editorial markers; never substitute their gold expansions.
Encode exact within-group character 2-, 3- and 4-grams, tagged by signed group
offset, into 4,096 deterministic hash bins and L2-normalize each context row.
No corpus-fitted normalization or vocabulary is supplied by held labels.

The shared remaining features are an exact training-type one-hot and ten layout
features: source record-position quartile, group-position quartile in its line,
and first/last source line indicators. Line group count comes from the actual
marked whitespace groups, not the historical bare-group-count column (which
differs on eight source lines). Record, page and book identities cannot
be lookup predictors. Numeric writer IDs are not assumed to identify the same
person across books and are not used.

F is empirical training candidate frequency. L adds a learned linear layout/type
score to fixed log F. C adds linear contextual features. N uses the same C input
through one 64-unit ReLU hidden layer. Every model uses identical train candidate
masks. Exact algorithms and optimization settings are in SPEC.json: 20 epochs,
two fixed seeds, AdamW, no hyperparameter search or best-run choice. Average the
two final candidate probability vectors; retain individual vectors and losses.

This is a fixed architecture comparison. Its bottleneck, parameterization and
optimization differ from C; an N advantage does not isolate nonlinearity or
establish neural necessity. Positional local features do not warrant a claim
about long-range grammar. Retain optimization curves and disclose possible
underconvergence; do not tune against held results.

## Endpoints and gates

For each book compute the equal mean of exact-expansion accuracy across its
eligible marked types. The primary metric is the equal mean of four book
metrics. A context arm earns retention only if its primary gain above the
stronger F/L primary score is at least .03 AND it beats both F and L in at least
three books. N additionally requires at least .01 above C and positive N–C in
at least three books. C and N are evaluated separately against their gates.

Publish token accuracy, each type, complete-record ambiguous-site accuracy,
every wrong/OOV prediction, and all seed results. Secondary subsets are fixed
before fitting: train-supported pairs differing only in terminal m/n, and
contexts whose exact sixteen-neighbor signature was unseen for that marked
type in training. Missing neighbors are explicit in that signature. Neither
subset removes primary errors or selects a revised model. m/n is a formal
contrast, not a verified case label. Report repeated contexts rather than
silently dropping them. No significance claim is planned.

Prediction artifacts are frozen before separate held scoring. This procedural
separation does not erase earlier label exposure. Independent checks reconstruct
the panel, candidates, features and prediction accounting. Reproducibility
checks are not evidence of manuscript meaning.

## Budget and stop

Selected 2026-10-03 06:25:07 UTC. The 90-minute inclusive checkpoint is
07:55:07 UTC, covering preparation, implementation, fitting, validation and
publication. At that point reassess expansion; do not automatically repair or
extend the model. Complete an already-running fixed test without interpreting
an implementation delay as a scientific failure. Keep old experiments frozen.
