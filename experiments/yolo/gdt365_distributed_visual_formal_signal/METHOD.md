# GDT365 distributed visual/formal signal method

Status: **POSTEXPOSURE MODEL FROZEN BEFORE DISTRIBUTED FORMAL SCORING**.

## Question

GDT363 and GDT364 ranked one anonymous source-family feature at a time. Neither
had an adjusted signal, but GDT002's central exploratory premise is that weak
constraints may combine. GDT365 therefore asks whether a small distributed
formal representation predicts either already frozen visual endpoint:

1. leaf margin: 29 SMOOTH, 13 TOOTHED, two retained missing;
2. reproductive structure: 19 FLOWER_SIDE, 8 BERRY_NO_CIRCLES, 7 explicit
   NO_FRUIT_OR_FLOWER pages.

Both endpoints and all source text have already been exposed. This is a
postexposure model-class test, not confirmation. No Pharma local-axis model is
run: existing CONTACT×root-colour, root-colour×root/leaf, and flower×root-colour
overlaps are only 2, 6, and 7 loci respectively.

## Frozen instrument

- Construct one state-blind family feature vocabulary on the union of both
  page panels. Features are exactly the nonlexical GDT363/GDT364 classes:
  component rates, within-group bigrams/trigrams, first-prefix/last-suffix,
  boundary classes, and multi-group construction rates. Require presence on
  at least eight union pages and absence on at least eight.
- Exclude exact families, surfaces, member IDs, roots, PAGE_HOSTs, tuples,
  EVA, and all meanings.
- Within every held fold, regress the formal matrix on Currier/hand, quire,
  folio-rank quartile, page side, source-group/locus volume, mean source-group
  length, label rate, and reading-alternative rate using ridge 8. Standardize
  the residual using the training fold only. In an endpoint where a nuisance
  is invariant, its column is inert rather than omitted adaptively.
- Learn PCA on training residuals only. Score fixed dimensions 2, 4, and 8.
- Use a smoothed nearest-class-centroid likelihood with equal spherical
  covariance. Compare its held codelength with the training class-prior code.
  No dimension, threshold, or feature is chosen from the outcome.
- Primary transfer is leave-one-physical-folio-out. Leave-one-quire-out is the
  stronger register/locality diagnostic.

Use 1,024 deterministic endpoint-specific state permutations: leaf states
within Currier × folio-rank quartile; reproductive states as whole-folio state
vectors within quire × page-count. Report local and max-six tails across two
endpoints × three dimensions.

## Decision language

- `DISTRIBUTED_SIGNAL_INTERESTING_EXPLORATORY`: positive folio and quire gain,
  positive on at least half of folio folds, and max-six p <= .20;
- `DISTRIBUTED_SIGNAL_LOCAL_OR_UNSTABLE`: positive folio gain but held-quire
  failure or no adjusted support;
- `NO_DISTRIBUTED_SIGNAL`: nonpositive held-folio gain.

These labels rank hypotheses; they do not alter GDT363/GDT364 or assign a
formal family to a visual state.

## Seal and ceiling

Reject every f84 selector before formal-field parsing. No image or catalogue
is opened. At most, a pass would show that a low-dimensional anonymous formal
page profile carries transferable information about one already annotated
visual axis. It would not identify a word, role, plant, lexeme, morpheme,
sound, language, plaintext, meaning, or translation.
