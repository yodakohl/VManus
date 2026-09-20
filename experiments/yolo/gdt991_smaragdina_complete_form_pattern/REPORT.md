# GDT991: complete pattern search stopped, no complete reading

The registered whole root/argument-slot pattern adds **108 separately corroborated contradictions**. Of the 1,980 previously unresolved full equations, **1,872 (94.545%) remain unresolved**. No whole-pattern witness or original full code was found. The fixed 90% stop applies: no third algorithm, automatic longer search, source repair or frame repair is selected. This is not a rejection of every possible Tabula-related text or of process content generally.

## Complete candidate accounting

The [candidate table](artifacts/CANDIDATES.tsv) retains all 32,376 original candidates. Each row identifies reading, whole paragraph, physical leaf, source branch, writer, original and observed status, source form count, target group count and independent meaning capacity. [Full cases](artifacts/CASES.json.gz) add necessary conditions and individual primary/reverse receipts. The [24-model table](artifacts/MODEL_SUMMARY.tsv) aggregates without selecting a page.

| Final status | Cases | Interpretation |
|---|---:|---|
| Source unknown | 19,080 | Original ineligible transcription lines retained |
| Nonempty length contradiction | 7,524 | Inherited GDT990 necessary exclusion |
| Distinct-root length contradiction | 3,696 | Inherited GDT990 necessary exclusion |
| Word boundary contradiction | 96 | Inherited GDT990 necessary exclusion |
| Complete form-pattern contradiction | 108 | Exhausted in both matching directions |
| Primary exhaustion uncorroborated | 1,299 | Primary exhausted; reverse check reached its limit |
| Primary pattern limit | 573 | Primary search reached its limit |

The primary implementation reported 1,407 exhausted patterns and 573 limits. The separately constructed reverse implementation exhausted 108 of those 1,407 and reached its external limit on 1,299. No reverse witness conflicted with a primary negative. The 1,299 uncorroborated cases remain open in the reported original-equation decision; they are not promoted to checked exclusions. There are zero saved positives, so no target pattern entered frame factorization.

All 24 full source/writer equality signatures differ, as preregistered in [source predictions](artifacts/SOURCE_PREDICTIONS.json). They are formally distinguishable by this test in principle, not identified in practice. THELESM as secret versus treasure, and other semantic renamings preserving the same equality pattern, remain indistinguishable. Unknown cases supply no ranking among those meanings or among the six source branches and four writers.

## Concrete inherited consequence for the motivating paragraph

IT2a f75v.38–42 contains 59 groups and 259 characters over 15 characters. All 24 complete-source candidates already fail GDT990's distinct-root minimum length: the 192-form branches require at least 305 characters, and the 193-form branches at least 307. The corresponding ZL3b rows remain source-unknown, with uncertain lines .39–.42. This illustration was selected after the full panel for reporting; it contributed no new selection or GDT991 exclusion. It excludes this entire Tabula writing on this IT paragraph, not the earlier conditional process rivals.

## Validation, exposure and reproducibility

Public preregistration commit `b74970689` preceded target matching at 2026-09-20 05:48:03.974507 UTC. All 1,980 primary jobs completed in 201.741 seconds. All 1,407 requested reverse jobs were retained; validation completed at 06:01:29.171848 UTC, before the shared 06:03:03.974507 deadline. Per-case outcomes were flushed to journals as they arrived. GDT990's original interrupted execution, source, writing contract and public lock remain unchanged.

The [validator](artifacts/VALIDATION.json) passes case/source reconstruction, receipt coverage and separate bounded reverse checks. It is a second implementation by the same author, not an independent human replication or meaning test. The post-result [reporting audit](artifacts/REPORTING_AUDIT.json) reconciles every table row and journal outcome without another search. The 5,100 exhaustive small controls and 24 complete-source control pairs were fixed before target access; their initial source-only matcher correction is disclosed in PRE_RUN_DEVELOPMENT.md. A validation PASS does not turn a limit into a proof.

All targets were previously exposed. ZL3b and IT2a remain alternate readings of one manuscript; the 108 new contradictions cover 18 physical leaves, not 18 independent semantic confirmations. Eligibility is unchanged: 31 ZL3b and 523 IT2a complete paragraphs, with 795 other paragraph readings ineligible. No new page, reserve, f84/f84r or outside reviewer was used. Independent meaning confirmation capacity is zero for every candidate; confirmed translated words remain zero. No significance or code-uniqueness claim is made.

Reproduction follows METHOD.md and the frozen scripts. Existing journals can be assembled with `src/run.py --assemble` and `src/validate.py --assemble`; fresh timed searches may produce different unknown counts on another machine. Exhaustion receipts and explicit limits must remain distinct.
