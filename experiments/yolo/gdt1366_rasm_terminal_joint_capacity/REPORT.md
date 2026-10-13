# GDT1366 — Recurrent words contradict the restricted mixed-direction rasm renderer

**RESTRICTED_RASM_JOINT_GE2_EXCLUDED.** The previously capacity-only restricted18
mixed-direction panel also fails a stronger necessary joint rule. This failure
occurs in common forms on54physical leaves in each reading, not only rare forms.
The18-class fixed RAW_CHAR renderer with preserved source boundaries is excluded
on the recurrent subset even if each source word can be reversed independently
and split further. This does not reject Arabic or consonantal writing generally.

| Reader | GE2 groups / types | Violating groups | Share | Violating types | Leaves with violations / all |
|---|---:|---:|---:|---:|---:|
| IT2a |19687 /1466|714|3.627%|31|54 /90|
| RF1b |16786 /1315|692|4.122%|28|54 /90|
| ZL3b |16865 /1337|709|4.204%|31|54 /90|

Readers are alternate transcriptions of one manuscript, not three independent
replications. GE2 means exact wholeforms on at least two physical leaves; these
are already exposed data, not a holdout. Rates describe violations under the
fixed inferred set, not minimum edits or a statistically estimated error rate.

## Why the contradiction does not depend on a guessed key

The pinned restricted rasm channel has18classes:15usable internally and3only at
source-word end. A fixed function emitting one raw character per class can
produce18different observed characters only by being bijective. Merging any two
classes would leave at most17distinct output characters.

Every GE2 reading uses18characters; exactly15also occur strictly inside groups.
Consequently the remaining three characters, m/n/q, must be the images AS A SET
of the3terminal-only classes. No individual source-letter assignment is made.
A source word can contain at most one occurrence from those three classes.
Reversal preserves the count and cutting words into smaller groups cannot
increase it. Every observed group must therefore have at most one occurrence
from {m,n,q}. Counting only distinct members would be insufficient; repeated
occurrences of the same candidate would also violate the rule.

The full census contradicts that implication. Candidate-only strings are:
IT qn705/qm9; RF qn686/qm6; ZL qn701/qm8. No other violating pattern occurs in
these fixed panels. For example, qokain occurs240/234/237times and qokaiin
219/213/220times in IT/RF/ZL respectively. Each contains q at the beginning and
n at the end. Those are literal transcription examples, not translations or
newly image-confirmed spellings. Every violating occurrence, complete cached
source row and raw offset is preserved in RESULT.json.

## What changes and what does not

GDT1365's restricted18 mixed-direction GE2 diversity result remains correctly
CAPACITY_ONLY for that weaker condition. GDT1366 adds a different joint-word
condition and rejects the survivor. It neither reruns nor reopens the original
FULL failure. The registry's SAME_MODEL_NOT_REOPENED response is retained in
the protocol; this is additional exclusion, not approval to repair the model.

The extended software20-class GE2 model does NOT inherit this proof:20classes
can map to18characters without a bijection. Its previous capacity-only result
remains. The full20 FULL failure stays rare-sensitive as reported in1365.
Actual glyph units, variable-width rendering, contextual allographs and removed
source boundaries are outside the present contract. They are not supported
repairs simply because this test does not cover them. No new source corpus,
decoder, sound value or word meaning is selected. Confirmed lexemes remain0.

For the unchanged restricted18 renderer, stop key fitting on both FULL and GE2.
Reconsideration requires independently justified new rendering/boundary evidence
and a distinct prospective test; changing the key or word direction cannot help.
Do not infer a ban on historical dotless scripts from a modern technical channel.

## Validation and provenance

The protocol openly follows exposed1365 results, and familiar q-initial/n-final
forms already made a contradiction plausible. It is a deductive model check,
not a blind discovery. Both programs, proof review, fixed cache/allowlist and
1365source/method/result were hash-locked before the new joint census.

An independent reviewer checked the bijection, set identity, multiplicity and
substring argument before counting. The separately authored validator was frozen
before reading the primary program or results. It independently rebuilds GE2,
all sets, denominators, summaries and every source/offset witness. Its source-free
controls include96split/reversal cases, repeat multiplicity and singleton cases.
Validation status is recorded separately in VALIDATION.json; report comparison
is in RESULT_REVIEW.json. Neither establishes historical source use or semantics.

Only the unchanged1233JSON cache and631allowlist are used. No new raw TSV,
images, source text, reserve, f84/f84r, f116v or f1rbody is accessed. No new web
search or source-code acquisition was needed;1365's pinned source rule is bound.
