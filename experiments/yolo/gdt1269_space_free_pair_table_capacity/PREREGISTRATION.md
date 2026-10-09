# GDT1269 — small pair tables without trusting visible spaces

Registered before native pair counting,2026-10-07. Inclusive45minute allocation
20:28–21:13UTC includes selection, penlift preflight, prior/code review, proof,
implementation, validation and local closure. No cap/alphabet/width repair.

## Decision question and predecessors
Could a fixed small pair-code writer evade the older whole-word constraints
because visible group boundaries are decorative? Concrete writer family: a fixed
injective or synonymous lookup table with at most32distinct TWO-working-unit
entries, plus optionally ONE single-unit control h (e.g. an encoded source space).
No two-unit entry starts h. Encode source symbols by these entries, then permit
arbitrary extra display spaces/line breaks; the reader ignores display spacing
and reads h singly, everything else in pairs. The source-message lookup and any
source-space control remain distinct from decorative written boundaries. This is
an invented class, not an assigned native value or a historically attested code.

The fixed code size is a declared bounded alphabet-sized construction, not a
universal definition of human simplicity. Arbitrarily many homophones/entries,
variable-width codes, contextual codebooks and overlapping ink are outside it.
Report the necessary entry lower bound itself as well as the predeclared32gate.

1234/1235and1267assume whole groups belong to C*; that premise is relaxed here.
1259supplies an immutable exposed packet, but its integer-balance result is not
used as a modular/parsing theorem.001's fixed block model resets its block split
inside each visible word and allows homophonic language-model mappings; its
CONTINUE_BLOCK_CIPHER_UNSTABLE remains. This test neither retries that search nor
counts its instability as universal exclusion.1263's fixed rank condition is a
different question. No old proposed-next-step is reused as an unexecuted route.

## Minimal data and necessary bound
Use ONLY1259CERTIFICATES.json:23old selected whole paragraph records separately
for ZL3b and IT2a. They were selected for the earlier rank certificate, not this
hypothesis, but are historically exposed. RF remains absent, not inferred from
other readers. Parse unchanged literal whole strings by the old22working units;
join their units in stored order across spaces AND line boundaries. Retain a
pointer from every unit to its original group/locus. No source normalization,
new scope or rawTSVquery. The result only needs this bounded witness subset.

Do NOT assume even these paragraph edges are actual code boundaries. For each
snippet and each of23global configurations (no singleton, or h one of22units):
- phase0 starts a fresh code at the first observed unit;
- phase1 ignores the first observed unit as the second half of an incoming pair.
From that point read h singly when present at a code start, otherwise consume2.
A final unmatched unit is ignored as the start of an outgoing pair. h may occur
as the SECOND unit of a pair; it is then not a control. The no-singleton case
simply consumes pairs. Neither source grammar nor paragraph resets are imposed.

Let P0,P1 be the sets of complete pair TYPES in these two parses. At least one
is the true parse restricted to this snippet, so every global table must contain
P0 intersect P1. Union these intersections across all23snippets in one reader to
obtain L_h distinct mandatory pair types. The minimum over23configurations is a
necessary lower bound on any table in the entire family. It is NOT the exact
minimum realizable dictionary: independently favorable phases may be inconsistent
with a common table or global source stream. Missing-coverage/phase constraints
are relaxed deliberately; do not optimize them after output.

Save both complete pair lists with indices, each intersection and a source-bound
phase0/phase1 witness for every mandatory type. >32for everyconfiguration excludes
the bounded family in that reader; any configuration<=32means only the necessary
bound is inconclusive. Primary ALL_SMALL_PAIR_TABLES_EXCLUDED only if bothreaders
exclude; otherwise PARTIAL_PAIR_TABLE_CAPACITY_BOUND. Counts and minimumconfiguration
are descriptive, no pvalue, statisticalfit, wordmeaning or semanticrelation score.
A global unit renaming merely permutes the enumeratedh choices and pair labels.

## Controls, verification and stops
Before target, generated legal small code streams with every clipped start/end
check that the intersection is always a subset of the generatingdictionary.
Includeh in secondposition, singletonruns, absenth, partialincoming/outgoingpairs,
one-unit/empty snippets and the NO_SINGLETONcase. A separately implemented
validator uses step-state tracking instead of the primary greedyoffset loop,
independent exact22unit segmentation, rawsource offsets/counts and mandatorypair
unions. Imports no primary functions. Protocol, programs and input hashes locked
before native evaluation. The producer's source-free proof review uses no target.

If excluded, stop all at-most32pairentry writers of this shape even when display
spaces are arbitrary. If inconclusive, report only missing bound strength, no
bigger packet, fitted key, additional control symbol or full decoder. Stronger
multi-length/multi-control rules require a separate motivated contract.
This does not prove printedspaces ARE sourcewordboundaries; those alternatives
remain broader than this smallcode family. Exact working units/transcription
stay paid assumptions. No new nativeimage, f84/f84r, f116v or reserve. No source
language, phonetics or native meanings. Local4Octobercheckpoint only, no push.
