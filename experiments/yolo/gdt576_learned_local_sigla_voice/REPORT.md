# GDT576 — learned local-sigla voice

## Result

`PASS_4_FAMILY_FRAMES__12_LEARNED_SIGLA_CARDS__773_LOCAL_SLOTS__715_CLAUSES_DIFFERENTIATED__31_COLLISIONS_RESOLVED__5122_EXACT_ROUNDTRIPS__ZERO_ROOT_CHANGE`.

GDT575 showed that the edition's smooth German was hiding structure: seven
different address atoms all sounded like `an der bezeichneten Stelle`, while
five variant/label atoms mostly sounded like `mit der lokalen Variante`.
Thirty-one apparent repeat groups were therefore different roots, not repeated
meanings.

GDT576 gives those atoms a mixed codebook voice: the function remains small
and productive, while the technical head is learned.

| atom | common function | learned head | current voice | uses |
|---|---|---|---|---:|
| `D_ADDR` | place reference | D-Stelle | `an der D-Stelle` | 519 |
| `A_ADDR` | place reference | A-Stelle | `an der A-Stelle` | 63 |
| `AM_ADDR` | place reference | AM-Stelle | `an der AM-Stelle` | 74 |
| `S_ADDR` | place reference | S-Stelle | `an der S-Stelle` | 16 |
| `LOCAL_CHAR_F` | place reference | f-Kennmarke | `bei der f-Kennmarke` | 48 |
| `M_LOCAL` | place reference | m-Ortsmarke | `bei der m-Ortsmarke` | 14 |
| `D_LABEL` | note | d-Vermerk | `beim d-Vermerk` | 2 |
| `LOCAL_CHAR_I` | variant reference | i-Variante | `mit der i-Variante` | 18 |
| `LOCAL_CHAR_G` | variant reference | g-Variante | `mit der g-Variante` | 12 |
| `G_LABEL` | note | G-Vermerk | `beim G-Vermerk` | 4 |
| `LOCAL_CHAR_B` | variant reference | b-Variante | `mit der b-Variante` | 2 |
| `LOCAL_CHAR_J` | variant reference | j-Variante | `mit der j-Variante` | 1 |

This is the requested compromise between productive roots and learned whole
entries. The common frames predict how a known atom composes in a clause; the
short head prevents us from pretending that two distinct technical sigla mean
exactly the same thing.

## Concrete gain

The 773 slots occupy 715 clauses, 294 statements and 28 pages. All 715 clauses
change: 123 state cards and 592 nonstate cards. For example:

```text
G407-E0001
before: ... an der bezeichneten Stelle und an der bezeichneten Stelle.
after:  ... bei der f-Kennmarke und an der A-Stelle.

G407-E4353
before: ... an der bezeichneten Stelle, mit der lokalen Variante,
        mit der lokalen Variante und an der bezeichneten Stelle.
after:  ... an der D-Stelle, mit der i-Variante,
        beim G-Vermerk und bei der m-Ortsmarke.
```

Every one of GDT575's 31 different-root collision groups now has a pairwise
distinct target phrase. The 65 same-root repeat groups remain explicit for the
next attachment/count pass; they are not silently deleted.

## Why this architecture is plausible

Fifteenth-century technical recipe writing commonly mixes a small repeated
instructional grammar with learned names, sigla, units and Latin heads. Meister
Eberhard's cookbook, for example, places recurring items, imperatives and
repeat particles beside learned Latin recipe heads; Cod. 3064 mixes German,
Latin and partly ciphered recipe material. These are analogies for the hybrid
architecture, not evidence that the Voynich labels have these German names.

- Meister Eberhard edition: <https://www.uni-giessen.de/de/fbz/fb05/germanistik/absprache/sprachverwendung/gloning/tx/feyl.htm>
- Cod. 3064 description: <https://kdih.badw.de/datenbank/handschrift/39/1/9>

## Reversibility and limit

Each assignment retains the original fragment, target fragment, source/target
spans, atom ID, recipe position and scope. The inverse channel reconstructs all
5,122 GDT574 clauses exactly; all 793 statements and thirty page boundaries
remain fixed. All 54 independent checks pass.

The D/A/AM/f/m/S/d and i/g/G/b/j heads are analytical codebook labels, not
claimed pronunciations. No Voynich root value, page, surface, recipe, event,
plaintext, language, genre or object identity is added.
