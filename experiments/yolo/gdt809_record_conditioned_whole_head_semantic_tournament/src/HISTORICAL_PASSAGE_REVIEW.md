# GDT809 historical passage review: properties are not preparation instructions

Status: exploratory comparison, not a translation or a new relation gate.
Review date: 2026-09-05.

## Result and inherited/new boundary

The most useful concrete distinction is between **dry as a described quality**
and **dried as a resulting material state**. They are not interchangeable
English renderings. In the recurrent `chor chol daiin`, the first gives the
hypothesis “flowers: dry in degree III”; the second permits “dried flowers:
three portions.” The manuscript tokens do not themselves supply the English
copula, colon, participle, measurement unit or attachment relation.

Neither repetition of this three-token expression nor the degree/amount
ambiguity is new. GDT629 already documented its two exact occurrences and
the portion rival; GDT686 rejected a universal degree or amount axis and
documented repeated value-like forms. GDT759 inherited the expression while
sometimes displaying `getrocknet`; GDT768 supplied the concrete flower/fruit
defaults but left their reversal tied. This review adds a **joint, full-paragraph
assumption audit** to GDT809. It must not be reported as a fresh discovery of
the same phrase, a newly found numerical system, or a reopened universal-axis
experiment.

GDT625's visible leaves are page/entry context, not a demonstrated `cthy`
word-to-object owner. Consequently `cthy=Blattgut` remains an assumed useful
reading against aerial herb and other material-name rivals. Neither botanical
coherence nor a historical Latin parallel identifies a Voynich word or language.

## Sources and exact scope

Read primary reports through the experiment index: GDT625, GDT629, GDT686,
GDT735, GDT755, GDT759 and GDT768. GDT735's historical entry observations,
GDT755's source/expression bank, and GDT768's whole-word/default specifications
supply inherited hypotheses, not independent lexical corroborations of them.

The four page selectors were first confirmed in GDT631's 179-selector
`PAGE_ALLOWLIST.tsv`. Cached transcription and alternate readings were then
queried with selector-before-retention guards. No new Voynich image, page or
transcription was acquired. The initial comma-joined allow argument selected
zero rows; the corrected explicit allow arguments selected the four requested
pages before any transcription was inspected.

```sh
./vmanus-exp query-tsv experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv --selector page --allow f17r --allow f21r --allow f32v --allow f29v --columns page
./vmanus-exp query-tsv transcription/voynich_zl3b_lines.tsv --selector page --allow f17r --allow f21r --allow f32v --allow f29v --columns page,locus,line_number,paragraph_start,paragraph_end,token_count,eva_clean --forbid-prefix f84 --forbid-prefix f84r
./vmanus-exp query-tsv transcription/voynich_cross_transcription_lines.tsv --selector page --allow f17r --allow f21r --allow f32v --allow f29v --columns page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean --forbid-prefix f84 --forbid-prefix f84r
```

The page query selected 48 already admitted lines. The paragraph flags delimit
the following four review units, comprising all 17 physical lines quoted here.
These are exact **ZL3b** quotations; they are not all reader-exact lines.
ZL3b, IT2a and RF1b are alternative transcriptions of one manuscript.

### P1: f17r.4–6

```text
f17r.4  tcho shol qokol qor olaiin opydg som ypchy ypaim
f17r.5  ychekchy cthy chor shor cphor cphaldy dair cthey qody
f17r.6  tsho qof cho qokcheor cheteg
```

### P2: f21r.8–12

```text
f21r.8   fcho kshy otor sheol ocphal opsheas cthodaiin oty
f21r.9   okaiin sho tshaiin chkaiin sh cthey cthody cthy s
f21r.10  totchy keor chy ky qotaiin qotchol ty ctheey otaiin
f21r.11  shol chol shol tchol chcthy otyky shey yteol shody
f21r.12  ykeey chor sheey ysheol chor chol daiin chkaiin
```

### P3: f32v.7–11

```text
f32v.7   ksho cphos she sheaiin otshcho r dain shckhy s odan
f32v.8   otchol daiin daiin ctho daiin qotaiin otchy d shan
f32v.9   qotchy cfhy skey chocthy daiin cthaiin daiin
f32v.10  sho keol chor chol daiin cpho l cthol da ar
f32v.11  ol sho chy
```

### P4: f29v.1–4

```text
f29v.1  kooiin shor chetchy ol ls shytchy cthy shy cho shy daiin
f29v.2  qotcheaiin s chol chol cthy chey cthold ytchor dary
f29v.3  chol chol kor shey odaiin qotchy taiin s she otey sy
f29v.4  ysho otshy okaiin cthy oltchy s shot sho okaiin
```

Agreement matters at the actual comparison span:

- P1's entire middle line f17r.5 is exact across the three readers.
- `chor chol daiin` is exact in P2 and P3, but neither containing full line
  is identical across all three readings.
- P3's adjacent `daiin daiin` survives all readers. Its later `ctho daiin`
  is `cthodaiin` in RF1b; do not count an invariant third separate word there.
- P4's f29v.3 begins `chol chol` in all readers. In f29v.2 IT2a has
  `schol chol`, against ZL3b/RF1b `s chol chol`; the two repetition cases
  therefore have different boundary robustness.
- P2's f21r.9 `sh cthey` is `shcthey` in IT2a. This does not authorize a
  free meaning for `sh` or a substring meaning in `cthey`.

## Fourteen complete-word assumptions shared by the two readers

D is a descriptive materia/quality reading. R is an ingredient/amount
counter-reading, not an endorsed recipe. Question marks apply to semantic
identity even when the exact EVA spelling is secure. These cards are scoped
to this exploratory comparison; they do not replace the main dictionary.

| Exact whole | D display | R display | Inherited source and strongest counterevidence |
|---|---|---|---|
| `cthy` | Blattgut? | Blattzutat? | GDT625/768: Herbal concentration and parallel whole-form contacts; aerial herb survives, and page leaves are not a token owner. |
| `chor` | Blütenstand? | Blütenzutat? | GDT768: nominal parallel-role lead; flower versus fruit/seed direction tied. |
| `shor` | Fruchtstand? | Fruchtzutat? | GDT768: paired nominal-role lead; reversed flower reading equally viable, and fruit is not identical to seed. |
| `chol` | trocken, als Eigenschaft? | getrocknet, als Zustand? | GDT629/759: recurrent whole/span hypothesis; R adds a prior processing assumption not supplied by an attested operation. |
| `daiin` | Grad III? | drei Portionen? | GDT629/686: inherited degree/amount rivals; quantity, degree, ordinal class and attachment are not established lexemes, and adjacent repetitions require a grammar. |
| `dair` | Anteil II? | Anteil II? | GDT768: measured-whole working card; no global root identity and no free `air` export. |
| `okaiin` | Zubereitung? | Zubereitung? | GDT625 low-confidence carrier hypothesis; repeated spelling does not establish one physical batch. |
| `otshy` | kalt-feucht? | kalt-feucht? | GDT625 inherited whole quality axis; retain unknown orientation and technical-class rival, and add no soaking verb. |
| `oltchy` | kalt-trocken? | kalt-trocken? | GDT625 inherited whole quality axis; add neither a drying operation nor a reached endpoint. |
| `s` | je? | je? | GDT759 context dispatch: final f21r.9 may be “zu gleichen Teilen?”; none here is an exact `s` plus `ain/aiin/aiiin` quantity span. No automatic drachm. |
| `ar` | Anteil? | Anteil? | GDT759 quantity-head candidate; bare final `ar` at f32v.10 contains no licensed number or specific unit. |
| `kooiin` | Wurzelstockdroge? | Wurzelstockzutat? | GDT625/768 old two-host lead; general Herbal entry/class head survives, and visible rootstock does not identify the word. |
| `cthey` | Droge Form I? | Droge Form I? | GDT768 f17r.5 exact-whole candidate, with preparation-form rival; does not inherit leaf from `cthy`. |
| `qody` | fertige Zubereitung? | fertige Zubereitung? | GDT768 f17r.5 nominal-result card; a closure marker remains a rival, with no imperative to finish. |

All 14 meanings remain assumptions. The common frame is intentionally stable
between paragraphs. The only substantive D/R switch is quality versus processed
state, coupled to degree versus portion. Swapping `chor` and `shor` gives a
third equally coherent concrete identity reading without changing any written
syntax: “fruit” replaces “flower” and vice versa everywhere. GDT768 already
showed why that swap remains unselected.

Do not add GDT768's `ychekchy=Ansatzposten`, `cphor=Dosisposten` or
`cphaldy=fertiger Anteil I` merely to make P1 fluent: their source explicitly
labels them `C0_MANUAL_SLOT_FILL`. They remain visible EVA here. The shared
deck likewise does not derive meanings for `cthody`, `cthodaiin`, `cthaiin`,
`chocthy`, `chcthy`, `qotchol`, `otchol`, `tchol` or `ysheol` by substring.

## What each complete passage actually permits

The following is interpretation of the complete units, not a replacement for
the exact lines above. All connecting relations in square brackets are supplied
by the model; they are not translated manuscript words. Unrendered spans must
stay visible in the companion token-aligned reader.

**P1, nominal inventory versus ingredient inventory.** Under D, its middle
line lists leaf material, flowers and fruit [as three parallel parts], followed
by `cphor cphaldy`, portion II, drug form I and prepared material. Under R,
these are leaf, flower and fruit ingredients [for one preparation], followed
by the same unknown span and nominal preparation fields. Both are coherent
inventory hypotheses; neither justifies “take,” “mix,” or a causal link to
the opaque first and third lines. The exact three consecutive words constrain
a reading more than a one-word image association, but do not identify the
three listed objects. The flower/fruit reversal costs nothing syntactically.

**P2, property notice versus preparation notice.** Under D, its final line
has `[ykeey] flowers [sheey ysheol]; flowers: dry in degree III [chkaiin]`.
Under R, the same line becomes `[ykeey] flower ingredient [sheey ysheol];
dried flowers: three portions [chkaiin]`. Calling the second `chor` “the same
flowers” requires an anaphoric rule. The preceding `cthy s` can provisionally
close a leaf-material/equal-parts item, but that choice does not turn the
entire paragraph into a recipe. In particular, `shol chol shol tchol` is an
unresolved repeated pattern, not a licence to narrate a wet-to-dry process.

**P3, repeated numerical fields versus repeated doses.** The final long line
contains the same D/R alternatives for `chor chol daiin`, with identical
surrounding opaque spans. D displays the two adjacent values in f32v.8 as
`Grad III?; Grad III?`; R displays `drei Portionen?; drei Portionen?`.
Neither is an adequate sentence without an additional repeated-field,
ellipsis, numbering or copying rule. The two later `... daiin ... daiin`
positions in f32v.9 expose the same debt. Do not silently attach every value
to an invented ingredient, and do not claim that the paragraph's short
final `ol sho chy` supplies a known completion verb.

**P4, different organ properties versus one material's treatment.** D can
read the last line as `[ysho]; cold-moist preparation; leaf material:
cold-dry; [s shot sho]; preparation`. It may be a contrast between parts
or preparations, but “this plant has two kinds of part” is supplied by D.
R can try `[ysho]; cold-moist preparation; leaf ingredient, cold-dry;
[s shot sho]; preparation` and hypothesize that one preparation is resumed
after intervening material. This still says neither “put into” nor “then dry.”
The exact repeated `okaiin` makes a same-carrier reading worth retaining,
but does not establish its referent. Both D and R must explain `chol chol`
in the earlier lines. Treating the duplication as two separately described
entries, intensification, an omitted noun, or scribal repetition is a new
grammatical assumption, not evidence already contained in “dry.”

## Historical syntax that can discriminate the models

The following sources were opened for historical comparison only. They add no
Voynich material. Short quotations preserve source spelling; surrounding
descriptions are paraphrases, and all target-language connections are inferences.

**H1 — description is not an operation.** The early-fifteenth-century
Wellcome MS.542 catalogue transcribes wood and herb materia entries with
paired qualities and a degree; the hellebore entry also has
`Radix ponitur in medicinis`. That is an explicit use statement distinct from
its quality field. The same manuscript contains practical recipe sequences.
This supports separating nominal part, property and use/process predicates;
it does not make `chol` a quality word. For D, an independently recognized
quality-degree field would be useful. For R, a preparation verb or a separately
identified dosage field would be useful. Mere co-occurrence with plant material
fits both. [Wellcome MS.542, contents 7 and 11](https://wellcomecollection.org/works/n674z2xd).

**H2 — ingredient grammar carries actual attachments.** Durham MS B.III.12,
f83v, has ingredient-and-weight sequences, a butter-oil preparation with
cooling and result clauses, and the short leaf phrase
`Accipe folia petrofilli virid’`. An actual recipe can specify the plant whose
leaves are meant, their freshness, and an operation; plant-part words alone
do not supply those relations. Thus an R reading should eventually identify
repeated name/part attachment, amount binding and operation/result behavior.
These are useful discriminators, not a requirement that every abbreviated
recipe spell every slot out. The excerpts are a catalogue transcription of
fourteenth/fifteenth-century material, not a new diplomatic collation.
[Durham catalogue, recipe notices 1, 2 and 6](https://reed.dur.ac.uk/xtf/view?docId=ark/32150_s18623hx81c.xml).

**H3 — repeated carrier and genuine process can coexist.** The published
fourteenth-century ink recipe from BnF lat.8651 f88v repeatedly refers back
to water while separately instructing boiling, straining and returning it to
the fire. Its anaphoric devices include `dictam aquam`, `aqua predicta` and
`eam`; sequencing also uses `deinde` and `iterum`. Therefore repeated
`okaiin` in P4 is compatible with process anaphora as well as parallel
descriptive fields. A process reading needs an independently defensible
reference chain and operation sequence, not just two assumed moisture values.
The comparator is a technical ink recipe, not evidence that the Voynich
paragraph concerns ink or water.
[Published primary-text transcription, p. 484](https://www.persee.fr/doc/bec_0373-6237_1925_num_86_1_460583).

**H4 — formula recurrence does not establish a function word.** The original
aligned-corpus study of John of Burgundy witnesses finds abbreviation
consistency depends on language, text type, word length and frequent lexical
items. Its corpus is later, approximately 1450s–1490s. Consequently repeated
short Voynich forms might represent stable technical formulae or lexical
wholes as well as grammar. Frequency and compactness cannot choose a Latin
function word, numeral or medical unit. This is a research comparator rather
than a period manuscript witness, and no graphic match has been inspected.
The article abstract was accessible; subsequent detailed-table requests failed,
so this review makes no new table-level frequency claim.
[Honkapohja and Suomela, original aligned-corpus research](https://academic.oup.com/dsh/article/37/3/765/6401180).

The previously observed Pal.lat.1234 part rubrics in GDT735 are inherited
architectural support for named parallel parts. The viewer was opened but no
new manuscript image was inspected, and this review does not claim a new
rubric reading from it. Historical `flos`, `fructus`, `semen`, `folia` and
`radix` are comparison vocabulary only. None supplies an EVA letter value.

## Strongest rival and decision ceiling

The strongest broad rival is a compressed record or learned-name system whose
recurrent cells do not yet have identified English meanings. A conjunction-only
replacement such as `daiin=and` is not a free improvement: it must account for
the already studied value-family and adjacent repetition behavior. Conversely,
“ditto,” an abbreviation, an inflection or a record delimiter cannot be selected
just because it conveniently absorbs a difficult repeated token.

At this scope no D/R winner is established. Two exact copies of a phrase
show reuse, not which historical expression it encodes. The genuinely useful
deliverable is a small common assumption dictionary, full paragraph coverage,
visible unknowns, reader-sensitive repetition checks, and an explicit account
of the grammar each concrete interpretation still owes. Dry property,
processed-dry state and the imperative “dry it” must remain three separate
claims. Confirmed lexemes, plaintext clauses and new component exports: zero.
