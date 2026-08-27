# GDT575 — repeated relation/modifier scope atlas

## Result

`PASS_4609_RELATION_MODIFIER_SLOTS__96_DUPLICATE_GROUPS_IN_90_EVENTS__3_SAME_ROOT_ADJACENT__62_SAME_ROOT_INTERRUPTED__31_SURFACE_COLLISIONS__17_OUTER_INNER_PAIRS__ZERO_SCOPE_COLLAPSE`.

All 4,609 relation/modifier slots in the complete GDT574 edition align exactly
to a current German phrase: 4,575 are unscoped, seventeen outer and seventeen
inner. No relation/modifier slot uses the third-level nominal scope.

The complete scan finds 96 exact full-phrase duplicate groups in 90 events and
98 mentions after the first. Their real structure is:

| underlying identity | raw spacing | groups | consequence |
|---|---|---:|---|
| same root | adjacent | 3 | bounded count-voice candidates |
| same root | interrupted | 62 | keep order; restore local attachment |
| different roots | adjacent | 13 | differentiate the German root voices |
| different roots | interrupted | 18 | differentiate voices and keep order |

## What looked repetitive

| complete current phrase | groups | extra mentions |
|---|---:|---:|
| `an der bezeichneten Stelle` | 40 | 41 |
| `auf Grad I` | 35 | 36 |
| `als Ausführung` | 17 | 17 |
| `auf Grad II` | 1 | 1 |
| `mit der lokalen Variante` | 1 | 1 |
| `von der Ausgangsstation` | 1 | 1 |
| `zur Zielspalte` | 1 | 1 |

Only three groups are the same atom with no intervening raw slot:

- `G407-E0152`: `O+O` — `als Ausführung` twice;
- `G407-E1846`: `D_ADDR+D_ADDR` — `an der bezeichneten Stelle` twice;
- `G515-E0379`: `AL+AL` — `zur Zielspalte` twice.

These are the only current relation/modifier cases for which a direct count
voice is structurally analogous to GDT574's adjacent-action rule.

## The more important correction

Thirty-one duplicate groups are not repeated roots at all. Thirty involve two
or more of the seven atoms currently flattened to `an der bezeichneten Stelle`;
the remaining case is `G407-E4353`, where `LOCAL_CHAR_I` and `G_LABEL` both
sound like `mit der lokalen Variante`.

This makes a plain `zweimal` rule actively misleading. The better next move is
a small common `STELLENVERWEIS`/`VARIANTENVERWEIS` family whose learned short
labels keep `D_ADDR`, `A_ADDR`, `AM_ADDR`, `LOCAL_CHAR_F`, `M_LOCAL`, `S_ADDR`,
`D_LABEL` and the variant atoms distinguishable. The labels are analytical
sigla, not claimed Voynich pronunciations.

The 62 interrupted same-root groups also stay open. Almost every repeated grade
is separated by an action, so its useful reading is likely local
action–modifier attachment (`… auf Grad I … auf Grad I`) or a repeat particle,
not a detached global count.

## Scope pairs

Seventeen additional events contain the same base root once in the outer and
once in the inner branch. They are intentionally not duplicate full phrases.
Both values can be shortened safely as, for example:

```text
über die sichtbare Verbindung im äußeren Zweig
+ über die sichtbare Verbindung im inneren Zweig
→ über die sichtbare Verbindung im äußeren und im inneren Zweig
```

The output table retains both atom positions and both scopes. No scope is
discarded or converted into a count.

## Consequence

GDT575 replaces one tempting blanket rule with a clearer working architecture:

- count only raw-adjacent identical roots;
- keep interrupted roots ordered and reconnect modifiers locally;
- stop making different technical sigla sound identical;
- factor outer/inner wording only while both scope slots remain explicit.

This is an inventory layer only. It changes no clause, root, recipe, event,
surface, page or scope and confirms no plaintext, lexeme, language, genre,
historical codebook or object identity.
