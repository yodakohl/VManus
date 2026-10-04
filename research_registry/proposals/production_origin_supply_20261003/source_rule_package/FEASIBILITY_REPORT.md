# Source recovery is possible only within a restrictive reference ceiling

4 October 2026. **The audited closed-vocabulary design does not justify a
larger context model now.** It has some legitimate novel-form recovery
capacity, but its exact-answer ceiling is55.906% by occurrence and32.602%
with equal written-type weights. Frequency alone already achieves49.580%
and27.784%, respectively. These are historical-source diagnostics with
supplied sign values, not a Voynich decipherment result or a fitted contextual
experiment. The source rules are useful; their compatibility is not recovery.

The protocol was written before the census. It fixes all six whole-book
reference splits and retains the11,724 selected source groups. There are
5,359 occurrences of2,558 known written types absent from the other five
books,6,161 occurrences of shared types, and204 unknown-written obligations.
The latter remain separately visible because they cannot honestly be called
known lexical types. The complete panel includes them with zero credit.
“Novel” means an unseen exact written form, not an unknown language, unseen
concept, or necessarily an unseen expanded word. All data had prior exposure.

## What the unknown written forms permit

| Quantity | Occurrences /5,359 | Interpretation |
| --- | ---: | --- |
| Exact answer expressible by the supplied rules |5,356 (99.944%)|Rule compatibility only; the three retained mismatches remain.|
| Exact answer also in other-book reference words |2,996 (55.906%)|Maximum possible exact recovery for this closed-vocabulary design, even with a perfect chooser.|
| Fixed reference-frequency choice correct |2,657 (49.580%)|No sentence context or fitted model.|
| Maximum remaining improvement |339 (6.326 percentage points)|Oracle headroom, not an expected context gain.|
| Correct reference answer with at least one rival |1,687|Some actual room for context-dependent selection remains.|
| No compatible reference candidate at all |2,020|Empty domains remain errors; no vocabulary repair.|
| Exactly one compatible reference candidate |1,589|Singletons need no contextual choice; they are not all correct.|

There are2,363 occurrences whose exact answers are absent from the reference;
this includes all three locally incompatible answers. The strong supplied-rule
coverage therefore does not remove the reference bottleneck. The all-panel
intersection is9,145/11,724; its higher rate mostly benefits from shared forms
and must not replace the novel-form task.

The problem is sharper when frequent forms cannot dominate. For2,558 novel
written types, first average over occurrences of each type, then over types:
the ceiling is32.602%, frequency achieves27.784%, and maximum headroom is
4.818 points. Averaging the six book-specific type means equally gives32.046%
versus25.992%. These different weightings are reported rather than selected.
Unknown-written obligations remain in the full occurrence accounting, not
silently assigned artificial type identities.

| Held book | Novel occurrences | Novel types | Exact-answer ceiling | Frequency correct | Maximum extra correct |
| --- | ---: | ---: | ---: | ---: | ---: |
| B4 |469|299|196|168|28|
| B6 |48|42|11|3|8|
| Br1 |105|81|51|37|14|
| Bs1 |1,144|491|723|673|50|
| Gr1 |2,372|1,086|1,359|1,248|111|
| W1 |1,221|559|656|528|128|

## Does the retained reference context distinguish alternatives?

The fixed diagnostic uses only adjacent raw written groups in the held book.
Their full legal reference-supported domains are intersected with ordered
expanded bigrams in the other books; held expanded neighbors are never given.
Support may come from either side, never across record boundaries. This is
presence/absence support, not a fitted or frequency-normalized language model.

Among novel occurrences,1,175 have unequal candidate support. Only the correct
candidate has any such support in763 cases; a wrong candidate alone has
support in126. Most of the763 were already solved by reference frequency:
only25 repair a frequency error, spanning18 written types and22 source leaves.
Thus there are real supported alternatives, but not evidence of a general
contextual selector superior to the baseline.

A **post-census descriptive cross-tab**, not a registered ranker result, finds
26 frequency-correct cases in which a wrong candidate alone has support.
Blindly overriding frequency whenever sole support exists would therefore
repair25 and spoil26 on this exposed panel. This does not refute richer
context, longer windows or language models; none was trained or compared.
Sparse context evidence and differing reference frequencies can both explain
why simple support is unreliable. No window or scoring repair was attempted.

## Decision and limits

The experiment can succeed on some words. The claim that a broad exact
reconstruction is now within reach is not supported by this data supply.
Do not launch the proposed larger closed-vocabulary context fit or an
unknown-key/Voynich stage from these counts. No prospective accuracy gate was
run or failed here; this is a design decision from measured capacity.

A changed proposal would need a fixed, independently justified mechanism for
reference-absent historical spellings, or an explicitly narrow research
decision worth the limited remaining contextual headroom. Merely adding the
observed missing answers, excluding OOV cases, normalizing after inspection,
or tuning a scorer until the25 favorable examples win is not that mechanism.
No automatic source acquisition or implementation follows. This does not
prove that every open-vocabulary approach would fail, and does not repair
GDT1164/1166. GDT1160's supervised positive remains intact.

Assumptions retained: known source language/alphabet and declaration values;
editorial graphic classes and word/record boundaries; exact editorial
restorations as reference; related books with possible shared recipes;
previously exposed data. The partition withholds complete books and their
expansion pairs from each reference, but is not independent historical or
analyst-blind confirmation. None of these counts identifies a Voynich word,
writing mechanism or language. Confirmed Voynich meanings remain0.

The independent bounded idea review used only predecessors, not this census.
It supplied no new candidate or independent performance estimate. It retained
the distinction between unseen writing and unseen plaintext, intersection
coverage and singletons. Existing raw supply was sufficient; no duplicate
proposal was added merely to enlarge the queue.

## Reproduction and accounting

Run `python research_registry/proposals/production_origin_supply_20261003/source_rule_package/feasibility.py`
and then `python research_registry/proposals/production_origin_supply_20261003/source_rule_package/validate_feasibility.py`.
Both use only the original pinned source files. The census imports the
unchanged source projector; its selected rows exactly match the frozen package.
The validator independently scans reference vocabularies with anchored regexes
instead of the census trie and checks7,408 distinct focus/neighbor domains,
all11,724 rows, all supports, complete-panel conservation and summary arithmetic.
It replays the same XML projector, not an independent native-image collation.

`FEASIBILITY_PROTOCOL.md` is the prior contract; `FEASIBILITY_RESULT.json`
contains hashes and all book/partition summaries. The three compressed files
retain reference vocabularies/bigrams, full candidate domains and every source
occurrence with raw neighbors and provenance. `FEASIBILITY_VALIDATION.json`
binds the validation and separately marks the post-census cross-tab. CoReMA,
University of Graz, CC BY4.0; original URLs and credits remain in SUMMARY.json
and the pinned source XML. No Voynich or reserved data were accessed.

Publication accounting: the live context and local/public metadata checks pass.
The repository-wide preflight still reports pre-existing route-literal,
historical manifest/hash, cached-artifact/layout and stale-index issues outside
this source task. It is not a global PASS. Publication uses an explicit14-file
staged scope, source-artifact hash checks and decompressed privacy scanning;
unrelated local changes and all legacy source bytes are preserved.
