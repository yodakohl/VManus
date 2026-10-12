# GDT1353 — Forced single entries under arbitrary-size freely UD codes

## Decision note before native calculation

The user requests continued phonetic construction.892's control capacity stop,
905/906's completed fixed Latin grammar failure,1350's manner failure and1351's
representation counterexample remain.1352did not identify linguistic units.
An assumed fixed variable-length phonetic code can instead face whole-word
constraints without selecting a language or sound key.

1235supplies short-code obligations (15/16/13forced singletons in IT/RF/ZL), with
later<=22entry exclusions.1267proves k/e/s under general freeUD and explicitly
records its broader native closure as UNEXECUTED: its selection_draft remains
byte-frozen. This test does not claim novelty for the closure algorithm. The
changed question is the entire forced-singleton intersection at ANY codebook
size, with explicit omission countercodes to separate unforced from unresolved.
1248's valid27entry prefix covers already prevent forcing every working unit;
cfh,cph,q cannot be declared mandatory singles on FULL. No old failure is rerun.

Outcomes change the permitted joint segmentation search: additional mandatory
singles rule out codes hiding those signs exclusively inside longer blocks;
explicit omission codes prove remaining freedoms. If the closure adds no useful
constraint, or countercodes do not complete the classification, report that
limit and stop. No automatic larger code search or source dictionary fit.
Smallest adequate test: finite sound quotient closure and simple per-sign
countercodes, plus full-word parse checks. Budget35minutes from first recorded
09:33:34UTC including subsequent retrieval, proof, coding, validation and
publication. Initial retrieval before that clock has no invented exact duration.

## Contract and existing input

C is any fixed set of distinct nonempty strings over the22working units. Every
finite sequence of C entries decodes uniquely (freeUD). Each retained whole
group is in C*. No prefix/suffix condition or cardinality cap on C. Entries
could stand for phonemes or other units; no interpretation is selected. One
fixed form per entry, no nulls, overlaps, context spellings, crossed spaces or
splitting inside an existing working unit. Grammar-assisted ambiguity is outside
this contract. Working-unit and complete-source-word assumptions remain paid.

Use only unchanged1233GROUPS.json.gz and its old allowlist. Readers separate.
FULL primary and GE2 sensitivity: retain whole forms on>=2physical leaves,
stripping side/foldout suffix. GE2does not repair rare readings or create a
holdout. Keep all22target signs, report active symbols separately. No new source,
image, raw mixed TSV, f84/f84r, f116v/f1rbody or reserve. No word meanings.

## Forced obligations

If x,xy,yz,z are in C*, y is too. By freeUD their codeword lists obey A D=B E
from x·yz=xy·z. Nonempty codes imply the boundary after x precedes the boundary
afterxy; the intervening whole entries spell y. A one-unit y must be a code entry.
One-sided cancellation is INVALID for generalUD: C={a,ab} does not contain b.

Initialize U with every panel whole-word type plus empty. Each round compute
left remaindersy from x,xy in U and right remaindersy from yz,z in U. Add common
nonempty remainders with four-parent proofs. Deterministic primary order is
lexicographic units, then split index; additions occur only after each round.
Every new string is a substring of an initial whole word, so closure terminates.
Archive all nodes, source-root counts/leaves/first exact row, parents and rounds.
This is least closure under ONE rule, not claimed complete logical free hull.
30second soft closure budget per panel, checked at round boundaries (one round
may overrun), maximum200000nodes; if hit, retain sound partial proofs and
report incomplete, never negative or exact. No increase or other rule afterward.

Report forced singletons, recursive source roots for each, and whole groups/types
whose every sign is forced. Such groups have their singleton parse in C*, so
freeUD forbids any competing longer-code parse. This is conditional segmentation,
not sounds or a meaning percentage. Report per-proof rare-form support; no claim
the first selected proof is the strongest possible. GE2is a separate sensitivity.

## Explicit countercodes for every other sign h

First try: if no panel word ends with h, split every whole word into maximal
blocks h^k a with a!=h andk>=0. Keep all actually used blocks as C_h. This is
prefix-free: another such block cannot extend one after its first non-h unit.
It covers every panel word and omits singletonh. If this condition fails but no
word starts h, apply the reversed construction a h^k: suffix-free, same coverage.
When h is unobserved the resulting singleton table simply omits that unused h.
If neither condition holds, mark h UNRESOLVED and launch no further search.
Keep the exact table, use counts and codebook size for each h. No invented source
labels or unused-code activity. Verify no forced singleton is omitted.

If closure is complete AND every nonderived h has a valid omission countercode,
the forced-singleton set is EXACT as intersection over all admissible C. Otherwise
report a lower bound plus explicit counterexamples and unresolved signs. Different
h may require DIFFERENT codebooks: no joint omission, minimum codebook size,
optimal alphabet or actual historical writer follows. Candidate countercodes are
allowed to depend on this exposed corpus; coverage is not predictive success.

## Verification and retained limits

Primary adapts1267's archived finite closure pattern; legacy bytes not changed.
Validator imports no runner, reparses raw forms, reconstructs GE2/source roots,
replays every acyclic proof, independently checks fixed-point residual membership,
and verifies each omission table is prefix/suffix-free. Independent dynamic
programming counts exactly one parse for every distinct whole word under each
table. Rebuild entry usages and group activity from those unique parses.

Source-free fixtures retain false one-sided inference{a,ab}, a valid non-bifix
UDtable{a,ab,bba}, and a nonUD collision{a,ab,bc,c}. W={ab,ba} shows appearing at
both ends does not itself force singles. Test the omission construction on every
binary word up to length6meeting its endpoint condition, including runs. No
post-result arbitrary decoder repairs. Accounting proof validation is not new
palaeography or confirmation of the whole-word/unit/phonetic premises.
