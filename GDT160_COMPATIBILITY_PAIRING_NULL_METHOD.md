# GDT160 compatibility-pairing null method

Status: **FROZEN BEFORE NULL SCORING**.

## Question

GDT159 left two facts separated: a real abbreviated corpus can reproduce the
Voynich operation count, and another can reproduce left-dominant edge support,
but none reproduced the frozen GDT003 compatible-pair density.  GDT160 asks
whether that density is merely a consequence of many individually supported
operations acting on a recurrent, restricted vocabulary, or whether specific
left and right operations are coupled into an unusually dense surface algebra.

This is a graph-structural test.  It assigns no morpheme, language, syntax,
sound, word, plaintext, or meaning.

## Inputs and seal

The target and comparator tokens are the already frozen GDT003 and GDT159
corpus panels.  GDT003 operation discovery and thresholds are used unchanged:

- minimum five source-target edge types;
- support on at least three training folds;
- the same fourteen operation strata and per-stratum truncation;
- a compatible operation pair requires at least three commuting three-cell
  hosts and at least one complete fourth cell.

Every fold is rediscovered from its training forms exactly as in GDT003.  No
new operation is added or selected from the null result.  The target file was
constructed with f84r excluded and contains no f84r record.  GDT160 does not
read a Voynich image, full transcription table, or f84r row.

## Exact decomposition

Before any randomization, the scorer must reconstruct the published aggregate
compatible-pair density exactly and partition its numerator and denominator
into LEFT×LEFT, LEFT×RIGHT, and RIGHT×RIGHT.  LEFT means PREFIX_ADD or
PREFIX_REPLACE; RIGHT means SUFFIX_ADD or SUFFIX_REPLACE.

The primary target is the LEFT×RIGHT component.  The published all-pair density
remains the reporting coordinate, so a null LEFT×RIGHT count is translated
back to the original denominator while the observed same-side components are
held fixed.

## Fixed-edge label-switch null

For a training fold, operation discovery defines a directed labelled graph:

`source form --operation--> target form`.

The null never changes a form, token occurrence, source unit, fold, string,
length, character, edge endpoint, or the number of outgoing transformations at
any host.  It randomizes only which operation identity labels existing edges
on one side.

Primary null, `RIGHT_LABEL_SWITCH_LENGTH_EXACT`:

1. keep every left-labelled edge fixed;
2. exchange labels only between existing right-edge slots with the same exact
   source-form length and target-form length;
3. accept a switch only when it creates no duplicate operation label at either
   source host.

This exactly preserves:

- the complete host and surface-form inventory;
- every token occurrence, token length and character frequency;
- form recurrence and its unit/fold/section/register placement, because no
  token or host annotation moves;
- every host's left and right operation degree;
- every individual operation's number of edge types;
- every operation's exact source/target length profile;
- the selected operation inventory and original GDT003 denominator.

It destroys only the assignment of particular right-operation identities to
particular pre-existing right-edge slots and therefore their specific pairing
with fixed left operations.

Two fixed sensitivities are required:

- `LEFT_LABEL_SWITCH_LENGTH_EXACT`, the direction-reversed label switch;
- `RIGHT_LABEL_SWITCH_RECURRENCE_STRICT`, which additionally requires the two
  source hosts to have the same exact sampled occurrence count, training-fold
  support count, and source-unit support count.

The strict sensitivity can retain more observed pairing because its switch
space is smaller; switch capacity must be reported rather than hidden.

This is an incidence-graph null, not a synthetic readable corpus.  A switched
edge label need not remain a literal prefix/suffix edit of its unchanged edge
endpoints.  That abstraction is necessary: with a fixed vocabulary and literal
deterministic operation semantics, every operation-host edge is already fixed
and there is no nontrivial conditional randomization.  The null therefore tests
whether operation *identities* are unusually arranged on the observed graph,
conditional on the graph and all listed margins.

## Compatibility under the null

A null three-cell support is a host with both a left-labelled and a
right-labelled outgoing edge.  A null complete rectangle is a directed square
whose opposite edges have the same left and right labels.  A pair is null
eligible under the unchanged thresholds of at least three host triplets and at
least one complete square.

The scorer reports the small calibration difference between this purely graph
definition and literal GDT003 commutation on the unshuffled graph.  The causal
excess uses graph-observed minus graph-null values; the exact published density
is never silently replaced.

## Randomization and reporting

- 1,024 retained worlds per corpus and null family;
- deterministic seed `1600032026` plus corpus/fold/null hashes;
- twenty attempted edge switches per switchable edge for burn-in and one per
  edge between retained worlds;
- folds randomized independently and summed by common world index;
- inclusive empirical tails `(1 + null >= observed) / 1025`;
- the same procedure for Voynich and all five GDT159 diplomatic corpora.

For each corpus/null report observed graph density, null mean and interval,
survival fraction `null_mean / observed`, absolute excess, ratio, z score,
inclusive p, switchable edge fraction, and fold-direction stability.

For Voynich, aggregate each named LEFT×RIGHT operation pair across folds and
report observed eligible-fold count, null expected eligible-fold count, excess,
triplets, complete rectangles, operation supports, and concentration of the
top pairs.  Pair rows are descriptive after selection and receive no individual
confirmation claim.

## Decision vocabulary

- `PAIRING_EXCESS_NOT_ABOVE_DEGREE_NULL`
- `PAIRING_EXCESS_PRESENT_BUT_DIFFUSE_OR_UNSTABLE`
- `SPECIFIC_LEFT_RIGHT_PAIRING_EXCESS_SUPPORTED`
- `INSUFFICIENT_NULL_MOBILITY`

The strongest decision requires the primary right-label null to have at least
25% switchable right edges, positive excess on at least 9/12 Voynich folds,
inclusive p <= .01, null survival below 75%, and the direction-reversed null to
agree.  The recurrence-strict sensitivity is descriptive because its mobility
is data determined.

Even a positive result establishes only excess organization of the frozen
surface-operation graph.  It does not establish linguistic morphology,
semantic composition, a word boundary, language, sound, plaintext, or
translation.
