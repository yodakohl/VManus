# GDT1321: unordered nonreturning blocks inside complete written groups

Decision note10October2026. Preparation11:09UTC onward; budget through11:35UTC
includes source review, proof, implementation, validation and publication. Stop
expansion at outcome. No changed alphabet, exception budget or repeated-role repair.

Question: can each written group be a compact record of distinct fields, each
field written as a single contiguous block using its own fixed sign class, while
the order of fields varies freely from one record to another? This differs from
GDT1263's one global field order, whose full-panel failure is retained. AB and BA
are legal together here; ABA is not unless the two classes are actually one.
The older SCC obstruction alone does not answer this weaker question.

Content-preserving abstract writer: the source is a finite ordered list of distinct
field labels, each with a nonempty payload string in its own disjoint alphabet.
Write the payloads consecutively. Read maximal constant-class runs, recovering each
field label and every payload symbol in order. This is an invertible restricted
record notation, not a code for arbitrary natural-language interleaving. Every
working unit has exactly one field class globally per reading. Field counts and
orders vary; no field may recur after another field in one written group. No
actual field names, source sounds, natural alphabet or word meanings are assigned.
Positive motivation is known structured word building, not proof of this contract.

Unknown after predecessor review: maximum number of distinguishable active classes
with no-return but WITHOUT a global class order. One class means the proposed
multi-field channel is excluded on that panel. More classes mean capacity only:
report the finest forced partition and whether it actually provides multiple
blocks in retained groups. No claim that those classes are historical fields.
GDT1263's recurrent19core result and all full-panel exclusions remain unchanged.
GDT1264/65 alternation and1278/79 predictive results are different, statistical
questions; this is exact block capacity. No1320context model repair is attempted.

Inputs: unchanged1233 strict interior complete P-groups with unique22unit parse,
both separators DEFINITE_SPACE, current179selectors. Rejoin915source ID, raw form,
index, locus, edition and separators. No normalization, image, raw mixed TSV,
f1rbody, f84/f84r/f116v,327/336body or reserve access. Each reader separate.
FULL includes every row. SECOND predeclared diagnostic PHYSICAL_LEAVES_GE2 retains
whole unit tuples found on >=2 distinct physical leaf numbers, matching1263's
old robustness definition; it never replacesFULL. No TYPE_COUNT_GE2alternative.
All source material historically exposed; no independence or new admission.

Algorithm: start singleton classes. If positions i<j in any retained word already
belong to one class, every intervening unit must belong to that class, else it
would leave and return. Merge any required intervening class and iterate to a
fixed point. Record every strict merge with original source ID, endpoint positions
and intervening position. At most21strict merges. Every merge is forced under
EVERYvalid global partition by induction. At the fixed point each class occupies
one interval in every word, so the partition itself is feasible. Thus it is the
unique finest forced partition and its number of classes is the EXACT maximum.
Not every coarser partition is valid: merging A and C in ABC can create ABA.
No claim of a minimum needed class count; the trivial one-class model always fits.

Report all six panels, active classes, exact maximum, original group/type counts,
number of groups using >1class, and full source-bound merge certificates. No
significance, accuracy gate, dominant-class omission or favorable-reader selection.
If a class is rare this is not evidence of an informative human field system.
Primary union-find closure and independent Boolean equivalence-relation closure
must agree. Validator also replays each forced merge and confirms final contiguous
blocks; source-line traversal rechecks every1233row. Exhaustive tiny-alphabet
partitions validate the maximum and forced relation, including AB/BA separation
from1263, ABA collapse, iterative transitive collapse, and invalid coarsening.
Lock spec/code/input hashes before any native capacity calculation. Review is
formal structural capacity, not authorial semantic relation scoring or a new key.
