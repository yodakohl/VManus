# A finite grammar for complete weighted-mixture accounts

2026-09-15, source-only design, 13:40–14:00 UTC. This card defines a finite semantic language and a separate, deliberately narrow hypothetical writing rule R0. Neither is a discovered Voynich parser. No target paragraph, length histogram, new image, code fit or digit-permutation search was accessed. Existing source renders were inspected; the earlier review and source-supply bytes remain unchanged. Root's separate source-only GDT971 control is not implemented here.

**What is now concrete.** [ALLOY_FINITE_GRAMMAR.json](ALLOY_FINITE_GRAMMAR.json) contains complete accounts for both source-derived total-20 methods, a new `(4,4,12)` method, and an account presenting all three as alternatives. The [small semantic verifier](alloy_finite_grammar.py) evaluates every recipe and reference exactly. It also generates a reviewable full token stream with every argument present. This is a variable account language, not a fixed number of calculation steps or a list of copied source sentences.

## Source ownership and the separate equation inventory

I independently viewed the producer's existing full renders of printed pp152–154 between 13:42:27 and 13:45:06 UTC. The subsection begins at the bottom of p152 and ends on p154 before *De consolamine trium monetarum cum minutiis*. The PDF SHA-256 is `e0617041071d181ae61a5109fc21ad48b8503927ed9f8f2a1378575de797ed1a`. These were cached source images, not newly acquired or Voynich images.

[ALLOY_SOURCE_EQUATIONS.json](ALLOY_SOURCE_EQUATIONS.json) contains 50 exact rational constraints from the whole worked subsection: 17 printed actions, 1 printed grade computation, 12 printed account relations, 6 common-grade consequences, 6 explicitly qualified normalizations, and 8 actions containing lexical number words. Each has a page, local source description and qualification. This is an equation/claim inventory, **not a diplomatic occurrence ledger**: a value reused within a mathematical expansion is not an additional printed numeral occurrence.

Native mixed spelling is retained as `mixed(whole,numerator,denominator)`: `3+1/2`, `3+5/7`, `2+1/2`, `6+1/4`, `11+1/4`. Their values may normalize internally, but a digit-spelling experiment must retain those components rather than silently substitute `7/2`, `26/7`, `5/2`, `25/4`, `45/4`. The standalone `5/7` and `2/7` allocations are also retained. The three explicitly printed fine-content totals are 25 and 80 on p153 and 100 at the alternative conclusion on p154. The fixed-10 example's mass 80 and fine content 400 are computed, not separately written checks.

The factors expressed by *duo equa*, *bis*, *quincuplum* and *septies* are typed separately from printed digits. A digit-only permutation leaves those lexical meanings fixed unless its registered policy explicitly changes them. Multiplying by 2 or 7 to clear the displayed mixed-number denominators is marked NORMALIZATION_CLAIM: the equivalence is source-owned, but the expanded equation does not create another printed factor token. The smaller-book and partnership-method citations are external dependencies, not newly acquired proofs.

## Semantic grammar S0

An account has one header and one to three alternative branches. The header declares three stable grade types A, B, C, one target grade and a requested total mass. The type names do not identify metals. Header literals are integers 0–400, constrained by `0 < A < B < target < C <= 400` and positive requested mass. The source-derived examples use 3,4,6, target 5 and total 20. Each branch contains at most 20 statements and ends with exactly one YIELD. Paragraph closure ends the account; there is no additional terminal END word.

```
Q := NUM(n) | MIXED(NUM(w),NUM(p),NUM(d)) | QREF(i)
   | ADD(Q,Q) | SUB(Q,Q) | MUL(Q,Q) | DIV(Q,Q)
   | MASS(R) | FINE(R) | GRADE(R)
R := RREF(i) | PORTION(type,Q) | MIX(R,R) | SCALE(Q,R)
   | REPEAT_FILL(R,R,Q,Q)
S := SETQ(i,Q) | SETR(i,R) | ASSERTQ(property(R),Q)
   | ASSERTWEIGHTS(R,Q,Q,Q) | YIELD(R)
```

Arity is fixed for each constructor. Numerical literals have canonical decimal spelling with no leading zero; mixed fractions have a positive proper fractional part. Expression depth is at most 6. Each branch has at most eight scalar and eight recipe registers, defined sequentially from zero; references must point backward, and every declaration must be used. Arithmetic compound values have absolute value at most 400 and denominator at most 400. These are prospective finite modeling bounds, not claims about medieval syntax. Recipe-state vectors need no extra arbitrary numerical labels.

A recipe denotes a rational vector `(amount_A,amount_B,amount_C)`, not an available physical stock. PORTION introduces one positive component; MIX sums vectors; SCALE multiplies all components by the same positive rational. A reference reproduces a recipe definition. It does not duplicate already possessed metal. Mass is the component sum; fine content is the grade-weighted sum; grade is fine content divided by mass. The strict grade order prevents the all-equal-grade collapse.

REPEAT_FILL(P,Q,N,k) requires positive integral k, computes `j=(N-k*MASS(P))/MASS(Q)`, and requires j to be a nonnegative integer. Its output is `k*P+j*Q`. It formalizes the source's conditional remainder/divisibility advice without a hidden loop or a free loss term. Failure of the divisibility requirement rejects that use of the constructor. Ordinary SCALE can still describe rational recipe proportions; it is not silently substituted for a failed integral-repeat instruction.

ASSERTQ states a numerical mass, fineness or fine-content property of an explicit recipe. ASSERTWEIGHTS states all three component weights. YIELD requires the requested total and target grade. All alternative yields must agree in mass and fine content; they need not share component-weight vectors, production histories or physical identity. No unknown-word skipping, last-known-material carryover, unrestricted comment, per-token meaning or unreported loss operation exists in S0.

## Complete examples and nontrivial consequences

The first source-derived branch constructs `2*A+5*B`, states its grade as the printed mixed `3+5/7`, adds `9*C`, states mass 16 and fine content 80, scales the recipe by `20/MASS(previous)`, states weights `2+1/2,6+1/4,11+1/4`, then yields it. The alternative defines standard recipes `A+2*C` and `B+C`, states their masses 3 and 2, fills total 20 by taking the first twice and the second an integral number of times, states final weights 2,7,11 and fine content 100, then yields. Each definition and reference is explicit in the JSON account.

The new branch forms `4*A+4*B`, adds `12*C`, states all component weights and yields total 20 at grade 5. It is a generated valid account, not claimed printed text. The first two branches have eight statements each; the new branch has four. Their fully serialized accounts have 106 words for the two alternatives, 33 for the new account alone, and 128 for all three. These are **generated model counts**, never a selection from target lengths. S0 permits other bounded statement counts and expression trees; none of these three counts is a required target length.

With the original two weight vectors fixed, their common final grade gives `2a-3b+c=0`, hence `c=3b-2a` and `target=2b-a`. Relative grade spacing is constrained; “silver” is not identified. A freely assigned scalar for each whole fraction would lose this consequence. S0 instead evaluates shared numerical atoms and operations, so a fraction cannot independently acquire whichever value closes a diagram.

The seven rejection fixtures are: moving the new weight 12 to A while correctly stating its new component vector (mass still 20, fineness wrong); replacing the lower weighted mean by `3+1/2`; choosing one first standard batch when the remaining second-batch count is 17/2; referencing an undeclared recipe; requesting final mass 19 while silently losing one unit; changing source grade C from 6 to 7 while keeping the stated weights; and appending an unconsumed extra argument. Both source methods and the new method pass. No exhaustive grammar enumeration or target success is claimed.

## Hypothetical writing rule R0 — explicit but untested

R0 is a technical shorthand, not Latin transcription or a claim about historical notation. Traverse every expression in prefix order. A constructor is one word; its fixed number of arguments follows in order. SETQ/SETR and references fuse their register index to their type prefix. NUM fuses its decimal digits to a single numerical prefix. MIXED remains the four-word construction `MIXED NUM(w) NUM(p) NUM(d)`. FIRST begins the first branch; ALTERNATIVELY begins each later branch. Every statement and argument produced by the JSON renderer is written, with exactly one literal space between words. No source equation is forced into an equal-width row and no computed intermediate must be separately asserted.

There is one global prefix-free code h over exactly 38 atoms, explicitly listed in the JSON: the ten decimal digits; the three type names A/B/C; GRADES, TARGET, TOTAL, FIRST, ALTERNATIVELY; NUM, SETQ, SETR, QREF, RREF; and every remaining constructor name in S0. Each atom has one distinct nonempty lowercase-letter code of length 1–8, fixed across all accounts. Word construction is concatenation of atom codes: for example `NUM(25)` is `h(NUM)h(2)h(5)`, while recipe reference 2 is `h(RREF)h(2)`. No whole-number code is independently assigned. Whole words and interior spaces are preserved exactly; no erasure, arbitrary spacing or alternate per-occurrence realization is available. An example key exists by assigning distinct two-letter strings to the 38 atoms, but no target key or artificial ciphertext is generated here.

The eight-letter code bound is a declared finite parameter limit chosen without target data. Prefix code lengths may differ between atoms; the equal-width digit assumption of GDT969 is not reused. The unknown global atom assignments remain substantial freedom, and every numeral/arity/reference relation remains a shared obligation. A future negative at a word-length or fixed-keyword condition would test R0 before the content equations; it must be reported that way, not as a rejection of mixtures generally.

R0 uses ordered productive pieces and hard word boundaries. It does not explain the retained whole-form residuals, positional allographs or entry effects. No learned BPE unit is treated as a phonetic alphabet, no initial glyph is stripped, and no whole-form exception is added. Those known limitations make R0 a narrow candidate to assess, not a completed writing theory. S0 and R0 are separate: source arithmetic identifiability can be studied before paying for any target renderer search.

Finiteness does not establish practical search capacity. Thirty-eight unknown atom codes plus variable expression trees are substantial freedom; their exhaustive Cartesian product is enormous. This card supplies a specified object for a later bounded necessity check, not an implemented or demonstrated fast target solver. No target length or renderer complexity has been measured here.

## Deliberate source projection and status

The generated accounts preserve the two mathematical recipe alternatives, their grades/weights, ratio or scaling relations, references, optional explicit checks and the repeat-fill condition. They do not copy the Latin source's introduction classifying equal/unequal/proportional mixing; instructions for arranging marginal tables; partnership analogy and its external chapter citation; smaller-book attribution; metatext such as “as shown” or the name of the method; repeated prose explanations of the same quantity; or every intermediate normalization/difference action. Those actions and claims are retained separately in the 50-row source inventory. S0 is therefore a complete language for the stated generated accounts, not a full translation of every source sentence. A target account under R0 must still consume all its own words.

The numerical spelling control in GDT971 can test whether known source assertions constrain a global decimal relabeling under its separately frozen subset. A result there would concern that source oracle and spelling assumption. The current card runs only source arithmetic and semantic fixtures. [ALLOY_GRAMMAR_CHECKS.json](ALLOY_GRAMMAR_CHECKS.json) records PASS_SOURCE_ONLY, 50 true equations, three complete generated accounts and seven rejected countercases, with no target or digit-permutation access. Earlier alloy review findings and all closed target experiments remain unchanged.
