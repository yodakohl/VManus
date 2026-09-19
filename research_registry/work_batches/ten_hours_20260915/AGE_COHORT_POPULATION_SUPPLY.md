# Age-cohort population accounts: bounded source supply

Date: 2026-09-15. One prospective raw proposal; no experimental selection.
Status: RAW_UNREVIEWED_NOT_SELECTED. No raw target data, target image or reserve was accessed.

The owned rabbit construction supports a content model in which an age-class distinction changes subsequent births. The proposed object is a complete population account with jointly interpreted cohorts, times, quantities and explanations. Its length and clause grouping may vary. There is no proposed fixed paragraph header, one-number-per-group format, copied twelve-month sequence, source-token count, or cipher alphabet.

## Ownership and complete source boundary

Fibonacci, *Liber abbaci*, composed 1202 and revised 1228; the owned witness here is Boncompagni's **1857 printed edition**, pp. 283–284, not a newly inspected medieval manuscript. [Public scanned edition](https://archive.org/download/bub_gb_CrdUBgtAZFoC/bub_gb_CrdUBgtAZFoC.pdf). PDF one-based pages 289–290 were rendered from the previously cached PDF and both complete pages were actually inspected with native vision in this task. The printed passage runs from `Quot paria coniculorum...` at the foot of p. 283 through `...infinitis numeris mensibus` near the top of p. 284. Its entire owned marginal table is included below. The preceding perfect-number problem and following four-men money problem are outside this boundary. The latter is not a second rabbit example.

PDF SHA256 `e0617041071d181ae61a5109fc21ad48b8503927ed9f8f2a1378575de797ed1a`; cached layout-text SHA256 `87f827c04d9c8fef4501d9f8dfa50b6947c682e01d5ad3487257c4c14a30d88a`. Native source render hashes: p. 283 `4e520e9d9832037226662c8ef569bebd25207f53c2f320cfaf834398c7a3b1b3`; p. 284 `4b44e3f6ba9d7b323fb9f5beecc426ac5c623022247b01360c3bd759968ea0f3`. No image pixels or private cache paths are included in this public dossier.

The following complete reading transcription normalizes whitespace, punctuation and evident OCR letter damage against the viewed print. It is not a diplomatic manuscript transcription. Numerals and operative assertions were checked against the source image. In particular the layout OCR's final p. 283 `2 f` is the printed **21**; no alternative numerical branch is chosen for a future code. The marginal heading reads `parium`, above initial 1; month labels then run Primus through Duodecimus. Latin case or letterform details in those labels are not used as semantic evidence.

```text
Quot paria coniculorum in uno anno ex uno pario germinentur.
Qvidam posuit unum par cuniculorum in quodam loco, qui erat undique pariete circundatus, ut sciret, quot ex eo paria germinarentur in uno anno: cum natura eorum sit per singulum mensem aliud par germinare; et in secundo mense ab eorum natiuitate germinant. Quia suprascriptum par in primo mense germinat, duplicabis ipsum, erunt paria duo in uno mense. Ex quibus unum, scilicet primum, in secundo mense geminat; et sic sunt in secundo mense paria 3; ex quibus in uno mense duo pregnantur; et geminantur in tercio mense paria 2 coniculorum; et sic sunt paria 5 in ipso mense; ex quibus in ipso pregnantur paria 3; et sunt in quarto mense paria 8; ex quibus paria 5 geminant alia paria 5: quibus additis cum parijs 8, faciunt paria 13 in quinto mense; ex quibus paria 5, que geminata fuerunt in ipso mense, non concipiunt in ipso mense, sed alia 8 paria pregnantur; et sic sunt in sexto mense paria 21;
[printed page break 283/284]
cum quibus additis parijs 13, que geminantur in septimo, erant in ipso paria 34; cum quibus additis parijs 21, que geminantur in octauo mense, erant in ipso paria 55; cum quibus additis parjis 34, que geminantur in nono mense, erunt in ipso paria 89; cum quibus additis rursum parijs 55, que geminantur in decimo, erunt in ipso paria 144; cum quibus additis rursum parijs 89, que geminantur in undecimo mense, erunt in ipso paria 233. Cum quibus etiam additis parijs 144, que geminantur in ultimo mense, erunt paria 377; et tot paria peperit suprascriptum par in prefato loco in capite unius anni. Potes enim uidere in hac margine, qualiter hoc operati fuimus, scilicet quod iunximus primum numerum cum secundo, uidelicet 1 cum 2; et secundum cum tercio; et tercium cum quarto; et quartum cum quinto, et sic deinceps, donec iunximus decimum cum undecimo, uidelicet 144 cum 233; et habuimus suprascriptorum cuniculorum summam, uidelicet 377; et sic posses facere per ordinem de infinitis numeris mensibus.
```

## Source-written claims versus modern state variables

The question gives one enclosed location, one initial pair, one year, one new pair per month, and reproduction in the second month from birth. It explicitly says that the initial pair reproduces in the first month. Thus its initial pair is already reproductive: the printed totals are initial **1**, then monthly **2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377**. Replacing them with an initially newborn `1, 1, 2, ...` convention changes the specified initial condition.

Source narration explicitly distinguishes the first/original pair in month 2; two pairs pregnant and two new pairs at the next delivery; month-3 total 5 and pregnant subset 3; month-4 total 8; five pairs producing five new pairs for month-5 total 13; and the five just-born pairs that do not conceive that month, while the other eight become pregnant. It then supplies the successive added births 13, 21, 34, 55, 89, 144 and corresponding totals through 377. These late additions are explicit written quantities, not values silently supplied by a simulator. The source gives total 21 at month 6, whose increment 8 is supported by the immediately preceding pregnant-eight clause.

The concluding explanation points to its own margin and prescribes adding consecutive earlier totals: explicitly 1+2 and 144+233, with the intermediate consecutive additions described generically. The first computed result is 3 and last is 377, also present in the narration/table. It says the ordered method can continue for indefinitely many months. This advice and the age-delay explanation belong to the complete source; they are not discarded as prose filler. There is one worked initial condition, not independent replications of every month.

Modern variables: M_t is the number of pairs eligible to conceive in month t for the next delivery; J_t is the newly born, excluded subset at that boundary. T_t=M_t+J_t. One source-compatible boundary convention has (M_0,J_0)=(1,0) and

`M_(t+1)=M_t+J_t; J_(t+1)=M_t; T_(t+1)=T_t+M_t.`

This models survival, maturation and delayed reproduction in the source's idealized calculation. Absence of death, migration and changing fertility is operationally assumed by its additions; these are not empirical biological claims or three separately printed laws. The M/J names and full cohort table are modern derived notation, not claimed historical written headers. The discrete boundary convention summarizes the printed conception/birth wording without claiming finer pregnancy timing.

| Month | Derived M | Derived J | Written total/table |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 1 |
| 1 | 1 | 1 | 2 |
| 2 | 2 | 1 | 3 |
| 3 | 3 | 2 | 5 |
| 4 | 5 | 3 | 8 |
| 5 | 8 | 5 | 13 |
| 6 | 13 | 8 | 21 |
| 7 | 21 | 13 | 34 |
| 8 | 34 | 21 | 55 |
| 9 | 55 | 34 | 89 |
| 10 | 89 | 55 | 144 |
| 11 | 144 | 89 | 233 |
| 12 | 233 | 144 | 377 |

## Distinct consequences and a complete generated example

1. The direct cohort path and the source's aggregate addition path agree: `T_(t+2)=T_(t+1)+T_t`. This is a consequence of one state transition, not a second independent data source or an automatic semantic-identification proof.
2. Immediate reproduction by every extant pair, with the same initial pair and monthly interval, predicts 1,2,4,8,... and contradicts the written month-2 total 3. The rival changes the age-delay meaning; it is not an arbitrary reversal of a copied numeral sequence.
3. At the source's month-3 boundary, `(M,J)=(3,2)` and total 5 predict next total 8. Swapping just these assignments to `(2,3)` preserves that total but predicts 7. The swap also violates the preceding source transition if retained as the same history; it is a deliberately false local state assignment, not another admissible history of the printed initial pair. This is the smallest state-versus-total consequence.
4. Every reached state has a unique preceding pair of compartments `(J,M-J)`. Nonnegative predecessor counts require M>=J after at least one closed-model step. Reverse-time readings or assigning a different entity to each occurrence cannot be freely absorbed while this same relation remains global.

A separately declared modern initial population of **3 eligible pairs and 1 newborn pair**, with the same subsequent rules and no new inputs, gives this complete four-transition account:

`(3,1;4) -> (4,3;7) -> (7,4;11) -> (11,7;18) -> (18,11;29)`

The notation is `(M,J;T)`. The aggregate route gives 4,7,11,18,29. Immediate reproduction would give 4,8,16,32,64. These are exact source-only integer calculations. The generated initial population is hypothetical, not another historical example; the account begins at that initialization and makes no claim about an earlier closed history. Arbitrarily choosing a fresh seed every step is forbidden.

Source-only checks computed all twelve transitions, all eleven aggregate recurrences and all inverse transitions; the complete generated account passes the same rules. These checks establish model arithmetic and the stated rival consequences only. No decoder, target scan or target writing-capacity check was built.

## Prior work, scope and remaining uncertainty

Live route and the genealogy context were read. Bounded searches/duplicate navigation used rabbit/population/cohort/maturation/Fibonacci terms; no returned card was assumed absent merely because one query was empty. Closest claim-bearing primary: [W97 report](../../proposals/translation_programs_20260912/work/W97/REPORT.md). All four fixed generation variants remain contradicted by participant self-reference under their original record-local identity and pointer rules. Same-generation equality did not establish siblings or marriage. This proposal does not reassign W97 words, reset identities per occurrence or reopen that failure: cohort counts are a different prospective content object, and no family-person names are inferred.

[GDT969 report](../../../experiments/yolo/gdt969_fibonacci_generated_root_trace/REPORT.md) was read directly: the fixed 23-group INPUT/HIGH writer failed before later arithmetic. Its content calculus succeeding on source simulations did not rescue the writer. GDT902 and GDT909 remain closed; this raw card changes neither their formats nor their decisions. Published target examples embedded in the W97/GDT969 reports were encountered only while checking those existing claims; no raw target material was queried. The live structural baseline permits ordered composition and space/higher-level effects, but does not license literal population prefixes, one field per word or a paragraph-to-month correspondence.

The proposed semantic restrictions are global age delay, cohort identity, one rate, one time direction and continued state across the whole account. A future joint reading may learn clause boundaries and semantic roles together, but must retain all meaningful declarations, actions, assertions and advice under one shared grammar with separately bounded syntactic alternatives. This raw card supplies no such finite writing grammar yet. It does not identify an admitted Voynich illustration or independent count owner as a population account. No next target experiment is selected.

Relabeling both cohort names together with their transition is a semantic gauge, not a rival contradiction. Counts of pairs versus individual animals differ by a global factor of two absent an independently bound unit. Scaling all counts preserves the homogeneous recurrence. A free second-order recurrence, unknown rate or arbitrary per-time reseeding would underbind meaning; none is established as a permissible escape. Calendar phase and initial maturity must be explicit before testing. The complete historical prose also says what is being counted and why: reproducing a numerical series alone would not translate that content.
