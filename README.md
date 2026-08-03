# Voynich first translation — working version 0.23

This is the first semantic reading supported by our local experiments. It is
not yet a word-for-word plaintext translation. Question marks are deliberately
left where the manuscript does not identify an English meaning.

## 1. First token-scale translation

On f75v, the same upper label occurs at the third outlet in two independently
drawn, mirror-matched five-outlet fans:

`daldy` → **[FAN / OUTLET POSITION 3]**

Natural reading in that diagram: **“third fan outlet”** or **“outlet slot
three.”** Scope is local: this does not yet prove that every `daldy` elsewhere
means “three,” “middle,” or “outlet.”

## 2. f67r2 lunar-record translation

The twelve records read, in physical order:

> **FULL DISC — RED CRESCENT — FULL DISC — RED CRESCENT — FULL DISC — RED
> CRESCENT — FULL DISC — FULL DISC — RED CRESCENT — RED CRESCENT — FULL DISC
> — RED CRESCENT.**

The prose inside each record is still unknown. A separate line is strongly
associated with the full-disc class, and its ending points back to the end of
its own record. The literal interlinear reading is:

| record | EVA object label | English record reading | separate key |
|---:|---|---|---|
| 1 | `qotoear` | **FULL-DISC ENTRY: ?** | body-tail key `-dy` |
| 2 | `dchdar` | **RED-CRESCENT ENTRY: ?** | absent |
| 3 | `y saldal` | **FULL-DISC ENTRY: ?** | body-tail key `-al` |
| 4 | `ytodal` | **RED-CRESCENT ENTRY: ?** | absent |
| 5 | `tol daiin` | **FULL-DISC ENTRY: ?** | body-tail keys `-in`, `-am` |
| 6 | `otar dy` | **RED-CRESCENT ENTRY: ?** | exceptional key `-dy` |
| 7 | `cho dal g` | **FULL-DISC ENTRY: ?** | body-tail keys `-ar`, `-an` |
| 8 | `ytchodly` | **FULL-DISC ENTRY: ?** | body-tail key `-in` |
| 9 | `octhys` | **RED-CRESCENT ENTRY: ?** | absent |
| 10 | `ytokar` | **RED-CRESCENT ENTRY: ?** | absent |
| 11 | `otolor` | **FULL-DISC ENTRY: ?** | body-tail key `-in` |
| 12 | `okodar` | **RED-CRESCENT ENTRY: ?** | absent |

This translates the record class and cross-reference operation, not the
unknown body clauses. Heading presence alone reads 11/12 classes; the nearby
label's local `l` channel reads 10/12. Their different errors show that these
are two separate channels rather than one invented word equation.

## 2a. Corrected physical f68r1 star-label inventory

The 2014 Voynichese Project spatial transcription already supplies word boxes
for this page. Registered to the cached scan, it resolves all 29 physical
label positions. It also falsifies the earlier candidate-constrained OCR:
only 1/29 top assignments was correct. In particular, the four formerly
retained assignments correct as follows:

| physical star | documented locus | current literal label | old CTC claim |
|---|---|---|---|
| G02 `(358,175)` | f68r1.9 | `odchecthy` | f68r1.12 `chocfhy` — false |
| G10 `(456,307)` | f68r1.24 | `otykchs` | f68r1.19 `otys` — false |
| G12 `(229,327)` | f68r1.16 | `okear` | f68r1.34 `osdaiin` — false |
| G14 `(392,354)` | f68r1.23 | `otchdy` | f68r1.29 `ykchdy` — false |

The complete corrected inventory is
`experiments/semantic_assumptions/results/f68r1_documented_star_label_mapping.tsv`.
This is a location/transliteration result only: every English lexeme remains
`LEX=?`, and no star or constellation identity follows from a box coordinate.
The corrected labels also fail three direct structure tests: their morphology
does not track star position/paint/shape; seven plausible geometry routes do
not form a prose-like chain or cycle; and coordinate-only alignment to f68r2
does not preserve label morphology, even after frozen root substitutions.
They must currently remain **29 separate untranslated labels**.

A manuscript-wide text-blind geometry search also finds no second diagram
whose mapped labels translate these: all 743 compatible page pairs are null
after same-kind and three-transcription controls (family p=.797).

## 2b. Illustration-interrupted reading units

Exact word boxes expose 408 internal same-row gaps wider than two word-box
heights. An independently trained hierarchy places the group near a physical
line break (0.571/0.693 in two canonical views), yet near an ordinary line
continuation rather than a new entry (0.082/0.038 on that second scale).

The licensed structural reading is:

> **[TEXT SEGMENT] — [CONTINUATION BREAK AROUND ILLUSTRATION/COLUMN] — [TEXT
> SEGMENT]**

Left-to-right order is retained. This is neither an ordinary word space nor a
new paragraph, and it is not asserted to be European sentence punctuation.
The conservative export assigns 105 high and 18 medium individual candidates;
285 other large gaps remain marked `LAYOUT_INTERRUPTION?` because the result is
group-level there. See `transcription/zl3b_layout_aware_reading_units.tsv`.

At these gaps the right segment preferentially begins with a `d/y/t` initial
operation (OR 2.56, corrected p=.00881; strongest in Currier B), but the
independent line-production gradient does not restart. The sharper reading is:

> **[LEFT CONTINUATION] — [LAYOUT BREAK] — [RIGHT RESTART-FORM CONTINUATION]**

This is a grammatical/layout operation, not an English word meaning “start.”

## 2c. f57v repeated symbol-wheel reading

The circular f57v diagram contains the same 17-position written template in
each of four quadrants. Thirteen positions have reusable spatial boxes; eleven
repeat literally, while only the `k/m` and `f/p` positions vary:

> **[17-SLOT SYMBOL TEMPLATE] × 4 QUADRANTS**

This is a structural translation, not the claim “Voynich alphabet.” Words at
equal radial positions on the neighbouring rings do not preserve surface,
root, or form morphology after the exact rotation/reflection family
(p=.181). The wheel's circular distances also fail to order the associated
f66r rows (p=.788), and ordinary word construction does not follow the wheel's
order under an exact 8! test (p=.506). No plaintext letter, number, season, or
compass meaning is currently assigned to any slot.

## 2d. f66r nested page structure

The 15 far-left labels divide the 32 right-column prose lines into contiguous
one-to-three-line bands. Under bottom-edge alignment every independently
transcribed paragraph begins at a band boundary. The licensed reading is:

> **[BAND LABEL] -> [ONE-TO-THREE-LINE PROSE BAND]**

The label strings do not unusually resemble, recur inside, or predict the
grammar of their own bands after local paragraph, vertical, length, edition,
and multiple-view controls (global p=.726). Therefore the hierarchy is read,
but every label meaning remains `LEX=?`.

## 3. Zodiac passage translation

The circular zodiac prose contains a distributed four-state cycle. Its two
textual switches recover all ten surviving sign passages:

| depicted passage | translated text state |
|---|---|
| Pisces | **ZODIAC-CYCLE STATE 3** |
| Aries | **ZODIAC-CYCLE STATE 0** |
| Taurus | **ZODIAC-CYCLE STATE 1** |
| Gemini | **ZODIAC-CYCLE STATE 2** |
| Cancer | **ZODIAC-CYCLE STATE 3** |
| Leo | **ZODIAC-CYCLE STATE 0** |
| Virgo | **ZODIAC-CYCLE STATE 1** |
| Libra | **ZODIAC-CYCLE STATE 2** |
| Scorpio | **ZODIAC-CYCLE STATE 3** |
| Sagittarius | **ZODIAC-CYCLE STATE 0** |

The contributing constructions are final `X+od` versus initial `ot+X`, and
`ar` versus `al`. They encode the passage state as aggregate choices; they are
not licensed as universal English words.

## 4. First ordinary-sequence structural reading

The f67r2 body fragment

`todaiin dain dy`

has the provisional interlinear reading

`todaiin[AII+N DESCENT-SOURCE] dain[AI+N DESCENT-TARGET] dy[?]`

or, at construction level:

**[LINE-LOCAL REL-I ORDER: AII+N FORMS BEFORE AI+N FORMS] — ?**

This order was suggested by the fragment and then tested in ordinary
Currier-A/B prose. On held even folios it occurs 61–67 times versus 37–42 in
the reverse direction across three transcriptions. Whole-page exact tests and
same-word-base shuffles pass in all three readings; five matched generated
texts lean in the reverse direction. The complete 35,060-token structural
table now marks 120 such descending edges.

The order is not confined to neighbors. After removing every adjacent pair,
held even folios still contain 228–262 non-neighboring AII-before-AI pairs
versus 147–165 reverse (exact page p=.0012–.0020). Global and within-page
same-base shuffles pass in all three readings, while all five generated
controls fail. The stronger translation is therefore a **line-local ordering
field**, not a fixed two-word idiom. A separate line table makes all 4,035
confirmed prose-line stage sequences explicit.

Across the full prose sample, the polarity reverses at the pen's return to the
next physical line. On held folios, immediate boundaries have 160–176
`AI+N → AII+N` transitions versus 120–132 continuations (exact page
p=.0019–.0026); both same-base nulls pass in every reading and all five
generated controls fail. The safe document-level reading is:

> **WITHIN A LINE: AII+N is relatively earlier and AI+N relatively later.**  
> **AT A LINE BREAK IN THE FULL DATA: AI+N → AII+N is enriched.**

This relationship is deliberately not upgraded to absolute “early” and
“late” word meanings. After removing every line containing both grades, held
singleton lines show no predicted absolute position bias: `AI+N` is slightly
earlier, not later, and all same-base controls are null or reverse. The
translation therefore applies only when the grades enter the ordered
construction; it is not a universal line coordinate.

A stricter boundary audit also removes every mixed-grade line from both sides
of the break. Its held counts still lean `AI+N → AII+N` in all readings
(43/30, 40/30, 41/30), but only part of the predeclared tests pass. Therefore
“reset” is no longer claimed as a separate state-machine operation: the
boundary enrichment may largely be the concatenation of lines whose internal
construction already runs AII-before-AI.

The tempting alternative that AII and AI are opening/closing brackets also
fails. Ordered AII...AI intervals do not contain an excess of the independently
confirmed D/REL/L grammar and do not reliably block those edges from crossing
the interval. They remain an ordered relational tier of unknown function, not
a translated noun phrase, clause, or parenthesis.

The extended 35,060-token table marks 336 full-data boundary-transition edges
as well as the 120 adjacent descents; the legacy column name says `reset`, but
version 0.4 interprets it conservatively as a boundary transition.

This is a sentence-order translation, not a word gloss. A separate test found
no relation between AI/AII/AIII grade and visible 6–9-point stars, so `aiin`
and `ain` must **not** yet be translated as “two” and “one.” AIII is also too
rare in adjacent contrasts to place in the order. Because f67r2 itself lies
outside the Currier-A/B confirmation scope, its displayed annotation remains
an explicitly analogical application of the confirmed prose rule.

## 5. Star-entry structural-semantic translation

For 212 aligned star entries containing three to seven lines, the first and
last lines form a different content tier from the middle. The source axis was
learned only from P-layout pages versus the ten nearby H pages in the same
Currier-A/hand-1 register. Every retained model had to classify both held
folio parities in all three transcription readings before the star-entry line
roles were inspected.

An independent axis learns root preferences in P illustration-label lines
versus P prose while holding the neutral root role fixed. It transfers in
both directions between the early and late P page groups (AUC .60--.69), then
declines across the star entry. Discovery selects first-minus-last; 93 untouched
late entries confirm it at z=4.91/5.70/5.30 and joint p<.000005. All five
relaid pseudo-text controls are null.

Combining the two channels gives this translated entry template:

> **[RELATIVELY P-LABEL-LIKE ENTRY OPENING; P-CONTENT-DEPLETED ROLE]: ?**  
> **[P-SECTION-LIKE TECHNICAL CORE; INTERMEDIATE LABEL-LIKENESS]: ?**  
> **[RELATIVELY P-LABEL-UNLIKE ENTRY CLOSE; P-CONTENT-DEPLETED ROLE;
> OPTIONAL AII+N / AI+N / ED CLOSE FORM OR OTHER CLOSE]: ?**

Inside that template, `D_SELECT_Q` is an **entry-opening-enriched
selector-to-q-dependent pair**. A fixed root-free family of 18 tests selected
its FIRST-minus-LAST rate on 119 early entries (family p=.0122). The same
direction holds on 93 untouched late entries in ZL/IT/RF (z=3.61/3.45/3.39;
joint family p=.000165), and none of 69 relaid pseudo-manuscripts reaches the
real joint z=3.48 (maximum 3.01; p=1/70=.0143). This is an enrichment, not a
rule: the pair can occur in middle and closing lines too.

For first-line occurrences, the construction now has an internal semantic
direction. The final model uses normalized roots only and ignores q and all
other formal roles; 96.9--99.4% of endpoint events have actual occurrences in
the P illustration-label corpus. Its label/prose discrimination transfers in
both directions between disjoint P page groups (AUC .612--.668). On 119 early
entries, the q-dependent endpoint is more P-label-like than the D-selector
endpoint (joint z=3.99, p=.000018). The 93 late entries confirm this in every
reading (z=6.13/6.52/5.73; joint p=.000002), and 0/69 occurrence-weighted Timm
controls reach real z=6.13 (maximum 2.09; p=.0143). Translate:

> **[RELATIVELY P-LABEL-UNLIKE D-SELECTOR SLOT] -> [RELATIVELY
> P-LABEL-LIKE Q-DEPENDENT SLOT]**

This is the first semantic side assignment inside a prose construction. It
does not prove that the right side is a noun or object name.

The direction is construction-wide, not merely a star-opening artifact. After
excluding every P source page, each grammar edge is compared with ordinary
non-construction pairs on the same page and in the same horizontal-position
bin. Odd folios select only `D_SELECT_Q` from D/REL/L (family p<.000002).
Even folios confirm z=5.79/5.65/4.91, and none of 69 occurrence-weighted
pseudo-texts reaches the real joint z=5.45 (maximum 2.61; p=.0143). The safe
construction translation is therefore:

> **[P-LABEL-CONTENT-DEPLETED SELECTOR] -> [P-LABEL-CONTENT-ENRICHED
> DEPENDENT]**

This remains a relative content axis. “Operator -> content-like dependent” is
a useful functional paraphrase, not a claim of “verb -> noun.”

A corrected four-root filler search sharpens the pair without inventing a
noun. The normalized root class `H` is a **P-label-depleted D-selector
filler**: discovery family p<.000002, held joint z=7.85 and p<.000002, with
0/69 controls reaching it (maximum 2.74). Roots `o` and `ok` are confirmed
structural q-dependent fillers, but their independent label evidence is neutral
or negative. The attractive P-label-enriched root `ot` fails the discovery
family (p=.388), so it is not promoted. Safe root readings are therefore:

> **`H` -> [P-LABEL-DEPLETED D-SELECTOR FILLER]**  
> **`o`, `ok` -> [Q-DEPENDENT STRUCTURAL FILLER]**

`H` is the parser's normalized root class, not an EVA letter or sound.

The corrected search over 35 source-valid models and three within-entry
contrasts selects root-plus-role content in the middle versus both edges
(family p=.00020). The effect is positive in ZL/IT/RF (z=4.32/3.47/4.04).
After the model and contrast were frozen, none of 69 independently generated
and identically relaid pseudo-manuscripts reached the real joint z=3.94
(maximum 3.03; empirical p=1/70=.0143).

The closing line also has a root-free optional marker family. Discovery over
35 supported formal candidates selects a line-final `AII+N OR AI+N OR ED`
form (p<.000005); 93 untouched entries confirm it at z=4.75/5.29/4.93 and
joint p<.000005. It occurs in 24--29 of those 93 closing lines, so it is one
closing strategy rather than a universal period. Once frozen, none of 69
pseudo-manuscripts reaches the real z=4.99 (maximum 1.93; p=1/70=.0143).

This is an aggregate role translation: 130/212 ZL entries point in the
selected direction, so it does not assert that every individual middle line
is P-like. “P-section-like” means the internal content axis that distinguishes
the manuscript's P-layout pages from nearby full-plant H pages. It does not
yet prove the English words “recipe,” “ingredient,” or “preparation.” A
discovery/held search for a single object-like carrier also fails its held
family test (best p=.232), so no root is promoted to a noun. The combined
791-line first translation is
`experiments/semantic_assumptions/results/star_entry_combined_first_translation.txt`.
Its exact 447 ZL `D_SELECT_Q` word-pair occurrences are exported separately so
the selector/dependent syntax is visible without assigning either side an
English word.

## 6. First ordinary-prose semantic-field root

The normalized root class `ol`, when it fills the independently content-like
right side of `D_SELECT_Q`, is strongly associated with the bathing/
balneological section. On odd ZL folios it is selected from all six supported
dependent roots (B-minus-S rate +.133; family p=.000002). Even ZL/IT/RF folios
confirm it at z=4.21/4.08/3.47. A stricter generated-text control lets each of
69 pseudo-manuscripts choose its own best odd-folio root and tests that root on
even folios; none reaches the real discovery and held thresholds (p=.0143).

The safe interlinear reading for the relevant `qol...` dependent is:

> **`ol` -> [BATHING/BALNEOLOGICAL-FIELD-ASSOCIATED D-DEPENDENT CONTENT
> CLASS]**

There are 79 such ZL edges in B and one in S. This is narrower than a word
translation but stronger than a generic register count because the root is in
a separately established content-enriched slot. The B drawings combine human
figures, pools/fluids, vessels, and connecting apparatus, so current evidence
cannot choose “woman,” “water,” “body,” “bath,” or “tube.” The 80 annotated
occurrences are in
`experiments/semantic_assumptions/results/d_dependent_section_class_translation.tsv`.

A frozen same-hand falsifier now makes that field reading stronger. Comparing
only Currier B, hand 2, `ol` is higher on bathing than herbal pages in odd and
even ZL/IT/RF panels (z=3.13--3.86; every p<=.00012). Each of 69 relaid
pseudo-manuscripts selected its own strongest odd-folio root and challenged it
on even folios; none reaches both real thresholds (p=.0143). Thus the result is
not generic Currier-B, hand-2, or illustrated-herbal vocabulary. The English
choice among water, body, person, pool, bath, and apparatus remains open.

The field signal is not only a mixed bag of long words. A predeclared split
separates the single-unit `qol` dependent from words beginning with the same
root and continuing into more units. The single-unit channel is bathing-over-
herbal in all six panels (49 ZL events in B, zero in matched H; corrected
p<=.00020) and 0/69 process controls repeat it. It may therefore be annotated
as `[BATHING/BALNEOLOGICAL-FIELD-ASSOCIATED SINGLE Q-DEPENDENT UNIT]`. The
expanded channel points the same way in all panels but RF-even has only six
events and misses correction (p=.099); it remains a root-level near-miss, not
a second confirmed word class.

Three finer tests do not supply an English noun. The frozen single-unit feature
does not correlate with seven cached, writing-erased visual concepts (odd
family p=.734; even direction reverses), nor with objective proximity to the
manuscript's own `Ln` figure versus `Lt` tube labels (odd p=.110; frozen even
p=.856). Its surrounding word-role/root context also fails a 28-view family
(p=.381). Thus the annotation remains a field association: it cannot yet be
printed as “water,” “woman/person,” “body,” “pool,” “bath,” or “tube.”

The root is nevertheless no longer construction-specific. After deleting
every D-dependent first root—the complete class that originally selected
`ol`—the remaining `ol` units are still bathing-over-herbal in odd and even
ZL/IT/RF panels (z=3.22--3.89; every p<=.00013). Non-q standalone, non-q
expanded, and q-standalone forms each replicate in all six panels. None of 69
generated manuscripts repeats the complete selection/validation/transfer
chain (p=.0143). The licensed reading is therefore broader:

> **`ol` -> [CROSS-CONSTRUCTION BATHING/BALNEOLOGICAL-FIELD STEM]**

This adds 1,117 non-D word occurrences on B pages to the interlinear. It is a
stem-level field translation, not permission to gloss each form as “water.”
Literal standalone forms survive a separate exact check after every D-right
word is excluded: ZL odd/even `ol` counts are 115/11 and 108/11 on B/H pages;
`qol` counts are 37/1 and 21/0. Both pass the two-word family in all six
panels. The visible pair can therefore be read locally as:

> **`ol` -> [FIELD STEM; NON-Q STANDALONE STATE]**  
> **`qol` -> [SAME FIELD STEM; Q STANDALONE STATE]**

This is a morphological translation, not a claim that `q` is a universal case
marker or that EVA `ol` gives the stem's sound. The merged table marks 223
exact `ol` and 107 exact `qol` occurrences with these scoped state readings.

The same frozen single-unit stem also predicts text-class page f76r, which was
absent from all B/H selection. It occurs in 6/52 D slots in ZL/IT (4/45 RF),
split across both page halves, versus zero on the three other Currier-B/hand-2
`T` pages. All three generated-text transfer tails are 0/69 (p=.0143). Six
f76r occurrences are now read as `[BATHING/BALNEOLOGICAL-FIELD-LIKE TEXT-PAGE
TRANSFER]`; this shows topic continuity without identifying the underlying
object noun. The held page-level result also tags all 47 f76r prose lines as a
`[BATHING/BALNEOLOGICAL-FIELD-LIKE TEXT PAGE]`.

Searching inside the enlarged stem paradigm does not yet narrow that field.
Sixty-seven supported role, form, joined-root, and neighboring-root subtypes
compete against every cached named image axis and four prompt-free components.
The exact paired-folio families fail (named p=.688; latent p=.631), so no
compound or inflection is promoted to water, person, body, bath, apparatus, or
plant.

A stronger cached-image falsifier now covers all 19 relevant B pages. It
compares recto with verso inside nine complete folios using all 512 exact
swaps, two independent vision encoders, global and local-tile views, seven
frozen concepts, colored-fluid area, and a prompt-free visual search. Neither
the semantic family (p=.908) nor the latent-image family (p=.930) survives.
The broader field tag is retained; water, woman/person, bath, pool, vessel,
tube, body, and plant remain unlicensed glosses.

A finer within-page attempt links 740 prose lines to nearby text-masked image
regions. Its first apparent `ol`/visual-component result is retracted because
inspection found writing and scan-edge leakage in the crops. After explicitly
erasing every documented word box and small residual component, both the
root/concept family (p=.245) and prompt-free family (p=.789) are null. No
within-page picture noun is added.

The manuscript's own figure/nymph (`Ln`) versus tube/apparatus (`Lt`) label
classes also fail to expose a noun stem after page, folio-parity, edition, and
73-feature correction (p=.524). The best `ot`-ending tube hint fails an
independent container-label holdout (p=.502), including zero ZL hits among 37
containers. Therefore `ot` is not translated as “tube” or “container.”

Allowing pharmaceutical labels to use their own section-local vocabulary does
not rescue the object nouns. On 183 labels from 12 pages, all 118 tested
surface, atom, root, and form features fail the complete container-versus-
plant-fragment family (p=.472). The directional hints `final r` for fragments
and `root k` for containers stay untranslated.

A fixed five-slot sentence-position audit also fails. In eight-line local
blocks, FIRST, SECOND, BODY, PENULT, and LAST lexical views all compete against
root-free form in the identical position. Best `PENULT|ATOM2` is raw p=.0334
but 30-test family p=.268 and reverses on even ZL. Ordinary prose therefore has
no licensed fixed topic/noun slot at a European-style line edge or center.

## 6a. Residual field elements independent of `ol`

After deleting every complete word that contains `ol` and every complete word
in the D-dependent-right slot, a new two-sided search still finds two stable
field elements inside the same Currier-B/hand-2 register:

> **`l-...` -> [BATHING/BALNEOLOGICAL-FIELD-ENRICHED INITIAL ROOT ELEMENT]**  
> **`...-od` -> [HERBAL-FIELD-ASSOCIATED FINAL ROOT ELEMENT]**

The roots survive odd/even folios, ZL/IT/RF readings, the same plain `BARE`
role, and their exact expanded-word positions. The discovery family p-values
are .000135 for `l` and .0201 for `od`; neither of 69 generated manuscripts
repeats each complete overall/role/position chain (p=.0143). This supports
field association, not the word equations `l=water` or `od=plant`.

The pair independently identifies text-class page f76r, which was never used
to select it. After the same masks, f76r contains `l/od=38/0`; the other three
same-register T pages contain `40/63`. Both halves and all three readings point
bathingward, and all three generated-text tails are 0/69. Thus f76r's
bathing-like subject matter is now supported by two disjoint lexical channels:
the earlier `ol` construction and the residual `l/od` axis.

Exact minimal pairs now determine what the edge elements do to a word. For 38
odd and 39 even ZL `l+BASE` base types, and 22/11 `BASE+od` types, the remaining
canonical BASE also occurs as a complete word. Holding that BASE literally
fixed, initial `l` moves use toward bathing pages by odds 3.05--3.67; final
`od` moves use toward herbal pages by odds 21.96--59.83. Every ZL/IT/RF panel
passes and both generated-process tails are 0/69. The morphological reading is:

> **`l + X` -> [LINKED/DEPENDENT FORM OF X; BATHING-FIELD-ENRICHED]**  
> **`X + od` -> [HERBAL-FIELD DERIVATION/CLASS OF X]**

“Derivation/class” is deliberately neutral: it may ultimately be a topic,
state, relation, or classifier. It is not yet an English prefix/suffix gloss.
Canonical base `che` (usually surfaced as `chey`) is the one complete
three-form paradigm present in every parity and transcription:

> **`chey` -> [CROSS-FIELD BASE X; LEX=?]**  
> **`lchey` -> [LINKED/DEPENDENT L-FORM OF X; BATHING-ENRICHED]**  
> **`cheody` -> [HERBAL-FIELD DERIVATION OF X]**

The v0.15 interlinear marks 117 plain bases, 25 `l` forms, and 9 `od` forms.
This is an internal morphological translation; it does not yet say what X is.

The `l` operator participates in a visible phrase rule. Holding the base exact,
odd ZL selects the preceding role `BOUND_E`: it favors `l+BASE` over plain BASE
at z=6.09. The rule survives the other five bathing panels (worst z=4.57), then
transfers independently to section-S/hand-3 prose (z=6.16/3.90 across halves
and all readings) and a full synthetic process control (0/69). Its neutral
sentence reading is:

> **[WORD ending E-BOUND] -> [LINKED/DEPENDENT `l+BASE` FORM]**

This is a general selector-dependent phrase edge whose use is bathing-enriched,
not a bathing noun or dedicated bath classifier. It is not yet a European
preposition, subject, verb, or object. The v0.17 merge marks 110 B/S edges.

The final roots `ol` and `od` form an even cleaner binary switch. Expanded
words with the same non-empty canonical base X and the same final BARE slot
differ only in the chosen root. Across all six panels:

> **`X + ol` -> [BATHING-SIDE STATE/CLASS OF X]**  
> **`X + od` -> [HERBAL-SIDE STATE/CLASS OF X]**

ZL odd/even herbal-oriented odds are 45.39 and 113.24; exact p-values are
2.3e-9 and 3.8e-6. A maximally permissive control lets each of 69 synthetic
manuscripts search every supported ending pair and direction; none survives
its odd-to-even challenge. Bases `ar`, `che`, and `e` carry both values in
every transcription/parity panel. This translates a binary class/state choice,
not `ol=water` or `od=plant`.

## 7. Complete manuscript-wide interlinear

The current evidence has been merged token-for-token over the complete ZL
transcription. The export contains all 38,988 tokens; 35,060 ordinary-prose
tokens retain the full structural parse, 9,255 tokens carry at least one
supported relational or local-semantic tag, and 935 lines carry a specific
star-entry, lunar-record, fan, or zodiac-passage reading.

The readable version is
`experiments/semantic_assumptions/results/complete_first_translation_v018.txt`;
the auditable token table is
`experiments/semantic_assumptions/results/complete_first_translation_v018.tsv`.
Every unknown English lexeme is printed as `LEX=?`, so the export cannot be
mistaken for a substitution plaintext.

An exact 10!-assignment attempt to extend the zodiac result from four states
to a smooth annual coordinate was rejected after generated-text calibration.
The raw signal was writing-order drift; after subtracting the 69-control mean,
the family p-value is .722. The ten four-state passage readings above therefore
remain the maximal supported zodiac translation.

## Current hard boundary

This is a real first translation of local functions, semantic classes,
line-order relations, and a technical-core entry template. It does **not** yet
translate ordinary prose into lexical English. Supplying nouns, verbs, or the
remainder of the f67r2 clause would still be fabrication.
