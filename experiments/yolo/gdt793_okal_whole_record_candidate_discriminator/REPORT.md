# GDT793 report — `okal` whole-record candidate discriminator

## Result

GDT793 selects one deliberately bold but replaceable working meaning for the
exact complete form `okal`:

```text
okal = KENNSTELLEN-/SYSTEMEINTRAGSCODE
       [C0 working renderer, not confirmed plaintext]
```

In a ring this is displayed as a ring-position or system-entry code; in the
f82 pool drawing it is displayed as a station/system-entry code. The meaning
is not exported to `ok`, `al`, `okaly`, `okaldy`, `qokal` or any other longer
or shorter form.

This is more specific than GDT792's structural tag. It says that `okal` most
likely classifies or codes a member/slot of an organised set. It does **not**
say “go to this target”, identify one unique named member, or mean a numeral.
An entirely opaque productive renderer remains a live null, so the confidence
stays C0.

The guarded build passes 181 checks and two byte-identical replays.

## Whole-record capacity

The literal complete-surface family `^okal.*$` contributes 41 occurrences,
fourteen whole forms and seventeen running paragraph units on the released
thirty-page spine:

| scope | occurrences |
| --- | ---: |
| running prose | 26 |
| local one-word labels | 15 |
| exact `okal`, running | 16 |
| exact `okal`, local | 4 |

Eighteen of 26 running family occurrences occur on pages with no local family
label. For exact `okal`, thirteen of sixteen running uses occur on pages with
no local exact `okal` label. A universal page-local pointer is therefore the
wrong default before any finer scoring begins.

## Address model: the target was its own evidence

GDT792's same-page bridges were real string reuses, but they did not establish
reference direction. GDT793 removes every complete `okal*` form and asks
whether the rest of the record still identifies the alleged source owner.

| record → alleged owner | overlap before mask | overlap after mask | owner recovered |
| --- | --- | --- | --- |
| f72 ring E → ring D | `okal`, `okaly` | none | no |
| f82 P1 → lower communal panel | `okal` | none | no |
| f82 P2 → lower communal panel | `okal` | none | no |

The result is 0/3. In other words, all apparent address evidence disappears
when the candidate is forbidden from proving itself. The class/slot model
does not predict such a companion fingerprint and survives this test.

## Unique member or name: four equally good f72 assignments

The ordered f72 outer ring contains:

```text
slot 2  okalar
slot 3  okal
slot 4  okaly
slot 5  okal
slot 12 okaly
```

Later ring-E prose contains one `okal` and one `okaly`. Either prose form can
be paired with either of the two identically labelled local members. That
creates four maximum exact assignments. Neither a unique named figure nor a
unique addressed member is recoverable.

The f82 P1 and P2 occurrences each have one exact local `okal` candidate, but
both point to the same proximity-ambiguous label between a figure and a
vertical form. Two locally unique cases cannot rescue the four-way f72
collision.

Repeated labels are exactly what a class or slot code may do: two different
members can carry the same code.

## Number, ordinal and grade

A strict whole-form ordinal fails inside the f72 sequence itself. `okal`
precedes `okaly` at slots 3→4, while `okaly` precedes `okal` at slots 4→5.
This produces the direct constraint cycle:

```text
okal < okaly < okal
```

The f82 pair `okal`, `okaldy` supplies only one edge and can fit either of two
arbitrary orders; it is not a transferable number ladder. A quality-grade
model remains unscored because the current local inventory supplies no
independently coded, repeated visible quality scale.

Thus `okal = four`, `okal = grade I`, and a simple ordinal family are not
usable defaults.

## The useful calendar/slot lead

One pattern is too interesting to discard. At homologous outer slot 4, four
of five mapped diagram units carry an `okal*` form:

| diagram unit | slot-4 form |
| --- | --- |
| f70v1 outer band | `okalal` |
| f70v2 outer band | `okala` |
| f72r1 outer band | `okalam` |
| f72r2 outer band | `okaly` |
| f72r3 outer band | `oraiinam` |

This is not the numeral four: the same family also occupies slots 2, 3, 5,
8, 9 and 12 in the admitted local material. The productive family may instead
be a topology-bound calendar, day, degree or catalogue-slot renderer. That is
the strongest concrete specialization of the selected class/code model and
the next route worth attacking.

## “Upper” sensitivity

The three timed exact-`okal` celestial labels lie at 11:30, 00:00 and 01:15;
the fourth exact label is in the f82 top row. In the post-hoc ±1.5-hour clock
window, 58 of 158 timed local labels lie in the window and all three timed
`okal` labels hit it (unadjusted descriptive probability 0.047842).

This keeps “upper-zone code” as a low-capacity rival, but it does not overtake
the class/slot reading. The window was noticed after exposure, there are only
three timed tokens, and the broader family is not confined to the top.

## What the working rendering actually says

The f72r2.22 source line is:

```text
oteey tey teodal chokaly ol cheol ol aiin oteo daiin shokal otey otaiin
otaly dal okaly dalchdy eteeey okal shey qoteeody sheycthy chotal chas
otoees aiin
```

Only the exact target changes:

```text
... dalchdy eteeey ⟦okal:Ring-/Systemeintragscode⟧ shey qoteeody ...
```

The surrounding paragraph remains untranslated. This avoids converting an
unknown sentence into fluent but content-free instructions. The practical
claim is only: at this position the manuscript most likely invokes the same
class/slot code that can also stand alone beside multiple diagram members.

All twenty exact occurrences receive an owner-conditioned version of this C0
display. Every row contains confidence, evidence, counterevidence, exact
scope, lexeme status and zero component-export credit.

## Alternate readings and source correction

Eleven of the fifteen local prefix-family labels are exact whole-form matches
in ZL3b, IT2a and RF1b. One differs in one alternate reading and three differ
in both, chiefly at the final character or word boundary. The three editions
are readings of one manuscript, not independent witnesses. In particular, the
endings cannot yet receive meanings.

During pre-build delegated exploration, two overly broad raw regex calls
traversed the mixed alternate-reader table. Their displayed output contained
only requested released loci and no `f84*` row, but all values from those
calls were excluded. The executable builder reacquired the material through
the required 35-selector guard: 1,007 allowed rows were selected and 98
`f84*` rows were rejected before materialisation. Zero sealed rows enter an
artifact or score.

## Claim ceiling

`KENNSTELLEN-/SYSTEMEINTRAGSCODE` is a C0 exploratory complete-whole renderer,
not a deciphered German or English word. GDT793 establishes no language,
sound, root, affix, numeral, direction, plant, substance, person, disease,
treatment or unseen-page rule.

## Next route

The next high-yield test is a multi-form homologous-position codebook over the
already released circular arrays. Instead of asking whether one exposed form
likes one slot, it must ask whether several complete forms jointly predict
several different homologous slots under leave-one-array-out transfer. A real
calendar/degree code should yield a reusable many-form mapping; a generic
class marker or positional renderer should not.
