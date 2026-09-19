# Subset-account identifiability: source-only raw supply

Date: 2026-09-19. One bounded proposal; no selected experiment.
Status: RAW_UNREVIEWED_SOURCE_ONLY_NOT_SELECTED.

The complete owned source uses the **same four written totals with different participant groupings**, producing a unique solution in one case and a contradiction in the other. Its explicitly revised case is solvable but has a free choice. Thus the content can constrain both reference grouping and the difference between unique, impossible and underdetermined accounts. This is not another copied-number sequence, alloy renderer, population recurrence or Dioscorides projection.

## Complete owned source

Fibonacci, *Liber abbaci* (1202, revised 1228), in Boncompagni's 1857 printed edition, pp. 284–285. The inspected witness is this printed edition, not a newly inspected medieval manuscript. [Owned public PDF](https://archive.org/download/bub_gb_CrdUBgtAZFoC/bub_gb_CrdUBgtAZFoC.pdf), SHA256 `e0617041071d181ae61a5109fc21ad48b8503927ed9f8f2a1378575de797ed1a`. The PDF and layout text were already cached before this task. PDF pages 290–291 were both actually viewed with native vision. Their source-render hashes are `4b44e3f6ba9d7b323fb9f5beecc426ac5c623022247b01360c3bd759968ea0f3` and `529272e1748284dd9206934d644e305165fcc60f85b02888833c703040fe25e4`. No source pixels or private cache paths are published here.

The complete chosen block starts `Qvatuor homines sunt` on p. 284, includes the following `Item si propositum fuerit` alternative, crosses the page boundary, and ends `ergo quartus habet denarios 20` on p. 285. The next `Item sunt quinque homines` is a new problem outside this bounded block. Both four-man marginal result tables on p. 284 belong to the chosen content and are retained below. The preceding rabbit table is not part of this new example.

Every operative assertion, written number and action in the selected block:

1. Four men have fixed holdings within the first hypothetical case. Men 1+2+3 have 27 denarii; 2+3+4 have 31; 3+4+1 have 34; 4+1+2 have 37. Ask how much each has.
2. Add these four totals, obtaining **129**. The explanation says each man is counted three times, hence this is three times their total. Divide by **3**, obtaining **43**.
3. Subtract the first triple's **27** from **43** to obtain man 4's **16**; subtract **31** for man 1's **12**; subtract **34** for man 2's **9**; subtract **37** for man 3's **6**.
4. Recombine **12+9+6+16=43** as an explicit check. The owned marginal table gives Primus 12, Secundus 9, Tercius 6, Quartus 16. The incidence equations' simultaneous verification is a modern additional check; the source explicitly recombines the final total.
5. A new hypothetical case assigns **27** to men 1+2, **31** to 2+3, **34** to 3+4, and **37** to 4+1. It explicitly says such positions are sometimes soluble and sometimes not, and proposes a criterion to distinguish them.
6. Add the totals for 1+2 and 3+4, and compare with the totals for 2+3 and 4+1. The source asserts equality means soluble and inequality means insoluble. Here **27+34=61**, whereas **31+37=68**. Both purport to count the same four men; the source states impossibility and concludes this case is insoluble.
7. To propose a soluble case, the source itself changes the 4+1 amount to **30**, retaining the other amounts in order. Now the two covering paths both give **61**. This is an explicitly announced new hypothetical case, not a silent repair of a failing equation or license to alter a future target value.
8. On p. 285 the source says the first man may have an amount chosen at will from the **27** held with the second. It chooses **10**, giving second **17**. Subtract **17** from **31** to obtain third **14**; subtract **14** from **34** to obtain fourth **20**. The second owned table gives Primus 10, Secundus 17, Tercius 14, Quartus 20. The closing edge **20+10=30** is a calculated verification; the prose stops at fourth 20, without spelling out that addition.

These are complete semantic inventories of the selected paragraphs, including problem statements, justification, counterexample, changed case, free-choice advice and checks. They are not represented as a diplomatic Latin transcription. Native collation corrects layout OCR that reads 129 as `li»`, 16 as `10`, 6 as `0`, and the page-285 starting 27 as `17`. The printed images, prose and two owned tables agree on the numerical inventory above. The edition's marginal manuscript line references are provenance apparatus, not additional mathematical statements.

## Shared semantics and genuinely different consequences

Let x_i be a fixed nonnegative integer holding of participant i **within a case**. A stated subset amount is the sum of exactly those participants' holdings. A new explicitly hypothetical case may change the holdings; repeated names inside one case do not silently introduce fresh people or amounts. Exact denarii are used for this modern semantic model; the source gives integer examples without providing a general modern domain declaration.

For the triple case, each participant occurs three times: T=(27+31+34+37)/3=43. Each x_i=T minus the total of the other three, uniquely giving (12,9,6,16). For the adjacent-pair case, the two complementary covers must agree:

`(x1+x2)+(x3+x4)=(x2+x3)+(x4+x1)`.

The original numbers violate this unavoidable equality by 7. No choices of holdings, including negative or fractional ones, solve that case under fixed identity. This is an actual semantic constraint, not a legal-program or freely satisfiable directed-graph fit.

After the source's explicit 37-to-30 change, the entire solution family is

`(x1,x2,x3,x4)=(t,27-t,4+t,30-t)`.

Nonnegative integer holdings allow t=0,...,27; strictly positive ones allow t=1,...,26. The source chooses t=10, but its equations do not identify 10. The continuous affine family is a modern derivation, while choosing the first amount at will is explicitly historical. In a general arbitrary cyclic problem the covering equality by itself is an algebraic consistency criterion; nonnegative or positive feasibility can impose additional bounds. This card does not universalize the printed criterion beyond its actual positive example.

**Rival consequence:** keeping all four written amounts 27,31,34,37 but reading the participant phrases as triples yields one solution; reading them as adjacent pairs yields no solution. The quantities alone cannot choose the meaning. Conversely, interpreting the corrected pair problem as uniquely determined contradicts the source's free-choice instruction and the surviving family. A future reading must bind the participant grouping and status language globally; it cannot call each numerical contradiction a negative example after seeing it.

A negative example is legitimately part of this complete historical argument. Therefore a future content model must express an asserted impossibility as well as a solution and an explicitly announced changed case. It must not require every embedded equation set to be soluble, nor introduce an unmarked case reset to rescue one. The syntactic realization of those distinctions is **not yet supplied**.

## Complete generated account and source-only verification

A separately declared modern example has holdings (4,7,9,12). Its triple totals in the same participant order are (20,28,25,23): sum 96, divide by 3 gives total 32, and complement subtraction recovers (4,7,9,12). Its adjacent-pair totals are (11,16,21,16), whose complementary covers both give 32; the pair data alone instead permit `(t,11-t,5+t,16-t)`, with integer 0<=t<=11. The chosen holdings correspond to t=4, not a uniquely inferred result. Changing only the last pair total to 17 creates covers 32 versus 33 and makes that modified case impossible. This generated example and its status claims are modern, not additional historical evidence.

Exact integer checks verify the historical triple solution, all 28 nonnegative historical pair solutions, the two contradictory cover totals, both printed answer tables, and the complete generated account. No target parser, decoder, target enumeration or new source acquisition was built.

## Novelty boundary and retained failures

The live route and `context topic numbers` were read first. Bounded duplicate/route searches for overlapping sums, simultaneous equations, subset sums and four men were navigation only; noisy or empty searches are not proof of absence. [IDEA354's source proposal](../../proposals/raw_global_simultaneous_grouping.json) was read in full. It concerns one unknown collection under modular grouping, with a residue-class ambiguity. This proposal concerns multiple persisting participants, different subset incidences, and source-owned transitions between unique, impossible and non-unique problems using the same amount list. Both share arithmetic consistency; no wholly novel research family is claimed.

[W94's primary report](../../proposals/translation_programs_20260912/work/W94/REPORT.md) was read in full. It already obtains nontrivial equalities from global identity assumptions, while its fixed extension to three distinct ratio values fails. Its A=B=C=1 consequence depends on unchanged-mass identity; separating mentions changes what follows. Those stops remain. This card assigns none of its old material/value words and does not reuse its last-mentioned-material rule. W96's local branch remains parked; GDT969 and the alloy writers remain closed. Route-search hits concerning overlapping digram or literal Sator string equations do not establish that those encoding models test numerical subset ownership.

The live structural facts—hierarchy at spaces, ordered reusable composition, whole-form residuals and entry/position effects—remain constraints on a future joint grammar, not translations of these source concepts. No known word is required to propose joint recovery, but this card still lacks a finite shared writing grammar and an independently owned target account. No source participant count, numeric field count, paragraph header or source order is imposed on the manuscript. No selection or target test is proposed here.

Permuting all participant names together is a gauge. Reordering equivalent assertion clauses does not change their equations. Changing units rescales holdings and totals. Arithmetic consistency alone does not identify men, coins or the meaning of the full explanatory prose. Allowing fresh participants per occurrence or assigning numerical content freely per word would erase the intended constraint and is excluded from this prospective content model.

Access: only existing external source caches and navigation/claim-bearing predecessor documents. W94 contains already published target examples, encountered in the required primary audit; no raw target data, target image, new admission, reserve or external contact was used. Previous source/proposal bytes and root metadata remain unchanged.
