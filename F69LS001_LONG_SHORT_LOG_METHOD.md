# F69LS001 — f69v long/short log feature test

Status before target execution: `REGISTERED_EXPLORATORY_TARGET_UNRUN`.

## Question

The human Stolfi catalogue marks 28 f69v radial loci as an exact clockwise
alternation of 14 long and 14 short graphical “logs”, one text locus per log.
Does any complete source-native text feature consistently distinguish the
LONG and SHORT members of the 14 adjacent pairs?

This is not F69M001's external lunar-mansion-name alignment and it is not the
earlier terminal-`y`-only parity check. It tests a frozen, complete surface and
STA-family feature inventory. The route was selected after the labels had been
seen, so even a pass is exploratory until an independent graphical array
replicates it.

## Frozen inputs

- `experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv`
  SHA-256 `79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61`
- `experiments/semantic_assumptions/results/source_separator_transcription.tsv`
  SHA-256 `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`
- `experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv`
  SHA-256 `84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77`

The panel must contain exactly `f69v.X1.1` through `.28`, exactly alternate
LONG/SHORT beginning with LONG, and have all ZL3b/IT2a/RF1b source rows plus
one STA consensus row per physical locus. Alternate readings are three
measurements of the same marks and are never counted as replications.

## Frozen features

For each reading, join all complete manual source groups within a locus without
silently deleting a group. Build:

- compact length and source-group count;
- presence and count of every observed single ASCII character;
- presence and count of every observed compact bigram;
- presence of every observed compact trigram;
- exact prefixes and suffixes of lengths 1 through 4.

From the all-reading consensus STA-family sequence build the analogous family
presence/count, bigram presence/count, trigram presence, and exact prefix and
suffix features of lengths 1 through 3. Repeat these invariant values across
the reading axis only so the same coherence code is used; this does not create
three observations.

Binary features are eligible only when their total support is 6 through 22 in
every reading. Count/scalar features require nonzero variance in every reading.
Every retained feature must additionally have nonzero exact paired-null
variance in every reading under both the FORWARD and BACKWARD pairing. This
last condition is invariant under every allowed within-pair flip and prevents
undefined standardized effects; it does not select an effect direction. Exact
duplicate `feature x reading x locus` matrices are collapsed to the
lexicographically first feature name, with all aliases retained. The eligible
feature inventory is fixed before LONG/SHORT scoring.

## Exact statistic and null

For each feature and reading, compute

`effect = mean(LONG) - mean(SHORT)`.

Enumerate all `2^14 = 16,384` flips that exchange LONG and SHORT within each
adjacent pair. Use the population standard deviation of that complete null to
standardize each reading effect. A feature score is the minimum absolute
standardized effect over the three readings when all three effects have the
same nonzero sign, and zero otherwise. The primary statistic is the maximum
feature score. Inclusive maxT p-values use the complete orbit, including the
observed all-unflipped assignment.

Run two equally defensible local pairings:

1. `FORWARD`: each LONG position with the following SHORT position;
2. `BACKWARD`: each LONG position with the preceding SHORT position.

The observed feature effects are identical; only the paired null changes.

## Frozen gates

A structural lead requires all of:

1. exact input hashes, 28-unit ownership, order, alternation, and coverage;
2. finite matrices and nonzero null variance for every eligible feature;
3. one unique top feature shared by both pairings, with one direction across
   readings;
4. inclusive maxT `p <= .01` under both FORWARD and BACKWARD pairings;
5. minimum common-reading standardized effect `>= 2.5` under both pairings;
6. material raw effect: `>= .35` for binary features, otherwise the absolute
   mean difference divided by the population standard deviation over all 28
   loci is `>= .75` in every reading;
7. every leave-one-pair-out raw effect keeps the same direction in every
   reading under both pairings;
8. no single pair supplies more than `.35` of the absolute observed paired
   numerator in any reading under either pairing;
9. planted, one-reading-only, concentration, tie, and malformed synthetic
   controls behave as declared; and
10. a nonimporting validator reconstructs the complete orbit and artifacts.

## Claim ceiling

A pass would identify only a source-native feature associated with the local
LONG/SHORT graphical state on f69v. It would not establish lunar mansions,
days, numbers, length words, an authorial phonology, language, plaintext, or
translation. Because the route is post-selection and one-folio, it would remain
provisional until an independently selected graphical array replicated it.

A failure closes this complete frozen surface/STA feature family for the f69v
LONG/SHORT contrast. It does not refute a 28-part astronomical interpretation.
