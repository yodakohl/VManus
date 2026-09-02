# GDT738 method

## Question

Can the 120 held body candidates from GDT737 support concrete readings for
complete observed headed forms when exact whole evidence, independent local
neighbours and the observed record position are required together, and when a
late-medieval pharmaceutical microentry is used only as an architecture prior?

## Inputs and boundary

The target is fixed by GDT737: 120 bodies, 273 observed headed surfaces and 811
cached occurrences. No new page, image or transcription is opened. The
builder reads the published GDT737 occurrence table, body candidate deck and
form bridge. It reconstructs adjacent cached tokens with the same guarded
allow-list code and joins their exact GDT734 compact cells by locus and token
ordinal. GDT736 supplies the training siblings; GDT737 supplies held siblings.
GDT735 and the checked institutional sources in
`src/HISTORICAL_MODEL_SPECS.tsv` supply historical architecture only.

ZL3b, IT2a and RF1b are alternate readings of one manuscript. Reader agreement
is therefore a transcription-stability gate, not independent witness support.

## Historical bridge: typed pharmaceutical microentries

The selected bridge is not an initial-letter dictionary. It is a record model:

```text
learned complete lemma or rubric
    + locally bound quality/state/degree field
    OR
    + locally bound amount/unit/process/result field
```

The comparison material is kept in two evidence decks.

### Descriptive deck

Period witnesses such as Vatican Pal.lat.1234 and Wellcome MS.542 place learned
drug or substance wholes under rubrics or beside part, quality and degree
fields. Wellcome MS.624 and MS.626 independently show large alphabetical
repertoires of learned simples; MS.626 also places recipes and a glossary in
the same codex. Wellcome MS.712 demonstrates that one lemma can carry different
degrees on different quality axes.

This deck licenses only the architecture `WHOLE + BOUND DESCRIPTOR`. It does
not license a drug name, plant part, hot/dry value, numeral or target sign.

### Prescriptive deck

Wellcome MSS.307, 683 and 327 exhibit recipe or ingredient wholes beside
`ana`, units, values and named product forms. Wellcome MS.534 distinguishes
numbered procedural passages or distillations. The medical abbreviation corpus
confirms that technical abbreviations, units and learned words can coexist and
that an expansion may depend on its lexical and scribal context.

This deck licenses only the architecture `WHOLE + BOUND AMOUNT/PROCESS FIELD`.
It does not identify a Voynich unit, number, operation or attachment direction.

The two decks are complementary architectural comparators, not two votes for a
Voynich reading. Every historical model has zero Voynich relation credit.

## Method

### 1. Formal occurrence deck

The 811 target occurrences expose 1,266 immediately adjacent left/right
slots. A slot enters the formal deck only when target and neighbour are exact
in all three alternate readings. A multi-character neighbour whose first EVA
transcription character is `p`, `s`, `r` or `l` is then excluded as another
formal head-like surface; `sh…` is explicitly not treated as an `s…` head.
This creates **FORMAL705**, containing 705 slots from 520 target occurrences,
109 bodies and 182 complete forms.

The exclusion is formal rather than phonetic or semantic. EVA initials still
carry no historical letter value. Each retained slot records side, exact
surface and `(section, cached-language)` register.

### 2. Broad and clean semantic decks

Each formal neighbour is joined to its GDT734 compact cell by exact
`(locus, token_ordinal)`. It enters **SEM570** when `unknown_v99r7=0` and its
German renderer contains none of the retired literal patient words powder,
seed, root or wood. SEM570 contains 570 slots from 444 target occurrences, 105
bodies and 162 forms. It is deliberately a discovery deck: 356 slots inherit
an ungraded renderer and therefore cannot by themselves license execution.

The clean **W23-AXIS195** deck additionally requires GDT734 confidence W2 or
W3, zero composition-semantic credit and at least one controlled axis. The
ordered, multi-label axes are HEAT, COLD, DRY, MOIST, VALUE, PART, MATERIAL,
PREPARATION, CLOSE and PROCESS; a cell matching none receives `OTHER` and is
not part of W23-AXIS195. The clean deck contains 195 slots from 178 target
occurrences, 71 bodies and 89 forms.

Neighbour meanings remain contextual support. They never turn the target body
or any of its substrings into a free suffix or lexeme.

### 3. Direct recurrence

For each body and evidence deck, direct support is accumulated as follows:

- two points when one exact neighbour surface occurs under at least two heads;
- one further point when such a surface also recurs on the same side and in
  the same section/language register;
- one point when one semantic-axis fingerprint occurs under at least two
  heads;
- one further point when that fingerprint also recurs on the same side and in
  the same register;
- one point when one section/language register contains at least two heads.

The maximum direct score is six. `SUPPORTED_CROSS_HEAD` requires score at
least four, at least four reader-exact target occurrences and at least two
reader-exact occurrences for every head participating in the decisive repeat.

### 4. Predeclared family transfer

Ten analogy families are enumerated before selection: the scalar `ain`
ladder, two heat/state ladders, dry and moist result ladders, preparation,
part, dry-part, material and preparation-result families. GDT736 members are
training siblings and GDT737 members held siblings. A sibling is comparable
only with at least five formal slots and three semantic slots.

Three cosine profiles are calculated:

- **F:** exact neighbour-surface counts on FORMAL705;
- **A:** multi-label semantic-axis counts on SEM570 or W23-AXIS195;
- **R:** `(section, cached-language)` counts on FORMAL705.

The best sibling is chosen deterministically by passed gates, total cosine,
then F, A, R and fixed family/member order. A strong family pass requires
`F >= .15`, `A >= .80` and `R >= .70`. `SUPPORTED_FAMILY_ONLY` additionally
requires at least four exact target occurrences and four formal slots.
High-capacity candidates with at least five exact occurrences, eight formal
slots, at most one family point and direct score at most one are marked
`CONTRADICTED_FAMILY_TRANSFER`; all other bodies remain undecidable. A separate
capacity/position/confidence score ranks rows but cannot override these rules.

### 5. Complete-form and position gates

A Discovery form needs a supported SEM570 body, at least two exact occurrences
of the full surface and at least two FORMAL705 slots. The executable decision
repeats that rule with the body's W23 decision. H1/H2 are expected line-first;
H3/H4 are expected middle/final. A surviving form with at least half its exact
occurrences outside that role is explicitly labeled a learned exact-whole
position exception rather than forced through the head template.

Every admitted output is an enumerated complete surface with an explicit
position scope. Missing combinations are not predicted. Manual cards supply
short German realizations and counterevidence only after the quantitative form
decision; they do not choose the surviving list.

### 6. Stress cases and literal-material correction

`sary`, `so`, `skaiin`, `lcheol`, `lchor` and `lsheody` receive a manual
full-line audit because GDT737 identified them as structural counterexamples.
Temperature, consistency, amount, degree and process passage remain competing
dimensions until a local host selects one.

The two provisionally retained GDT737 salt cards are re-audited rather than
treated as truth. Literal salt/species language requires independent salt
evidence; mere absence of the four retired head-patient words is insufficient.

### 7. Exploratory versus executable whole decks

The broad deck contains 17 scoped complete-whole candidates. It preserves
rivals and counterevidence and may be used for manual comparison. Execution is
restricted to the final quantitative W23 subset of 12 cards:

`lain`, `lcheedy`, `lcheol`, `lkaiin`, `lkain`, `lkar`, `lsheedy`, `pcheol`,
`rain`, `rsheedy`, `sain`, `skaiin`.

The five cards `lcheor`, `lkeey`, `lkey`, `lky` and `pcheor` remain
`DISCOVERY_ONLY` with zero executable renderer credit. Confidence alone is not
an execution gate: a `MEDIUM` card is not automatically discovery-only, and a
higher-confidence card does not bypass the quantitative W23 decision. This
split remains additional to the exact-occurrence and position gates and does
not convert confidence into plaintext evidence.

## Decision rule and claim ceiling

Outputs distinguish supported complete-whole candidates, learned position
exceptions, holds and unknowns. An executable card may render only its listed
complete surface at its listed eligible occurrence. It receives zero
free-component credit, predicts no unseen form, and creates no universal head
or body meaning.

GDT738 may select concrete state-, value-, part- or procedure-oriented working
readings for complete observed wholes, downgrade inherited whole cards, and
rank unresolved candidates. It cannot identify plaintext, language, sound,
physical glyph expansion, Latin initial, ingredient, species, disease, cure,
unit or universally portable stem.
