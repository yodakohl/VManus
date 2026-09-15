# GDT965 — no joint reading on the literal panel; wider scope unknown

All 1,071 source/page consequences were published in registration commit
adbd863e5 before filtering. The unchanged GDT900 exact string enumerator was
then run on every case surviving the necessary conditions. Independent
validation passes all 14 checks, including source collation, all 357 rebuilt
frames, all predictions, contradiction certificates, and exhaustive replay of
the sole exact UNSAT result. No code or translated word was found.

## Complete candidate results

The full [candidate/prediction table](artifacts/CANDIDATE_TABLE.tsv) gives every
source/page case, observations, contradictions, unresolved scope and zero
independent confirmation capacity. The [registered predictions](artifacts/PREDICTIONS.tsv)
and [machine-readable cases](artifacts/ALL_CASES.json) preserve the exact details.
No page was selected for favorable fit.

| Edition / complete source | Necessary contradiction | Exact UNSAT | Computation unknown | Source unknown |
|---|---:|---:|---:|---:|
| ZL3b / peach | 0 | 0 | 0 | 119 |
| ZL3b / pomegranate | 0 | 0 | 0 | 119 |
| ZL3b / quince | 0 | 0 | 0 | 119 |
| IT2a / peach | 98 | 1 | 2 | 18 |
| IT2a / pomegranate | 101 | 0 | 0 | 18 |
| IT2a / quince | 101 | 0 | 0 | 18 |
| RF1b / peach | 2 | 0 | 0 | 117 |
| RF1b / pomegranate | 2 | 0 | 0 | 117 |
| RF1b / quince | 2 | 0 | 0 | 117 |
| Total | 306 | 1 | 2 | 762 |

The sources have 285/464/326 clusters. All start with aleph, which occurs
51/88/61 times respectively. Under the fixed nonempty common code, the first
target character must occur at least that often. This necessary consequence
fails in 301 cases. Other overlapping contradiction certificates are insufficient
length (100), final-unit recurrence (208), and equal initial/final code for
quince (103). These counts overlap; they are not independent discoveries.

Three IT2a peach cases survive the necessary filters:

| Page | Characters | Initial character / count (required 51) | Final character / count (required 35) | Exact search |
|---|---:|---|---|---|
| f30r | 487 | o / 59 | y / 41 | UNKNOWN after 2 s |
| f35r | 456 | c / 51 | n / 39 | Exhaustive UNSAT, independently replayed |
| f66v | 588 | o / 63 | y / 57 | UNKNOWN after 2 s |

These two unknown peach cases do not supply a three-record reading: every
literal pomegranate and quince candidate is already contradicted. No joint
solver run or longer local search is necessary to decide that literal panel.

## Scope and ambiguity

The joint status UNSAT_LITERAL_DOMAIN means no assignment exists within the
fully literal page domain. ZL3b has **zero** such pages, so its status expresses
missing capacity, not substantive evidence against the model. IT2a has 101
literal and 18 source-unknown frames; RF1b has 2 literal and 117 source-unknown
frames. Source unknown means uncertainty in the target transcription or seams,
not an unknown meaning of the historical source. All 762 cases stay unresolved.
Thus **no whole-scope exclusion** follows in any edition.

The [309 observation groups](artifacts/EQUIVALENT_OBSERVATIONS.json) group equal
measured consequences, not equal full codes or equal meanings. Unknown cases
cannot be distinguished by this test. No code witness exists whose arbitrary
units could be assigned a confirmed phonetic value. The two computation unknowns
are not compatible readings established by a successful search.

## Assumptions and exposure

The [fixed method](METHOD.md), [decision](src/DECISION.md),
[source audit](src/SOURCE_AUDIT.md), and [preregistration](PREREGISTRATION.md)
retain the complete source bounds, exact edition-level clusters including dots
and final forms, one prefix-free injective common code, original order, and
three different physical leaves. No source word had to equal an EVA group.
The printed cluster inventory is not a proven historical cipher alphabet.
The source is catalogued broadly after the tenth century; a pre-1420 date is
not established. This tests exact copying through the registered channel, not
all Arabic composition, paraphrase, morphology or multilingual writing.

The source was collated and directly viewed before fitting; target pages and
structural profiles were previously exposed in the project. Initial-entry
recurrence conflict was anticipated and disclosed before the run. Three source
records belong to one physical fragment, and alternate Voynich transcriptions
are not independent witnesses. Selection and additional confirmation cannot be
separated here: independent confirmation capacity is zero. No reserve was
opened; f84/f84r remain sealed. No search-wide control or independent meaning
check exists, so there is no significance or confirmed plant-name claim.

## Decision

Park this exact complete-record/common-code route. It has no joint reading in
the usable literal panel, while the wider transcription-uncertain scope remains
unknown. Do not repair it by stripping dots or entry glyphs, deleting titles,
changing boundaries, selecting synonyms, or extending solver time. A materially
different model needs a separate decision and registration; broader Semitic
language hypotheses remain untested. GDT193/194/893/900/915/963 are unchanged.

The 08:40 UTC inclusive checkpoint was exceeded by closure and publication;
source selection, code and search limits were not expanded. The user/tool
interruption before 08:16 is not counted as active computation.
