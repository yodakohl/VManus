# V77 four-role selection — actual 1420-era codebook words only

## Selected working result

V77 removes the invented long-word dictionary and keeps exactly two new,
atomic, explicitly provisional word hypotheses:

| anonymous exact card | working word | why it may remain |
|---|---|---|
| `dcda95c81a5460feb191` | `ET?` = **UND/AUCH?** | 19 mostly medial occurrences, including two visible A–link–B–link–C chains; `et` is an exact whole-word entry in the genuine Florentine Fi1 key of 1414 |
| `b5fcea1eaed06b2f2291` | `PER?` = **DURCH/GEMÄSS?** | 7/9 field-entry occurrences and one line-edge carry/restart; `per` is an exact whole-word entry in the same 1414 key |

The question marks are mandatory. These are creative defaults, not confirmed
translations.

The selected dictionary also contains two nonlexical formal labels and 20
`EXEMPLAR_VALUE_UNKNOWN` rows. Every former portable content mnemonic—MASS,
ANWENDEN, BEREIT, ANSATZ, ZIEL, KLAR, VORIGES, ANTEIL, TEMPERIEREN, SPÜLEN,
ABLASSEN—is withdrawn.

## Why the minority lead is retained

R1, R2 and R3 correctly returned zero words from their frozen source samples.
Those samples primarily contained the diplomatic nomenclators of Gabriel de
Lavinde (1379). They therefore found no exact category match for the inherited
medical/process mnemonics.

R4 independently added an actual 1414 key whose three whole-word entries are
`per`, `et`, and `che`, then tested fresh, simpler categories against all frozen
occurrences. This is a genuine evolution of the hypothesis, not a relaxation
of the historical rule. The user explicitly allows an exploratory assumption
to remain until contradicted or replaced by a better one, so a three-to-one
vote is not used as an automatic veto.

The selection is nevertheless conservative:

- no card is matched by visual resemblance to the historical sign;
- `che` is not assigned merely because it is common;
- no terminal card is called `scripsi` merely because `scripsi=22` occurs in
  the after-1412 Pisan-papal key;
- no word receives more than one minimal default;
- the next round must use the same default at every occurrence and withdraw it
  on a real contradiction rather than inventing polysemy.

## Four-role outcomes

| role | source-first result | selected contribution |
|---|---|---|
| R1 workshop master | 0 words; 4 formal channels | strict teachability and complete 197-event audit |
| R2 historical scribe | 0 words from 48 exact rows / 6 source objects | documentary negative control and shelfmark discipline |
| R3 technical notation writer | 0 words; terminal/placement confounds quantified | machine-checkable invariance and false-friend audit |
| R4 chancery corrector | 2 atomic codebook-category leads | `ET?`, `PER?`; all long old glosses withdrawn |

## Executable V78 rule

1. Print `ET?` at all 19 exact `dcda…` occurrences.
2. Print `PER?` at all 9 exact `b5fcea…` occurrences.
3. Print the two structural prompts only as `[FORMAL:…; KEIN WORT]`.
4. Print every other target card as `[EXEMPLARWERT UNBEKANNT]`.
5. Local fluent readings may add bracketed image-/owner-/master-exemplar
   expansions, but those words do not enter the dictionary.
6. No substring, PAGE_HOST, stem, sound or language inference is licensed.

The selected machine-readable dictionary is
`V77_SELECTED_CARD_DICTIONARY.tsv`; all 197 affected occurrences are in
`V77_SELECTED_197_OCCURRENCE_AUDIT.tsv`. `V77_VALIDATION.json` is `PASS`.

## Interpretation ceiling

V77 shows only that two very small historical codebook-sized categories can be
made coherent as a creative reading on these ten pages. It does not establish
that the manuscript uses Latin, that the visible cards spell `et` or `per`, or
that any Voynich author used the Florentine key.
