# V78 R4 — continuous chancery edition under `ET?` and `PER?`

## Result

`BOTH_MINI_WORDS_SURVIVE_ONE_CONTINUOUS_PASS__TWO_STRAINED_OCCURRENCES`

All 381 prose events are now assigned exactly once to 116 continuous working
statements and eleven complete records. Physical lines never terminate a
sentence automatically. Every concrete noun and action remains inside an
`[EXEMPLAR:…]` bracket. The only printed word candidates are the two V77
entries:

- `ET?` at 19/19 exact occurrences;
- `PER?` at 9/9 exact occurrences.

No third word, stem, sound, PAGE_HOST value or language label was introduced.

## Literal reading contract

```text
dcda…     -> [WORTKANDIDAT:ET?]  -> und/auch? [EXEMPLAR:local content]
b5fcea…   -> [WORTKANDIDAT:PER?] -> durch/gemäß? [EXEMPLAR:local content]
formal    -> [FORMAL:...; KEIN WORT] [EXEMPLAR:local content]
all else  -> [OPAQUE_KARTE:id] [EXEMPLAR:local content]
```

This keeps the exact card order separate from the readable expansion. A
fluent sentence is therefore a proposed reconstruction of the absent master
exemplar, not a claim that the bracketed German is encoded word for word.

## Pressure test of the two words

### `ET?`

Of 19 occurrences:

- 14 are good medial additive links;
- 3 are acceptable field-initial “auch/weiter”-type resumptions;
- 1 is an acceptable field-final open addition/carry;
- 1 is strained: the card is the whole one-card field f81v F024.

The singleton does not make `ET?` impossible—a short “auch/weiter” cell or a
nonlexical continuation mark can explain it—but it is the strongest objection.
The formal rival remains an additive link/continuation sign with no spoken
word.

### `PER?`

Of nine occurrences:

- 7 are good field-initial relation/instruction heads;
- 1 is a good physical-line-edge catchword followed by the same card at the
  beginning of the continuing statement;
- 1 is strained: f82r E219 is medial immediately before a terminal card.

That last context can still read “gemäß [der örtlichen Vorschrift]”, but the
formal rival—an entry or standard-slot prompt—is at least as economical.

No occurrence forces a second lexical sense. Both candidates therefore remain
for one more round, with `ET?` stronger than `PER?`.

## Eleven complete records

The selected content expansions remain those already fixed by V73–V74, now
placed behind a strict bracket firewall:

- H1: unidentified pictured plant; root-like portion, cleaning, water-like
  extraction, small use amount and storage.
- H2: two collection fractions, pressing, oil-like medium, combining, soft
  preparation and external use.
- H3: early plant fraction, wine-like extraction, repeated filtration and a
  second retained preparation.
- H4: broad-leaf preparation, clarification, local wash and warm poultice-like
  use.
- H5: fresh sticky-plant topical use plus a dried wine/honey-like extract.
- B1: one shared two-row pool field with local measuring, washing, resting and
  closing operations.
- B2: upper pair, middle device, unresolved middle station, lower pool and
  edge stations; every visible owner change resets substance and direction.
- B3: three short stations, an unresolved interval and then a genuinely linked
  pair.
- B4: the linked pair followed by separate left and right stations with no
  connecting edge.
- B5: a small left end-station record.
- B6: an independent right S-run/multiarm end-station record.

The full event-bound prose is not shortened in the release:
`V78_R4_11_CONTINUOUS_RECORDS.tsv` contains every statement and every event in
order, while `V78_R4_381_EVENT_CONTINUOUS_INTERLINEAR.tsv` gives the one-to-one
phrase binding.

## Why the translation is still mostly exemplar text

The continuous edition has gained grammatical readability, not semantic
coverage. Every one of the 381 events still carries a bracketed local
expansion because even `ET?` and `PER?` do not supply their nouns, arguments or
domain. Long expressions such as “wash the affected place” or “take a portion
of the pictured plant” remain editorial completions from image owner, genre and
the chosen practical world.

Thus V78 does not revive the discarded dictionary. It only asks whether two
small connective categories can sit inside a complete reconstruction without
breaking it.

## Validation and ceiling

`V78_R4_VALIDATION.json` is `PASS`:

- 381/381 events;
- 116/116 statements;
- 11/11 records;
- 19 `ET?` and 9 `PER?` occurrences;
- 28/28 fit-audit rows;
- zero unbracketed concrete source phrases;
- zero f84/f84r access.

The result is a coherent ten-page working edition, not a plaintext translation.
