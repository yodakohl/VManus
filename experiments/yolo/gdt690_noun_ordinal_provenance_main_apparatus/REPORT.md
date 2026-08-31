# GDT690 — V63 concrete noun main text and rival apparatus

## Outcome

V63 is the first current reader in which every German noun printed in the main text is addressable to one exact written token ordinal. It keeps the concrete reading aggressive, but moves alternatives and parser vocabulary out of the recipe sentence.

The deterministic result is:

`PASS_V63_ALL_MAIN_NOUNS_EXACT_ORDINAL__ONE_MAIN_HEAD_PLUS_RIVAL_APPARATUS`

The edition contains 51 lines, 479 written token positions, 725 noun occurrences at 459 positions and 108 selected canonical German nouns. Seventy-two explicit render rules touch 104 positions; 92 positions change their spoken wording.

## Main dictionary decisions

The productive initial heads now have one short value throughout the main text:

| head | V63 main value | apparatus rivals |
|---|---|---|
| `p` | Pulver | Trank, Pille |
| `s` | Samen | Salz, Saft, Arzneispecies |
| `r` | Wurzel | Harz/resina |
| `l` | Holz | Auszug/liquor |

This removes atomic values such as “fertig aufbereitetes Drogenholz.” For example, `ldy` now reads “fertig aufbereitetes Holz”: the noun head is `Holz`; the remainder supplies the result state.

The six requested problem areas receive these working choices:

| family | main text | apparatus |
|---|---|---|
| `shx` | eingeweichtes Gummi | Harz, Gummiharz, Pech |
| `shor` | Blüte | Fruchtstand, Samenstand, reproduktiver Pflanzenteil |
| `r/rr/raiin/ram` | Wurzel | Wurzeldroge, Harz |
| `checthy` and CTH family | Kraut | Blatt, Krautdroge |
| `qotain` and frame sisters | kalter/heißer Ansatz, Grad II/III | Zubereitung; q/Frame only as apparatus |
| `olkar/olam` | Holzfraktion / Maß Holz | Drogenholz, Holzstoff, Auszug |

`olkar/olam → Holz` is deliberately labeled `PROVISIONAL_LOCAL_SCOPE_HEAD`. The forms are o-initial and therefore do not inherit GDT635's productive token-initial `l` rule. V63 keeps the concrete local choice because the prior reader carried a Holz scope at exactly these positions, but it does not export a free internal-`l` rule.

## Renderer cleanup

V62 spoke 40 structural or apparatus-only noun occurrences: chiefly 20 `Holzbindung`, twelve preparation/qo/Ansatz frames, the CTH/Herbal labels, `Eintrag`, and abstract alternative labels. V63 speaks none of them.

Twenty-one token positions previously contained a slash or an “oder” alternative. V63 contains zero. Each position receives one main choice; all live alternatives remain recoverable in the apparatus.

Examples:

- `shx`: “eingeweichtes Gummi,” not “eingeweichtes Gummiharz.”
- `shor`: “Blüte,” not “Blüten-/Fruchtstand; reproduktiver Teil.”
- `checthy`: “trockenes Kraut,” not “trockenes CTH-Drogenmaterial; im Herbal …”.
- `qotain`: “kalter Ansatz, Grad II,” not “kalt im qo-Rahmen, Grad II.”
- `olkar`: “erste erhitzte Holzfraktion im Ansatz,” not “…; Holzbindung offen.”
- `olam`: “ein Maß Holz,” not “Ansatz-/Drogenmaterial; Holzbindung offen.”

The eight current `chol/shol/tol` cells still emit only `trocken/feucht/kalt` and zero nouns. GDT685's rejection of a universal unheaded `Ansatz` therefore remains intact.

## Exact provenance and the remaining gap

Ordinal provenance is complete: all 725 main noun spans have an exact `(locus, token_ordinal, character_start, character_end)` and reproduce their visible German span byte-for-byte apart from sentence-initial case.

Upstream card provenance is not complete. Among the 479 token positions, the restricted GDT635/636/685 join gives:

| upstream status | positions |
|---|---:|
| exact surface and byte-identical source gloss | 49 |
| exact surface, different source gloss | 45 |
| productive initial head only | 25 |
| upstream card not exported in this scope | 360 |

V63 never converts the last category into a fabricated source. The practical main value is retained as a working selection while the token table explicitly reports `UPSTREAM_CARD_NOT_EXPORTED_IN_GDT690_SCOPE`.

## Historical comparator

The historical material calibrates short heads and rivals; it does not prove a Voynich value.

- Tadhg Ó Cuinn's 1415 materia medica is organized as short apothecary drug heads followed by hot/cold/dry/wet qualities and uses a standalone `Gumi` chapter. [1415 introduction](https://celt.ucc.ie/published/G600005/index.html), [Gumi chapter](https://celt.ucc.ie/published/G600005/text762.html)
- Early-fifteenth-century Wellcome MS.542 explicitly combines `Aloes lignum` with hot/dry grade II and `Radix` with hot/dry grade III. This is a close architectural comparator for head + quality + grade. [Wellcome MS.542](https://wellcomecollection.org/works/n674z2xd)
- The Ó Cuinn glossary preserves `materia` as matter/substance and `flos rose` as a short flower-part head. [Materia-medica glossary](https://celt.ucc.ie/published/G600005/text907.html)
- Gualterus de Dosibus distinguishes quantity by measurement from quantity by quality/degree and repeatedly separates minimum/maximum dose from the material and its grade. [Gualterus de Dosibus](https://celt.ucc.ie/document/T600021/)

These comparators favor `Pulver/Samen/Wurzel/Holz/Gummi/Blüte/Stoff/Portion/Maß/Dosis` over sentence-long dictionary values.

## Validation

The independent validator performs eighteen named checks, recomputes all 725 main and 773 source noun spans, replays the 49/45/25/360 source partition, confirms all 36 productive-head positions, verifies the six focus families, and regenerates every result artifact byte-for-byte. It also confirms that no f84/f84r selector was accessed.

## Interpretation

V63 is a more useful working translation than V62: it says concrete things in the main channel and places uncertainty where it belongs. It is still a replaceable working code, not a decipherment or historical plaintext identification.

The next high-yield pass should attack the 140 preparation-noun spans in the same way, especially the 89 bare `Ansatz` occurrences now printed in V63: separate true o-frame preparations from learned whole cards and prose support, then choose concrete preparation nouns such as Ansatz, Auszug, Absud, Mazerat or Bad only where the exact card or local family can carry them.
