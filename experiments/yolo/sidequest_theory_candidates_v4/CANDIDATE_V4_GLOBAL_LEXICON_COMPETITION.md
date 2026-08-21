# V4 global lexicon competition

Date: 2026-08-21

Status: **speculative sidequest analysis, not a translation and not a GDT
result**. Confirmed English lexemes: **0**. Confirmed plaintext clauses: **0**.

## Scope and evidence discipline

This pass compares three compact lexicons against **every occurrence** of the
five nominated exact cards on the seven fixed prose pages. The three fixed
circle pages have no GDT327 events and therefore contribute only to the
cross-register plausibility judgment; they receive no imported prose-card
glosses. No additional page was admitted. `f84` and `f84r` remained sealed.

The source slice was obtained only through guarded `query-tsv`, with the exact
allow-list `f10r f11r f55v f56r f81v f82r f83r` and
`--forbid-prefix f84`. It returned 381 events and skipped 8,067. ZL3b, IT2a
and RF1b are not counted as independent witnesses.

All labels below are **structural expansion classes**. They are not claims that
a card means the printed English word.

## Frozen all-occurrence census

`F/M/L/S` mean first, middle, last, or sole card in its field.

| exact card | all occurrences by page | field position |
|---|---|---|
| `qokaiin` (`b5fcea...`) | 9: f55v 1, f81v 1, f82r 3, f83r 4 | F 7, M 1, L 1 |
| L/O (`dcda95...`) | 19: f10r 3, f81v 9, f83r 7 | F 3, M 14, L 1, S 1 |
| AIIN (`2f1c5e...`) | 20: f10r 3, f11r 1, f55v 3, f56r 2, f81v 2, f82r 2, f83r 7 | F 6, M 9, L 5 |
| Y (`b921a2...`) | 18: f10r 5, f11r 3, f55v 1, f81v 1, f82r 2, f83r 6 | F 2, M 13, L 3 |
| CTHY (`e0b630...`) | 7: f10r 2, f11r 1, f83r 4 | F 0, M 6, L 1 |

The five cards total 73 events. There are eleven uninterrupted runs of two or
more nominated cards, covering 25 events:

```text
f10r.5   L C
f10r.6   Y Y A Y
f10r.8   L A
f11r.4   Y A
f11r.7   C Y
f55v.5   Q A
f81v.18  Y L
f82r.23  A Y
f83r.3   Y A Y
f83r.14  Q C
f83r.54  A L
```

Here `Q/L/A/Y/C` are card identifiers, not initials of translated words.

The terminal census remains formally stronger than any lexical proposal:
90/90 already identified attached terminal events realize a local close. The
guarded slice contains one positive B3 event; under the frozen two-realization
description, the other 89 closes are DY-bearing. Exact terminal-card identity
is retained as payload. No terminal family is equated with punctuation, and no
family is assigned RESULT, LOCATION, PREPARATION or another English value.

## Competing frozen lexicons

### Model A — typed practical form (current model)

| card/family | one role used globally |
|---|---|
| `qokaiin` | ENTRY / reactivated ADDRESS HEAD |
| L/O | RELATION / co-member LINK |
| AIIN | PARAMETER / degree / index / reference slot |
| Y | ITEM-TAG / POINTER slot |
| CTHY | PROPERTY / CONFIGURATION STATE |
| terminal families | exact PAYLOAD + formal COMMIT realization |

This model deliberately refuses the narrower expansions TAKE, WITH, AMOUNT,
OBJECT and PREPARED. They would fail more occurrences than the broad roles.

All-occurrence forcing:

- `qokaiin`: seven initial cases are direct fits. The single medial case can
  reactivate an address. The f82r.3 final case is acceptable only as the local
  anticipatory copy whose identical card reappears at f82r.4 entry. Counting
  the pair twice costs one exceptional placement; collapsing the carry to one
  logical head removes it. This repair is licensed only for that exact local
  transition.
- L/O: fourteen medial cases fit a binary or list relation. Three initial, one
  final and one sole case force RELATION to include a unary/open relation or
  relation-field use; they reject a single literal conjunction or
  preposition.
- AIIN: all twenty fit only at the broad parameter/reference level. Six first
  and five last occurrences reject a narrowly medial dose or amount marker.
- Y: all eighteen can be item/tag/pointer slots. Its thirteen medial cases are
  strongest; two initial and three final cases prevent a fixed left- or
  right-pointer direction.
- CTHY: six medial and one final case fit a state/qualifier slot without a role
  switch. Nothing identifies which state.
- terminals: all ninety keep the same formal COMMIT operation while exact card
  identity carries unknown payload. No semantic family switch is needed.

### Model B — working-medium/process recipe

| card/family | one role attempted globally |
|---|---|
| `qokaiin` | WORKING MEDIUM / liquid matrix |
| L/O | COMBINE / IN-WITH process relation |
| AIIN | DOSE / DEGREE of treatment |
| Y | PORTION / station or treated item |
| CTHY | TREATED / prepared process state |
| terminal families | resulting preparation + process completion |

All-occurrence forcing:

- `qokaiin`: a medium can lead an ingredient phrase, but 7/9 field-initial
  occurrences make it behave like a repeated topic or instruction head rather
  than ordinary material. The f82r final-to-initial repeat can denote
  continuous material, but that explanation is selected from layout and has
  no independently owned liquid referent. The model must alternate between
  MEDIUM as content and MEDIUM as discourse header.
- L/O: fourteen internal cases allow IN/WITH-like expansion, but three first,
  one last and one sole occurrence require an imperative process, elliptical
  complement, or bare process heading. That is a material role switch.
- AIIN: DOSE/DEGREE is possible in the nine medial cases but strained in six
  first and five last cases unless omitted units and operands are supplied.
  The two `Y-AIIN-Y` contexts do not independently establish equal portions.
- Y and CTHY remain possible at their broadest levels, but PORTION and TREATED
  require unobserved recipe entities/actions. `C-Y`, `Y-L` and final Y are not
  continuously readable without ellipsis.
- assigning different terminal families to different results overreads the
  evidence. Retreating to unknown payload + completion simply imports Model
  A's terminal analysis.

The rival therefore survives as a page-level subject hypothesis, especially
for Biological material, but it is not the best global card dictionary.

### Model C — indexed workshop checklist (new rival)

| card/family | one role used globally |
|---|---|
| `qokaiin` | RECORD KEY / mode selector |
| L/O | CROSS-REFERENCE / list edge |
| AIIN | INDEX / coordinate / value slot |
| Y | CHECKPOINT / labelled node |
| CTHY | CLASS / status flag |
| terminal families | exact cell value + VALIDATION SEAL |

This is not a medical-content model. It treats the pages as an illustrated
inventory, routing sheet or exemplar checklist whose cards primarily locate
and validate entries.

All-occurrence forcing:

- `qokaiin`: seven initial keys fit directly; the medial case is a nested key;
  the f82r final/initial pair is a forward key copied at the new line. This is
  the cleanest positional account of the three models.
- L/O: an edge/reference can be internal, initial, final or sole, so all 19
  cases fit without changing category. Direction remains unspecified.
- AIIN, Y and CTHY are all positionally mobile enough for value, node and flag
  slots. `Y-AIIN-Y` becomes NODE–INDEX–NODE, and all eleven consecutive runs
  admit compact formal parses.
- exact terminals can carry a cell value while DY/B3 supplies a validation
  realization, again with no family-specific English semantics.

Its weakness is explanatory rather than positional. It redescribes the card
layout elegantly but does not explain why an expensive illustrated practical
codex would encode a content-light checklist, nor why Herbal, bathing/apparatus
and astronomical iconography should be selected. Astro could be a local lookup
array, but the prose cards cannot be imported there to prove the proposal.

## Scoring

Each axis is scored out of 25. On the first axis a high score means **low**
semantic role-switch cost. Consecutive coverage asks whether all eleven
nominated-card runs can be paraphrased without changing the frozen roles or
silently inserting arguments. These are transparent comparative judgments,
not statistical estimates.

| model | low role-switch cost | positional fit | cross-register plausibility | consecutive coverage | total |
|---|---:|---:|---:|---:|---:|
| A typed practical form | 22 | 22 | 23 | 23 | **90** |
| C indexed checklist | **24** | **24** | 17 | **24** | 89 |
| B medium/process recipe | 14 | 17 | 19 | 16 | 66 |

### Decision

**Model A wins narrowly.** Model C is the better description of pure
distribution, so V4 does not strengthen literal medical vocabulary. Model A
wins because it preserves nearly the same formal economy while explaining the
fixed illustrated registers as content-bearing practical forms. The result is
a sharper split:

```text
supported formal layer:
  KEY/ENTRY-like Q + mobile LINK/VALUE/NODE/STATE slots
  + exact terminal payload under COMMIT

preferred but unproved content layer:
  practical medical dossier/form, with Astro as a separate lookup annex

live adversary:
  content-light indexed workshop checklist
```

The competition weakens `qokaiin = TAKE/USE`, `L/O = WITH`, `AIIN = AMOUNT`,
`Y = ITEM` and `CTHY = PREPARED` as literal expansions. It strengthens only the
broader structural classes.

## Most concrete permissible pseudo-translation

The cleanest longer passage is f83r.3 because it contains the repeated
`Y-AIIN-Y` frame, a terminal, and a following `qokaiin` head. Keeping every
unidentified card visible:

```text
f83r.3
  [opaque committed cell]
| [opaque — opaque]
| POINTER/ITEM — PARAMETER/REFERENCE — POINTER/ITEM
    — [exact unknown payload + COMMIT]
| ENTRY/ADDRESS HEAD — [opaque — opaque]
```

Maximum source-class paraphrase:

> Within the pictured dossier, close the first local cell; retain the next
> opaque pair; register two marked slots under one parameter or reference and
> commit that exact cell; then open the next addressed entry with two unknown
> specifications.

Provenance: “pictured dossier” is inherited page/register context; ENTRY,
POINTER, PARAMETER and COMMIT are formal card-role hypotheses; “register,”
“under” and “specifications” are speculative connective expansions. No
substance, action, body part, quantity, direction, disease, result or ordinary
source wording is supplied.

The f82r.3–4 boundary can be stated still more securely, but less
semantically:

```text
[opaque field] | [opaque sequence] — Q(carry)
line break
Q(entry) — [opaque sequence] | [opaque field]
```

This licenses “copied active head across available line space” as a local
layout parse, not RESUME, WATER, APPLY or any plaintext word.

## Falsifiers for a next pass

- Model A loses its lexical advantage if a matched frequent-card baseline
  shows that 7/9 entry behavior and right-context diversity are ordinary.
- Model B rises only with an independently owned medium/process referent; more
  fluent recipe wording is not evidence.
- Model C rises if exact terminal identity or the `Q/L/A/Y/C` roles predict
  repeated labelled positions inside an already owned fixed-page visual
  homologue. It loses if the apparent keys/edges do not recur by visual role.
- Any narrow terminal dictionary is withdrawn unless exact closer identity
  predicts preceding construction class after page and field length are held
  fixed.
