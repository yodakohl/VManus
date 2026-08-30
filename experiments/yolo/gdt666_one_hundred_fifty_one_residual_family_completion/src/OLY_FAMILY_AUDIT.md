# OLY family audit (recipe-practitioner read)

## Recommendation

**ACCEPT** a 48th learned action block:

`OLY_STRAIN_ACTION` — spelling `oly` — concrete default **abseihen**.

This is a narrowly scoped learned block, not a productive equation `ol + y =
abseihen`.  It may be used as the exact naked word `oly`, or as the exact
terminal block `oly` after an independently licensed, complete material/result
head.  On that rule, `chololy` is best read as:

`CH_DRY + OL_MATERIAL + OLY_STRAIN_ACTION`

> **seihe den getrockneten Drogenstoff ab**

This is more predictive than either an otherwise unsupported exact
`LEARNED_CHOLOLY_WHOLE` or the non-action parse `CH + OL + OL + Y`.

## Safe evidence and distribution

The V42 safe coverage contains the following exact-token distribution:

| surface | occurrences | BOS | medial | EOS | inherited reading |
|---|---:|---:|---:|---:|---|
| `oly` | 53 | 1 | 16 | 36 | abseihen |
| `loly` | 5 | 0 | 1 | 4 | seihe den Holzabsud ab |
| `qolkeeoly` | 1 | 0 | 1 | 0 | erhitzte Drogenbasis; danach abseihen |
| `olyly` | 1 | 0 | 0 | 1 | seihe ein zweites Mal ab |
| `doly` | 4 | 1 | 1 | 2 | eine Dosis Abguss |
| `choly` | 12 | 0 | 9 | 3 | Trockenrückstand |
| `chololy` | 1 | 0 | 1 | 0 | GDT666 target |

The 53 naked occurrences are strongly action-shaped: 36 close their line, and
the medial cases commonly divide one preparation step from the next.  The one
BOS case (`f86v6.13`) is compatible with a carried-over instruction and does
not require a material meaning.  Most importantly, the inherited learned
relatives preserve the same operation: `loly` ends five wood/preparation lines,
`olyly` explicitly repeats the straining, and `qolkeeoly` contains a terminal
straining step after heating.

## Strong complete-line checks

1. **f103v.33** — `... shdpchy opchey oly`: an anfeuchtete/angetrocknete
   Pulverportion and a Trockenpulveransatz are followed by `oly`.  “Abseihen”
   is an executable final separation; another unnamed material is not.
2. **f75v.63** — `... oldy olyly`: an inherited finished/strained extract is
   followed by “seihe ein zweites Mal ab.”  This is the clearest internal
   support that `oly` is the learned operation inside an iterative whole.
3. **f81r.12** — `... sheedy qokeey loly`: wetting and end-stage heating end in
   the learned wood-specific straining command.  The five `loly` occurrences
   are 4/5 line-final.
4. **f75r.15** — `sain qokain qolkeeoly ...`: the sole inherited long relative
   explicitly joins an erhitzte Drogenbasis to subsequent straining.  It is
   supporting evidence for terminal `oly`, although the entire long form
   remains learned and is not reparsed mechanically here.
5. **f28v.9** — `sor chear chl choly dar`: `chl` introduces drying and `choly`
   names the resulting Trockenrückstand, followed by a measured fraction.
   This is the strongest negative control: `choly` must not inherit the
   straining action.
6. **f35v.17** — `daiin dain chkaly choly`: a dry/heat preparation terminates
   in `choly` as a residue/result noun, again without flow.
7. **f80v.2** — `... qoky daiin doly`: a graded heated preparation ends with
   “eine Dosis Abguss.”  `doly` is a nominal learned whole, not an imperative
   instance of productive `d + oly`.
8. **f3r.5** — `qokol chololy s cham cthol`: heating is immediately followed by
   the target form, then a new seed/material clause begins.  Reading
   `chololy` as “seihe den getrockneten Drogenstoff ab” gives the practical
   order *heat — strain — next material entry* without inventing water,
   quantity, or a separate flow token.

## Exact scope

Accept `OLY_STRAIN_ACTION` only under longest-match parsing in either of these
positions:

1. exact surface `oly`; or
2. exact suffix `oly` after a separately licensed, complete material/result
   head, currently demonstrated compositionally by `l + oly` and
   `chol + oly`.

The block licenses the operation **abseihen**, but it does not itself license
water, an infusion/decoction, a quantity, a receiving vessel, or a resulting
liquid.  Such details require independent cards.

## Examples and exclusions

- `oly` → `OLY_STRAIN_ACTION` → **abseihen**.
- `loly` → `L_WOOD + OLY_STRAIN_ACTION` → **seihe den Holzabsud ab** (existing
  learned relative; it supports the block).
- `chololy` → `CH_DRY + OL_MATERIAL + OLY_STRAIN_ACTION` → **seihe den
  getrockneten Drogenstoff ab**.
- `olyly` remains the learned iterative extension
  `OLY_STRAIN_ACTION + ITERATIVE_Y`, **seihe ein zweites Mal ab**; this does not
  make bare `ly` productive.
- `qolkeeoly` remains its existing learned long form.  Its terminal semantics
  support the audit, but its unique occurrence is insufficient to export a
  general `qolkee + oly` parser.
- **Exclude `choly`**: parse as `CH_DRY + OL_MATERIAL + Y_START_OR_CLOSE`,
  **Trockenrückstand**.  Its 12 occurrences are a coherent nominal control.
- **Exclude `doly`**: preserve the exact learned nominal whole, **eine Dosis
  Abguss**.  Do not turn it into the command “eine Dosis abseihen.”
- **Exclude `qoly` and `ykoly`**: longest licensed wholes/components win; a
  substring ending in the letters `oly` is not enough.
- Exclude all other accidental internal `oly` strings until their prefix is a
  licensed complete material/result head and the resulting instruction is
  locally executable.

## Exact proposed card row

Using the GDT666 card columns
`surface, working_meaning_de, composition, strongest_rival_de, family`:

```tsv
chololy	seihe den getrockneten Drogenstoff ab	CH_DRY+OL_MATERIAL+OLY_STRAIN_ACTION	zwei Drogenstoffe leicht zusammen trocknen	EXTRACT
```

The rival deliberately states what the competing `CH + OL + OL + Y` parse
would have to mean; it does not smuggle in an unlicensed Auszug or flow result.

## Exact proposed learned-block registry row

If the 47-role sheet is extended with its existing role-registry columns, add:

```tsv
oly	OLY_STRAIN_ACTION	abseihen	exaktes nacktes Wort oder exakter terminaler Aktionsblock nach einem vollständigen Stoff-/Ergebniskopf	oly|loly|chololy	kein Export in choly|doly|qoly|ykoly; olyly und qolkeeoly bleiben gelernte Erweiterungen	HIGH
```

The confidence is high for the narrow block and only medium for its first new
composition in `chololy`; this distinction should remain visible in prose even
if the role sheet has only one strength field.
