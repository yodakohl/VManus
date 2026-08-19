# GDT360 existing-annotation joint grounding method

Status before scoring: **EXPLORATORY METHOD FIXED; NO NEW VISUAL ACQUISITION**.

## Question

Do already acquired, provenance-bound visual observations jointly predict any
source-native formal construction across unseen physical folios after broad
section, Currier, hand, layout-kind, and source-code nuisance is conditioned
out?

This is a deliberately permissive YOLO discovery pass. Weak, asymmetric,
uncertain, one-sided, and previously exposed observations remain usable. Old
capacity and validation gates remain historical facts, but are not discovery
kill rules. The unit of interpretation is a complete candidate world composed
of several neutral visual–formal associations, not an isolated glyph gloss.

## Existing evidence only

No manuscript image is opened. The fixed inputs are:

- the complete exact-locus human annotation layer derived from Stolfi's source
  comments;
- the current 80-row GDT002 exploratory visual–formal join, including CONTACT /
  CLEAR_GAP, BFE enclosure, and f80r/f82r layout observations;
- the existing zodiac clothing, star-tail, barrel, and facing inventories;
- the existing special-circle ray/ownership and slot-capacity inventories;
- the source-native three-reading family-consensus loci/groups;
- GDT327 exact joint tuples, used only where that interlinear already has
  coverage.

Derived tables, source comments, crosswalks, and catalogue rows descending from
the same source assertion are one evidence lineage, not independent witnesses.
Rows from different annotation channels on the same manuscript locus are also
not independent manuscript samples. The inventory records those dependencies.

## Visual endpoints

Every endpoint is an observable class, never a meaning:

1. exact local human relations, each contrasted against explicit
   proximity-only comments: attachment, enclosure, contact/overlap, and
   array/group;
2. explicit visual object contexts: plant, figure, star/sky, and
   water/apparatus, each against other explicitly tagged contexts;
3. the three existing GDT002 channels;
4. clothing, star-tail, barrel, facing-profile, and star/group ownership
   channels from already published inventories.

Hedged human assertions remain in the main exploratory scan and are rerun as an
unhedged-only sensitivity. `UNCERTAIN` visual states remain in the inventory but
are missing from the primary binary score. They are never forced to either
class. One-sided pages/arrays are retained descriptively and can contribute to
held-folio prediction, though not to a within-unit permutation.

## Formal features

The main representation is the frozen source-native family consensus. The
state-blind feature library contains:

- family-component presence;
- within-source-group family bigrams and trigrams;
- first-group prefixes and last-group suffixes of length 1–3;
- delimiter-preserving recurrent exact family expressions;
- symbol-count and source-group-count bins;
- synchronized boundary types and alternative-reading status.

N-grams never cross a physical source-group boundary. Globally identical
state-blind locus masks are collapsed to one canonical predicate and their
other formal descriptions are retained as aliases. A feature is admitted
without consulting visual states only if it appears on at least four eligible
loci and on at least two physical folios, with at least four eligible loci not
carrying it. Exact GDT327 tuple IDs remain atomic; their coverage is audited as
a secondary ceiling and is not silently replaced by PAGE_HOST substrings.

## Ranking and controls

Each binary endpoint is scored separately. A smoothed low-capacity model is
trained on all non-held folios and predicts the held folio. Its nuisance key is
section × Currier × hand × layout kind × source code. The candidate model adds
one formal predicate. Reported `lofo_gain_bits` is its total held codelength
saving over the nuisance model.

Two 1,024-world permutation diagnostics are fixed:

- nuisance-stratified permutations preserve positive counts within the broad
  nuisance key;
- topology-local permutations preserve counts within the source-defined array,
  ring, page-unit, or page when no finer existing unit is available.

A third sensitivity further refines the topology-local key by exact source
symbol count and source-group count. Its frequently tiny mobile orbit is
reported as an opportunity-matching capacity diagnostic, not used as a
discovery kill gate.

The candidate library is constructed state-blind. MaxT is taken across the
complete admitted library in every nuisance-permutation world. The local
topology diagnostic is allowed to have zero mobility; that is reported as a
confound rather than an automatic stop. Selector-paid bits subtract the literal
single-rule search cost `log2(features × endpoints × 2 directions)`.

The joint-world atlas groups the same formal predicate across two or three
different evidence families. It sums only positive held-folio gains, disallows
multiple endpoints from the same evidence family, records locus overlap, and
charges feature, endpoint-subset, and direction choices. These worlds are
postselected exploratory summaries, not posterior probabilities.

Labels are assigned mechanically:

- `INTERESTING_EXPLORATORY`: at least 4 held bits, at least three positive held
  folios, nuisance local `p<=.05`, maxT `p<=.20`, topology-local `p<=.10`,
  and at least ten topology-mobile rows;
- `LIKELY_PAGE_CONFOUND`: a nominal nuisance association has fewer than ten
  topology-mobile rows or topology-local `p>.20`;
- `WEAK`: positive held gain with at least two positive held folios or nuisance
  local `p<=.10`;
- `UNSTABLE`: nominal association but nonpositive held gain;
- `NO_SIGNAL`: none of the above.

Relation tags and object-context tags derived from the same exact human row
share one evidence lineage and cannot jointly satisfy a multi-channel world.
These ranks guide acquisition. They do not confirm or kill a semantic theory.

## Holdout and claim ceiling

All `f84*` rows are rejected by `GuardedTSV` before parsing. No f84 payload,
image, commitment, or prediction is opened or changed.

At most GDT360 can identify a dirty but reusable association between a neutral
visible relation/context class and a source-native formal signature. It cannot
establish an object name, semantic role, word, morpheme, POS, sound, language,
plaintext, translation, or universal manuscript grammar.
