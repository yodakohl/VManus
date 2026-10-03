# Contextual expansion: available source packet

2026-10-03. Capacity review only; no model trained, prediction scored, experiment selected or target opened. Companion `CONTEXTUAL_EXPANSION_CAPACITY.json` retains every training candidate domain, fold counts, held-site-set hashes and three source hashes.

The source packet is GDT155's existing Nuremberg diplomatic lines and aligned editorial abbreviation expansions: 48,337 lines in 3,176 records. Every record has all expected line indices. There are 118,843 eligible observed sites whose entire whitespace group equals their marked site span and contains exactly one editorial `¤`. Case, long-s, Unicode characters and marker position are unchanged. Eligibility uses only blinded source fields; expanded length does not filter held sites.

`¤` is an editorial placeholder, not an inventory of the manuscript's actual abbreviation signs. These are ambiguities in the retained transcription representation, not independently verified native homographs. All labels have earlier project exposure; a future split is not fresh historical blindness.

A candidate marked type qualifies on the OTHER THREE books if at least two expansions each have >=5 training sites on >=3 distinct source pages. All training-attested expansions remain in its candidate domain, including rare ones. All held occurrences of qualified types remain; missing held answers are coverage errors, not exclusions.

| Held book | Train qualified types | Held sites | Held types | Held pages | Held records | Held answers outside train domain |
|---|---:|---:|---:|---:|---:|---:|
| Band2 | 103 | 3043 | 83 | 248 | 442 | 32 |
| Band3 | 92 | 4870 | 79 | 530 | 1000 | 22 |
| Band4 | 104 | 4763 | 95 | 284 | 516 | 21 |
| Band5 | 79 | 8836 | 75 | 603 | 1039 | 96 |

Before any model, the narrower training-defined contrast with two supported expansions differing only in final `m` versus `n` also has capacity: 15/14/15/14 training types and 851/1009/679/1494 held sites, respectively; 12/13/13/13 held types on 223/395/241/524 pages. The companion retains every qualifying type. This is not an assertion that every difference is grammatical case; all primary robust types must remain, and other candidate expansions must not be suppressed.

## Relevant predecessor boundary

GDT155's unblind calibration uses raw-site/group identity, character-neighbor backoff, stripped host, compiler signature and marker/position buckets. Inspection of `run_gdt155_unblind_calibration.py` confirms these are per-site lookup representations; surrounding written words are not a contextual inverse model. GDT157 learns forward character emissions and abbreviation propensity; GDT207 tests static diplomatic-language mapping. GDT158/159 audit comparative source supplies. No contextual neural inverse experiment was located by the bounded primary/source-reference search. This is not a claim to have proved absence throughout every archive.

GDT832's actual language model is a discounted word bigram with order-four character backoff; context has demonstrated control value, but its co-lemma factor adds none. GDT834's wrong function-word maps fail GDT835's writing rule; GDT837's wrong suffix maps fail GDT995's full inverse. Neither already-resolved error is a useful neural recovery target. Here multiple editorial expansions genuinely share the exact retained marked group, so input-spelling compatibility alone cannot select one.

## Smallest useful follow-up decision

Compare candidate ranking from the same train-only domains under (1) exact marked-form frequency plus declared style/position metadata, (2) a regularized non-neural local-context model, and (3) one fixed small contextual neural model. No pretrained weights or external text are needed for the capacity finding. Freeze model, context extent and tuning split before prediction; use only raw diplomatic context, never gold expanded neighbors. A same-input simple comparator is necessary: a neural win over frequency alone would not establish neural necessity. Remote-context ablation is needed before claiming long-range grammatical information.

Use held whole books, preserve physical-page boundaries, retain all wrong/OOV predictions, and score macro by marked type alongside token accuracy and complete-record ambiguous-site accuracy. The OOV truth class must be explicitly scored, not given an oracle candidate. Known original spellings and mixed writer labels remain intact. `writer_id` exists, including comma-delimited mixed assignments; do not interpret equal numeric IDs across books as the same historical scribe without provenance. Style metadata can supply a stated predictive control without that identity claim. Book/record IDs must not become answer lookup keys.

**Success changes model choice:** a model that improves genuine ambiguous expansion recovery over both frequency/style and local-context baselines becomes a calibrated candidate-ranking instrument for future finite reading lattices. **Failure changes model choice:** do not add that contextual architecture to the reading search. Neither outcome authorizes a Voynich decoder or establishes its writing channel. This is supervised source-channel calibration; it is not unsupervised Voynich lexical induction. The positive Voynich constraints (directed composition with whole-form residuals, fresh q/post-DY context transfer, known r/l phrase dependence) motivate preserving complete forms and written context, not importing these German expansion rules or meanings.

The earlier rough normalized census was exploratory and is superseded by this exact-marked, blind-eligibility packet. Its whole-group total was 118,842 only because it unnecessarily conditioned on single-word gold expansion; removing that condition gives 118,843. The robust held table above is unchanged. No prediction or model selection preceded this correction.
