# GDT1382 — Homophonic context-identity lower bound

## Decision note (before implementation and native evaluation)

GDT194 searched only three coordinate-descent starts; no global exclusion follows.
GDT1380/1381 now certify six fixed injective costs on NEW_PAGE_HOST, but their
reserved target slots are invalid for many-to-one mappings. IDEA001052 already
contains the weaker homophonic relaxation; this is its first scoped execution
with all within-row source identity constraints. Bounded route/duplicate screens,
194/1380/1381 primaries and followups, and an independent review found no executed
identical certificate. GDT883 is a different overlapping-block architecture;
GDT1322 prohibits dropping variant likelihood when scoring actual keys, but does
not prohibit dropping a nonnegative cost in an explicit lower bound.

Positive retained constraint: a fixed sign-to-consonant writer must reuse the
same output whenever that sign occurs, including repeated context/next signs.
Unknown: is that constraint alone, while allowing all distinct signs to collide,
enough to make the six fixed target models lose against matched native KT?

Smallest test: finite per-context enumeration, at most21^2 target pairs, no global
key search. All three frozen reader corpora and all six frozen models are declared.
Budget35minutes inclusive of preparation, implementation, validation and publication,
starting2026-10-13T14:41:15Z. A positive margin closes that precise reader/model cost
comparison; otherwise the comparison stays open and this bound branch stops.
No automatic tightening, partition solver, alternate corpus or reverse-channel
search follows either outcome. This is a cost exclusion, not translation progress.

## Frozen dependencies and assumptions

Use GDT1380 artifacts/CORPUS.json.gz and MODEL_COUNTS.json.gz unchanged. Readers
ZL3b, IT2a, RF1b are separate alternative readings, not independent replications.
All six packs: latin, medieval_czech, middle_french, middle_high_german,
old_hungarian, old_italian_tuscan. No new source selection, parser, extraction,
licensing, training or target choice. This is lossy ASCII NEW_PAGE_HOST, not
literal Voynich phonemes and not old GDT194's pooled historical input.

Let m be the frozen reader's active ordinary alphabet size, including rare signs.
Every ordinary source sign maps to one of C=bcdfghjklmnpqrstvwxyz, with replacement.
SPACE maps only to SPACE; BOS is a fixed history marker. No source symbol is
silently removed and no 21-source-sign capacity limit applies. Line resets,
no EOS, context counts and selected groups are exactly those of GDT1380.

Use unchanged order2 target probabilities (2n+1)/(2T+22). Primary imports only
GDT1380's certified Decimal60 integer-tick arithmetic and KT helper. Validator
uses GDT1380's independent Decimal80 arithmetic and KT helper. Scale2^32ticks/bit.
Compute matched order2 KT intervals with m+1 outcomes for EACH reader from the
frozen contexts. IT2a interval must exactly equal1380; the two other intervals
were not calculated there because its injective family was empty.

Paid key cost is m*log2(21), language selector log2(6); lower interval endpoints
used. Shared overhead cancels under the same fixed scope. The global Dirichlet-half
reverse cost of194 is nonnegative and bounded below by0. No actual key is scored
without its reverse cost. Other nonnegative reverse costs would preserve this
inequality ONLY with the same forward model and key accounting.

## Local minimization and proof

For each native context(u,v), collect distinct ordinary context signs, excluding
SPACE and BOS. Enumerate all assignments of these signs to C WITH REPLACEMENT.
Repeated source signs have one shared image. Different signs may share an image.
This determines the target context and hence its22 lower cost ticks.

Charge SPACE next-events at its fixed target cost. Each ordinary next-sign also
occurring in the context pays its assigned target cost. All other ordinary
next-sign counts are pooled and multiplied by the cheapest ordinary target cost.
No target is reserved: these signs may reuse any context target and each other's
images. Minimize over context assignments, breaking ties by target-context tuple.
Store every row's lower cost and minimizing target context; sum the minima.

Every global many-to-one key restricts to a permitted local assignment. The free
next-sign assignments include its choices and can only improve their cost.
Minimizing rows separately drops cross-row key consistency, again only improving
the cost. Finally dropping a nonnegative reverse cost cannot increase it.
Thus sum(row minima)+key_lower+selector_lower is a certified lower bound for
EVERY global194-style key on these frozen inputs. Row minimizers are not a key.
No comparison to the old injective lower bounds is required or informative.

## Decision and controls

Per reader/pack: paid lower minus matched KT upper >0 yields
CERTIFIED_NO_KEY_BEATS_MATCHED_KT; otherwise BOUND_INCONCLUSIVE. No tolerance,
posthoc source filtering or language/reader pooling. Report all18 comparisons.
Nonpositive bounds neither exhibit a successful key nor favor homophony.
A positive bound is conditional on these corpora, representation, static forward
map and cost contract; it is not a general language or consonantal-writing ban.

Before native evaluation, freeze protocol, programs, input/helper hashes and
proof review. Source-free exhaustive controls must compare local minima with
all maps on tiny alphabets and global sum bound with all global maps, allowing
more source than target signs. Include repeated context/next identity, distinct
context collisions, free successor reuse of context targets, SPACE/BOS and a
strict improvement over the unconstrained homophonic minimum. Independent
validator must replay all row certificates and complete cost accounting without
importing the new primary program. No new meaning, sound assignment, image,
reserve, f84/f84r, f116v or f1r-body use.
