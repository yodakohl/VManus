# Two historical notations with shared, contextual meaning

2026-09-20. Status: RAW_UNREVIEWED_NOT_SELECTED. Source-only bounded supply;
neither proposal is a target reading, selected test, or cipher implementation.
The live route, composition topic, bounded duplicate navigation, IDEA127/W91,
IDEA358's source dossier, and GDT609/GDT882 primary reports were read. No new
Voynich source, image, reserve, root experiment output, or target fit was used.

The concrete addition is a writing rule in each historical source. Shared
components constrain complete contents, rather than receiving fresh meanings
for each occurrence. A Voynich realization of either rule remains unbound.
There is no licensed identification of EVA characters with Latin letters,
decimal digits, fraction marks, or known morphemes.

## A. Fibonacci: common-bar scope changes the values of earlier components

Primary: Fibonacci, *Liber abbaci*, medieval work first composed in1202 and
revised in1228; Boncompagni's1857 edition, printed24–25, PDF31–32. The notation
primer begins `Cum super quemlibet numerum` on24 and ends with `quartam et
quintam unius none` and its transition sentence on25, before the division tables.
Both complete pages were actually viewed natively. The source is the already
owned [public scan](https://archive.org/download/bub_gb_CrdUBgtAZFoC/bub_gb_CrdUBgtAZFoC.pdf),
SHA256 `e0617041071d181ae61a5109fc21ad48b8503927ed9f8f2a1378575de797ed1a`.

The source explicitly distinguishes several fractions under one common bar
from fractions under separate bars; a component's grade is counted from the
right and changes which denominators govern its value.

Full bounded primer inventory, preserving conventions beyond the proposed
ordinary-bar subset:

1. A number above a bar denotes parts of the number below. The written single
   examples are1/2,1/3,1/7,1/10,1/19,2/3,2/7,2/23,7/9,7/97,13/29,13/347.
   These are notation demonstrations, not an alleged manuscript number list.
2. Under one common bar, the rightmost numerator/denominator is the first
   grade. Moving left adds parts of parts of all earlier denominators to its
   right. The displayed numerator row1,4 over denominator row2,7 means four
   sevenths and one half of a seventh.
3. Replacing the4 over7 by zero leaves only one half of a seventh. The zero
   preserves the grade; it does not remove that denominator.
4. The displayed row1,5,7 over2,6,10 means seven tenths, five sixths of one
   tenth, and one half of one sixth of one tenth. All three contributions are
   expressly described. The text directs smaller denominators toward the left.
5. With separate bars, `rupti unius uirgule non respondent ruptis alterius`:
   the parts of one bar do not depend on those of the other. It directs the
   bar denoting the larger part toward the right. These are source writing
   conventions, not a discovered ordering convention in the Voynich manuscript.
6. It names the grades and states that their number equals the count of
   numbers under the bar. Repetition of a digit does not create a new value.
7. A bar ending in a circle is a different construction. The first displayed
   example has2,4,6,8 over3,5,7,9 with the circle at the right. Its prose lists
   8/9;6/7 of8/9;4/5 of6/7 of8/9;2/3 of4/5 of6/7 of8/9. Reading this list as
   a sum of the four named contributions is a modern algebraic expansion.
8. The other-end circle example denotes *only* the final product
   (2/3)(4/5)(6/7)(8/9). Its display also reverses the fraction order. It is
   therefore not an experimentally isolated example of moving a circle while
   holding every other printed feature fixed. The explicit prose, not a
   guessed resemblance to EVA o, owns the product interpretation.
9. Small bars drawn above a common bar supply another construction: the
   displayed1,1,1,5 over5,4,3,9 means5/9 and a third, a quarter, and a fifth
   of one ninth. The final two named parts continue on25. This construction
   must not be silently interpreted by the ordinary common-bar rule.

The source's ordinary common-bar rule has this exact modern expression. For
left-to-right cells `(a_i,b_i)`, with positive denominators,

```
V(cells) = sum_i a_i / product_{j=i..n} b_j
D(cells) = product_i b_i
V(A followed by B) = V(B) + V(A)/D(B)
```

For source rows1,4 over2,7, the value is9/14. For1,0 over2,7 it is1/14.
For1,5,7 over2,6,10 it is19/24. These reduced results are our calculations,
not asserted printed result numerals. The source owns the cells and their
complete verbal expansions. Identical two cells under *separate* bars give
1/2+4/7=15/14. A left-anchored nested rival gives1/2+4/(7*2)=11/14. Thus the
same cell inventory has three different exact consequences; an unordered bag
of digit values or an additive component gloss cannot supply all three.

An explicitly generated example, not additional historical text, is the
ordinary bar1,2,3 over2,3,5. It denotes3/5+2/15+1/30=23/30. Separating its
three bars gives1/2+2/3+3/5=53/30. Removing the zero in the source's1,0 over2,7
would similarly change1/14 into1/2. These are scope consequences, not claims
that one Voynich group denotes one number, bar, formula, or printed clause.

The prospective finite production family is `Number := digit+`,
`Cell := Number/PositiveNumber`, `Bar := Cell | Cell followed-by Bar`, and
`Account := Bar | Bar separate-from Account`. Bar composition uses the fixed
right-to-left equation above; separation terminates denominator scope.
Number spelling, the serialization of numerator/denominator rows and bar
boundaries, and their relation to manuscript spaces all remain unselected.
The three exceptional marked constructions are inventoried but not silently
added as optional escape rules to this ordinary-bar candidate.

This can explain why the same subcomponent contributes differently within a
whole form without assigning it a new per-word meaning. It does not by itself
predict entry allomorphs, prove that most prose consists of arithmetic, or
identify any target numeral. A complete future account must include its
operands, bar scope and independently constrained arithmetic assertions;
reading every unknown group as an unconstrained rational would be vacuous.
No paragraph is newly nominated and no old partial arithmetic gloss is reused.

Novelty is relative to IDEA358's [complete multiplication/reduction account](COMMON_MEASURE_CONTENT_SUPPLY.md):
that source constrains two calculation paths and an irreducible endpoint;
this source constrains how the writing itself changes reference scope inside
one compound quantity. The proposals can eventually interact but are not the
same fixed test. GDT969's fixed generated root trace remains closed. GDT882
excludes a nonzero fixed additive universal whole-line invariant, not this
nonlinear contextual quantity grammar; that distinction is not evidence for
the grammar. GDT609 licenses no arbitrary context-dependent exception table.

## B. Sherwood: mnemonic words combine proposition types and proof operations

Primary: William of Sherwood, thirteenth-century *Introductiones in logicam*,
Martin Grabmann's1937 edition, printed/PDF50–56. All seven pages were actually
viewed natively. [Official BAdW PDF](https://publikationen.badw.de/de/011720359/011720359.pdf),
SHA256 `c0c7434f09d950bc5489f67f7b897d9361024d077e4389fdaa42500d4bccd53e`.
The edition identifies Paris, BnF latin16617 as its manuscript witness;
this task has not collated that manuscript or a second edition. The source
reading below preserves the1937 printed witness, including disagreements.

Sherwood explicitly assigns a/e/i/o to four proposition types and s/p/m to
conversion and premise exchange; the mnemonic therefore carries reusable
semantic information inside a written word, with its figure supplied by context.

The complete four-line mood mnemonic at55 is:

```
Barbara celarent darii ferio baralipton
Celantes dabitis fapesmo frisesomorum
Cesare campestres festino baroco
Darapti felapton disamis datisi bocardo ferison.
```

The figure mnemonic is `Sub pre prima bis pre secunda tertia bis sub.` The
source explains on51 that the two premises share one middle term and a
syllogism has three terms. The middle is subject in one premise and predicate
in the other in figure1; predicate in both in figure2; subject in both in
figure3. The first two mnemonic lines belong to figure1, the four words of
line3 to figure2, and the last six to figure3. These contextual facts are
required: the mnemonic word is not a complete serialization of its arguments.

The following crosswalk gives the ordered major/minor/conclusion types from
the source's full descriptions and examples. A=universal affirmative,
E=universal negative, I=particular affirmative, O=particular negative.
The first three vowel occurrences match these types. The bounded explanation
does **not** explicitly state a universal first-three-vowels extraction rule;
that positional correspondence is our crosswalk to the ordered prose.

| Printed word | Figure and direction | Types | Source reduction description |
|---|---|---|---|
| Barbara |1 direct|AAA|First perfect mode; explains dici de omni.|
| celarent |1 direct|EAE|Second perfect mode; explains dici de nullo.|
| darii |1 direct|AII|Third direct mode.|
| ferio |1 direct|EIO|Fourth direct mode.|
| baralipton |1 indirect|AAI|Derive first-mode conclusion, then convert per accidens.|
| Celantes |1 indirect|EAE|Simple conversion of the universal-negative conclusion.|
| dabitis |1 indirect|AII|Convert conclusion per se to the third mode.|
| fapesmo |1 indirect|AEO|Major per accidens, minor per se, exchange premises; fourth mode.|
| frisesomorum |1 indirect|IEO|Convert both premises per se and exchange; fourth mode.|
| Cesare |2 direct|EAE|Convert major; second mode of figure1.|
| campestres |2 direct|AEE|Convert conclusion and minor, exchange premises; second of figure1.|
| festino |2 direct|EIO|Convert major; fourth mode.|
| baroco |2 direct|AOO|Major plus contradictory of conclusion produces contradictory of minor.|
| Darapti |3 direct|AAI|Convert minor; third of figure1.|
| felapton |3 direct|EAO|Convert minor; fourth of figure1.|
| disamis |3 direct|IAI|Convert major and conclusion, exchange premises; third mode.|
| datisi |3 direct|AII|Convert minor; third of figure1.|
| bocardo |3 direct|OAO|Contradictory of conclusion plus minor produces contradictory of major.|
| ferison |3 direct|EIO|Convert minor; fourth of figure1.|

The operation explanation across55–56 reads:

> In hiis versibus a significat propositionem universalem affirmativam, e universalem negativam, i particularem affirmativam, o particularem negativam, s conversionem per se, p conversionem per accidens, m transpositionem premissarum, b et r cum sint in eadem dictione significant reductionem per impossibile.

At50 the source defines conversion by exchanging subject and predicate.
Per se preserves quality and quantity and is exemplified for E and I.
Per accidens preserves quality but changes quantity, exemplified as A(X,Y)
giving I(Y,X). In modern set semantics that step requires X to be nonempty;
the source does not print an extra existential premise in its worked argument.
Page50–51 also treats contraposition, infinite terms and a qualified dispute
about I conversion. That material is not represented by a new arbitrary
mnemonic operator in the proposed A/E/I/O+s/p/m subset.

### Complete owned fapesmo construction

The eighth first-figure mode at53.16–24 starts with these complete assertions:

> omnis homo est animal. Nullus lapis est homo. Ergo quoddam animal non est lapis.

It expressly classifies the conclusion as indirect and says it reduces to
the fourth mode by `conversionem maioris per accidens et minoris per se et per
transpositionem illarum`. It then gives the converted major as `quod animal
est homo` and the converted minor as `nullus homo est lapis`, and states that
their exchange yields the earlier conclusion in the fourth mode. The printed
`quod` is retained; it is not silently transcribed as `quoddam`. The particular
force is supplied by the expressly named per-accidens rule on50.

Writing H=human, A=animal, L=stone only as our explanatory class labels, the
complete conditional content is:

```
premises: A(H,A), E(L,H)
major p: A(H,A) -> I(A,H), conditional on H nonempty
minor s: E(L,H) -> E(H,L)
exchange: E(H,L), I(A,H)
fourth mode: O(A,L), the original conclusion
```

The same p must change universal to particular while reversing arguments;
the same s reverses without that quantity change; m changes premise order
without renaming the classes. This joint consequence rejects a generic
"reverse something" gloss. Applying per-se reversal to every A statement is
false, e.g. H={x}, A={x,y}; every H is A but not every A is H.

### Complete campestres construction and source conflicts

The second second-figure mode at54.4–9 gives:

> omnis margarita est lapis. Nullus homo est lapis. Ergo nullus homo est margarita.

It reduces to the second first-figure mode by conversion of conclusion and
minor plus premise exchange. Thus, with P=pearl, L=stone, H=human, the original
`A(P,L), E(H,L) => E(H,P)` becomes `E(L,H), A(P,L) => E(P,H)`, followed by
conversion of the conclusion to E(H,P). Both paths retain the same three
classes. This modern explicit sequence expands the source's named operations;
the intermediate formulas are not additional printed Latin sentences.

Three disagreements prevent treating the printed mnemonic rule as a clean
universal decoder:

1. The source prints **campestres**, including p. Its prose reduction calls
   for simple conversions and exchange, with no per-accidens step. Do not
   normalize the word to Camestres or suppress its p without an explicit
   witness/version decision. Attachment to the preceding vowel is also an
   inferred crosswalk, not an explicit universal clause of this rule paragraph.
2. The rule really prints **b et r**, not b and c. Both Barbara and baralipton
   contain b+r as well as baroco and bocardo. It therefore does not uniquely
   select just the two worked reductio modes. This is a nonselective/ambiguous
   instruction, not permission to modernize its consonants.
3. At56.15–16 it prints `In tertia autem non sequitur aliquid maiori existente
   negativa.` This conflicts with its explicit negative-major third-figure
   modes, including felapton and ferison. Retain **maiori**; do not silently
   substitute minori. The same closing paragraph also asserts the reduction
   of all modes to the first two perfect modes, prohibits two negative or two
   particular premises, disallows a particular major or negative minor for a
   direct first-figure result, and disallows two affirmative premises in
   figure2. Its complete closing claims are evidence, not automatic filters
   overriding the preceding worked modes.

### Raw mechanism and meaningful rival

The source-native finite semantic inventory has four proposition types,
three term positions, three figures, nineteen named modes, and the stated
conversion/exchange/reductio operations. A prospective content production is
`Argument := class-reference`; `Proposition := Type(Argument,Argument)`;
`Proof := Figure + three shared class-references + Mode + its certified
reduction`. Arguments may vary across complete proofs; a sequence of proofs
need not copy the verse or have a fixed source length. Class references and
figure must be written or inherited by one declared, bounded scope rule;
unlimited invisible premises and locally reassigned class identities are barred.

The historical name supplies shared type and operation cues, but it does not
supply the class names, a Voynich segmentation, or a surface writer for every
sentence explaining the proof. Initial consonants and every residual sound
cannot be given an ad hoc target meaning. The19 named forms and the conflicts
above are the full retained source inventory, not freely generated combinations
of arbitrary fillers. A fixed experiment must choose a source-faithful bounded
subset or collate the disputed rules *before* fitting; neither action is done
here. This raw card is therefore not a selected nineteen-word literal-copy test.

One consequence requires both quantifier pattern and shared argument roles:
figure1 AII has `A(M,P), I(S,M) => I(S,P)`. Keeping AII but using figure2 gives
`A(P,M), I(S,M) => I(S,P)`, which is invalid. In a two-object counterworld,
P={x}, M={x,y}, S={y}, both figure2 premises hold and its conclusion fails.
This is an explicit explanatory countermodel, not a new target computation.
An approach that classifies vowel patterns while leaving term incidence free
cannot distinguish those cases. Permuting all class names consistently remains
a symmetry: logical success alone cannot identify "human", "stone", or "pearl".

IDEA127 and [W91](../../proposals/translation_programs_20260912/work/W91/REPORT.md)
remain intact. W91 fixed sol=therefore and qokeey=if-then in seven f83r records,
found five countermodels and two unbound cases, and did not test categorical
quantifiers or a historical mnemonic writer. No such old gloss is inherited.
The new source constrains internal word composition and proof transformations;
it does not supply a missing target constituent grouping. GDT609's mixed
abbreviation model likewise was a historical prior, not a validated word map.
GDT892's primary report was also read: its Latin consonant/vowel channel stopped
at insufficient eligible control sentences before cipher generation. It did
not disprove the channel, and is not rerun here. Historical mnemonic vowels
are semantic type cues in this source; they are not evidence that EVA is a
Latin phonetic alphabet or that the GDT892 capacity threshold may be lowered.

## Source render receipt and exact limits

Native inspection hashes, source page identifiers only; no pixels or private
cache paths are included in this public dossier:

| Source page | SHA256 of inspected render |
|---|---|
| Abbaci24 / PDF31 JPEG |6ff79907fb6ae9d796574f2e63580680d50d2f789895056df8101a5af60c45a2|
| Abbaci25 / PDF32 JPEG |b520687b87c6cdaa1240e8f0f62715efdb39391679dfcbe608502a5e194c4207|
| Abbaci24 / PDF31 larger PNG |b7a88426c82302a3932c285103790ba345ebc132f78c9ff58137eb300df4bf70|
| Sherwood50 JPEG |a988e859ad4e545d374b8ea92a930322a3b86a48b674d02dcd1134b7bfdbec00|
| Sherwood51 JPEG |780218c456560e218c7b0f9c409f1afc9d26bdd581d3e99b66a3b29fe4059719|
| Sherwood52 JPEG |fdfcd0ad02f6f01122ba44f044ed3e5e12a8569817377d0522760e7a4b99ca73|
| Sherwood53 JPEG |10a9873fa64afce65e14794a80f0d16e745c2dd7a6be40caa10cb2a347883017|
| Sherwood54 JPEG |2fa193ea3a488ec6f6d95c79d989792a2bda5ebadf98f150348e0a1190163f01|
| Sherwood55 JPEG |7db10fe87a32f8c574a095ed85c943d652f711b392d232e3ecf482778879e0b5|
| Sherwood56 JPEG |831da22df7470d6dd0633d78390dac61b009e8300b9f1b04c47551632b2bceb5|

Result: two historically concrete mechanisms are retained as raw supply.
No confirmed word, complete Voynich translation, manuscript semantic
discriminator, target owner, cipher alphabet, or viable target writer has been
established. Missing target realization is an explicit selection debt, not a
claim that joint exploratory meaning hypotheses require confirmed seed words.
