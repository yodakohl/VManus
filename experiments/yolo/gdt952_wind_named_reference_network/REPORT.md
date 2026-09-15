# GDT952: no observed wind-name reference supports the fixed register

The complete comparison yields **zero definite off-diagonal title recurrences in all six cases**. After the explicitly documented separator-enum correction, IT2a contradicts both fixed models even when every uncertain edge is allowed. ZL3b/RF1b retain only unresolved possibilities. None supplies a supported wind-name assignment or a translated word.

The original registered implementation made a table-enum error and treated definite spaces as uncertain. Its original outputs remain under artifacts/, labelled here **INVALID_TEST**, not manuscript evidence. The corrected diagnostic under artifacts/corrected/ changes only that enum and the output destination; it is post-exposure. See CORRECTION.md. The public preregistration was849f66d69; its locked files and predictions remain unchanged.

## Complete candidate table

Each row considers all479001600bijections of the12source winds onto the12fixed physical title/body sectors. Counts are exact for the lower and upper graphs; positive upper counts are generous possibilities under independently allowed missing readings, not completed readings.

| Reading | Frozen representation | Supported assignments | Possible assignments, upper bound | Decision |
|---|---|---:|---:|---|
| ZL3b | Whole literal title | 0 | 22,560 | Unresolved only |
| ZL3b | Whole cached root sequence | 0 | 1,497,600 | Unresolved only |
| IT2a | Whole literal title | 0 | 0 | Contradicted |
| IT2a | Whole cached root sequence | 0 | 0 | Contradicted |
| RF1b | Whole literal title | 0 | 8,328,000 | Unresolved only |
| RF1b | Whole cached root sequence | 0 | 158,376,960 | Unresolved only |

Definite titles:10/12ZL,11/12IT,8/12RF. Of132off-diagonal cells percase, the unknown counts are respectively43,67,13,41,79,116in table order. Unknown does not mean observed. The three editions are alternative readings of one manuscript, not independent replications.

## Predictions and contradictions

The source requires Vulturnus→Subsolanus, Eurus→Subsolanus, Euroauster→Auster, Euroauster→Eurus, Euronothus→Auster, Affricus→Zephirus, Chorus→Zephirus and Circius→Septentrio. For every candidate bijection, each destination's complete title representation must occur in the source wind's entire assigned body. Seven references are spatial; Euroauster→Eurus is an explicit etymological name mention. The ambiguous ninthCircius reference is excluded prospectively. Favonius/Zephirus identity and stable case-independent concept rendering are declared assumptions, not discovered linguistic facts.

The IT contradiction has a small checkable witness. Subsolanus,Auster,Zephirus must each receive two references from six different other wind entries. Enumerating all220choices of three target centers, literal IT can realize at most3of these6distinct-body obligations, and cached-root IT at most5. This fails before the other two source edges are even required. IT_CONTRADICTION_CERTIFICATE.json retains all220center choices permodel.

Example of what was actually compared: the entire ZLtitle atf67r2.1 is `ykshy s aram`, with cached roots `H s ar`; its owned complete body is .13–.15. Title.12owns the08:30body.48–.51. Partial `s`, `ar`, `H` or another convenient fragment does not satisfy the whole-title prediction. Every title and every belongingQ1/M1line appears in COMPLETE_RECORDS.tsv. The lack of whole-title recurrences agrees with the older warning against treating outer titles as lexical body summaries; it does not create a new general discovery about word morphology.

## Remaining ambiguity and capacity

The eight-edge source graph already cannot distinguish Affricus from Chorus: each only points to Zephirus. The test also ignores physical compass orientation, source aliases beyond the fixed concept collapse, and weather attributes. In ZL/RF, additional ambiguity is caused by unread or unaligned forms. ALL_NAME_CANDIDATES.tsv gives every one of the864reading/model/name/sector possibilities with supported and upper assignment counts. All lower counts are0. No upper-only candidate may be promoted to a name merely because it survives an unknown cell.

There is one previously exposed physicalleaf and **zero independent confirmation leaves**. No new reserve or image was opened. All51loci were selected prospectively through the guarded query. Full title/body matching is a conditional rendering hypothesis; a case-inflected, abbreviated or differently organized wind text would be another model. The broad wind genre is not refuted. The present fixed register receives no positive evidence and will not be extended by selecting smaller fragments or repairing a decoder.

The result is an exact consistency diagnostic, with no suitable countercontrol of the complete historical/model search and therefore no significance claim. No independent meaning test has confirmed a wind, plant or other word. GDT888's non-uniqueness and GDT913's18lexicon result remain unchanged.

Reproduce: run src/prepare.py, src/run.py for the preserved original error, src/run_corrected.py for the diagnostic, src/star_certificate.py and src/validate.py. SOURCE.json supplies the complete symbolic prediction table; ALL_TITLE_BODY_CONSEQUENCES.tsv supplies all864observed cells, without selected examples determining the outcome.
