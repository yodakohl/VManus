# GDT623 — corrected temperament reader and first concrete state/part defaults

Status: **WORKING_TRANSLATION_V2__MOISTURE_AXIS_FLIPPED__LOCAL_ATTACHMENT_REPAIRED**.

## Result

The GDT622 square survives, but its moisture direction does not. The current
working composition is:

| Surface composition | Working reading |
|---|---|
| `qo-k-ch-...` | hot and dry |
| `qo-k-sh-...` | hot and moist |
| `qo-t-ch-...` | cold and dry |
| `qo-t-sh-...` | cold and moist |

Thus `k=hot`, `t=cold`, `ch=dry`, and `sh=moist` are the V2 defaults inside the
quality construction. The moisture sign is the useful correction. The thermal
sign remains weaker: `t=hot, k=cold` is a serious rival on Herbal-only counts.

The first concrete vocabulary beyond the four bundles is:

| Surface | Short default | Strength |
|---|---|---|
| `chody` | dry / dry class | medium |
| `shody` | learned whole form in dry context; content open | moist reading rejected |
| `shedy` | moist / moist class | weak, register-local |
| `kooiin` | cold-dry thick/creeping-root drug subclass | medium |
| `koaiin` | sibling of that rootstock class | weak-to-medium |
| `p...air...` at Herbal page head | root-part / *radix* drug entry | medium |
| Herbal `shor` | flower/fruit stand; reproductive head | weak |
| head `koary|korary` | fruit/seed/reproductive drug | weak |
| `poror(y)` at Herbal page head | opens a Herbal entry | structural |

These are deliberately short values. “Root/underground drug” does not expand
into an invented instruction such as “obtain plant material at the proper
time.”

## Why `ch` now means dry

Of 27 complete Clm 667 comparison rows, 24 are dry: 88.9%. In the guarded
Voynich panel, `ch` occupies 168/192 exact four-corner forms (87.5%) and
455/512 strict q-prefix forms (88.9%). Across Herbal cuts it remains 90.6–94.0%.
Reading `sh` as dry would instead make dry the rare 6.0–12.5% side.

On the whole 179-page panel, V2 ranks first for exact, prefix, and substring
counts; the old GDT622 orientation ranks last. Herbal-only counts reverse the
thermal sign but retain `ch=dry`. Therefore the defensible update is stronger
than the complete four-value key:

```text
ch = dry     strong working direction
sh = moist   binary complement
k = hot      best current working direction, still weak
t = cold     serious t-hot rival remains
```

## Attachment was the second correction

Historical comparators do not license “the first token names the pictured
plant and any matching code twelve lines later describes it.” They support
same-line attachment, an immediate opening clause, or a forward list under an
explicit header.

This removes two old conveniences: f3r Diptam at twelve lines and f24r
Cucurbita at eleven lines can no longer orient the key. The strongest surviving
external anchors are conditional:

- f45v `korary ... qokchy` within two lines: Chamaedrys, if that old visual
  identification is right, reads hot/dry as its medieval description requires;
- f15v has `qotchod` and `qotchey` inside the opening six lines: if the four-leaf
  plant is Herb Paris, it reads cold/dry;
- f38r Balsam and f45r liquorice remain real counterevidence for the old
  moisture direction, but their plant identities are tentative.

This leaves a working reader, not a result manufactured by whichever distant
code fits a chosen plant.

The architecture itself now has two independent manuscript witnesses. Clm 667
and mid-fifteenth-century Wellcome MS.541 f184r both put learned whole drug
names before compact hot/cold, dry/moist, and degree fields. Pal.lat.1234 adds
the complementary hierarchy: temperament/degree blocks contain explicit
plant-part rubrics such as seeds, flowers, leaves, fruits, roots, wood, gums,
and juices. A mixed system of learned names, part classes, and short quality
codes is therefore historically real; it still does not identify the Voynich
values by itself.

## Six repeated carriers preserve local values

Six exact line/page heads occur exactly twice and reach the same strict family
locally in both occurrences:

| Carrier | Pages | Local family | V2 reading |
|---|---|---|---|
| `dsheody` | f86v3, f102r1 | KCH | hot/dry |
| `tchdor` | f95r1, f115v | TCH | cold/dry |
| `poraiin` | f107v, f113v | KCH | hot/dry |
| `kooiin` | f2v, f29v | TCH | cold/dry |
| `tshod` | f95r2, f106v | KCH | hot/dry |
| `yshol` | f42r, f90r1 | TCH | cold/dry |

The recurrence demonstrates a useful attachment mechanism. It does not turn
all six forms into plant names: several cross registers or occur beside
different pictures.

## `chody` is the first practical dry-class word

`chody` occurs 78 times on 56 panel pages. Twelve occurrences have no strict
q-code anywhere on their page. Of the other 66, the nearest strict code is dry
65 times and moist once. Restricting to one physical line gives 33 dry and one
moist. The form is line-internal in 77/78 occurrences, which suits a state or
quality/state word better than a page title.

The concrete default is therefore:

```text
chody  -> dry / dry class (compare Latin sicca)
```

“Dried” is retained only as a separate preparation alternative. Medieval
technical vocabulary distinguishes `siccus` (dry), `siccatus/exsiccatus`
(dried), `humidus` (moist), `humectatus` (moistened), and `recens/viridis`
(fresh/green). Packing those into one gloss would erase the distinction we are
trying to recover.

The apparently symmetric `shody = moist` extension is therefore rejected:

```text
shody nearest strict q-code: 37 dry, 1 moist
shody within one line:        14 dry, 0 moist
```

The similar `shedy` remains a separate weak moist-class candidate. Its nearest
moist-code rate is 79/326 = 24.2%, versus
57/512 = 11.1% for strict q-codes globally, but the effect is section-variable
and moist is still a minority. “Fresh” and “moistened” are not silently added.

## Two actual underground-drug slots

The exact head `kooiin` occurs only on f2v and f29v. The two drawings are
visibly different plants, so it is not one learned species name. Both pictures
emphasize a compact underground stock and both heads lead on the next line to
TCH. One-edit `koaiin` heads f3v, whose long segmented horizontal stock is the
clearest of the three. The practical reading is “cold-dry thick or creeping
root drug / rootstock subclass,” with the cold/dry value contributed by the
separate q-code. “Rootstock” describes the picture for a modern reader; it is
not a claim that the medieval plaintext used the later botanical sense of
*rhizoma*.

The second family is broader and temperament-independent:

- f18r `pdrairdy`: conspicuous fine roots;
- f23v `podairol`: long branching red roots;
- f31v `podair`: a very large fine root fan;
- f39v `pdair`: one plant with a large divided root system;
- f43v `pdsairy`: two units, one with a curled/segmented body and one with a
  fine root bundle.

All five forms are Herbal page heads and all five official images emphasize
the underground part. Their first complete or partial q-onsets differ. Hence
`p...air...` means, provisionally, **root-part / *radix* drug entry**, not
“hot/dry” and not “fibrous root.” RF1b even splits f39v `pdair` as `p air`,
making `air/dair` the better semantic-core candidate and `p` a plausible head
wrapper. f31v was queried as one explicit supplemental visual page and did not
enter any frequency total.

## A weak reproductive-part layer

The eleven-page visual audit adds two intentionally weaker defaults. Exact
`shor` occurs eight times on six inspected pages: f6v, f18r, f23v, f29v, f39v,
and f45v. All six have conspicuous flowers, buds, fruits, or seed-like terminal
bodies. Across the full panel, 67/91 `shor` occurrences are Herbal. The short
default is **flower/fruit stand; reproductive head**. It remains weak because
several equally conspicuous reproductive drawings lack `shor`, and the form
also crosses into other sections.

The only `koary` and `korary` page heads are f6v and f45v. Both have many
terminal bodies and an early `shor`, so **fruit/seed/reproductive drug** is a
useful weak default. Both readings are boundary-unstable and f45v also has an
enormous rootstock. `koair` is excluded: it contains the root-family `air` core
and its image was not part of this visual audit.

## Concrete excerpts

```text
f2v.1–2
kooiin ... / ... qotcho ...
[thick/creeping-root drug] ... / ... [cold and dry] ...
```

```text
f18r.1–2
pdrairdy ... / ... qokchol ...
[root-part / radix entry] ... / ... [hot and dry] ...
```

```text
f56r.16
qotchy chody ctho r chey kcharg
[cold and dry] [dry / dry class] <ctho> <r> <chey> <kcharg>
```

```text
f86v3.17
dsheody qokchey dal or odaiin sar
[recurrent carrier] [hot and dry] <dal> <or> <odaiin> <sar>
```

Angle brackets are untranslated surfaces. They stay visible because replacing
them with “take material, perform step, continue” would add no information.

## Boundary and next move

This is not a complete Voynich translation. It is a materially narrower and
more concrete working dictionary than GDT622: one axis was corrected, page-wide
attachment was restricted, one dry-class word and two root-drug families now
have operational defaults, one false moist extrapolation was removed, and two
reproductive-part defaults were added at explicitly weak strength.

The next useful route is to extend the same compositional test to complete
`ch...`/`sh...` and `k...`/`t...` word pairs, then search the already inspected
Herbal heads for leaf, flower, fruit/seed, and whole-herb contrasts. A candidate
survives when its short meaning predicts both the word family and the picture
or local quality code without changing the V2 moisture axis.
