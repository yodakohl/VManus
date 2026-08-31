# GDT708 report — a variable batch card reaches one terminal product

## Result

The best next reading is A012:

> **C021 / f106r.23#2-6:** Das Arzneikompositum bis zur Mittelstufe
> aufbereiten. Danach stehen: abgemessener Anteil II; Rohstoff I; heiße
> Mittelstufe. Mögliches terminales Produkt: bis zur Mittelstufe eingeweichtes
> und abgeschlossenes Arzneikompositum.

The decisive information is not another generic continuation. The earlier
three-item path ended at #5 with only a hot middle-stage checkpoint and had
lost the action's material head. #6 supplies the missing terminal product:
`Arzneikompositum`, `Mittelstufe`, `eingeweicht` and `abgeschlossen` occur
together. The working reading cuts before #7, which changes to hot-dry at the
beginning of the grade. This is an analytical exclusion point, not written
punctuation or a written patient change; #7 may begin another phase of the
same material.
Soaking and completion occur only on the right; they are not silently
derived from the broader action `aufbereiten`.

## What changed in the working model

The surviving material is not well described by a fixed three-token result.
The useful form is variable:

> action + shortest coherent batch card, ending at the first terminal
> material product or at the first material, operation or grade reset

Three cases place the terminal product after an attribute stack:

| case | visible order | best end | decision |
|---|---|---:|---|
| A012 | quantity → material → state/degree → terminal product | #6 | C021 |
| A014 | quantity → state/degree → terminal product | #5 | object-block hold |
| A024 | state/degree → state/degree → material → terminal product | #7 | object-block hold |

A043 is the strongest local/formal countercase because explicit #2 `dy`/`;`
places its finished dry portion immediately at #3. It loses to A012 only on
the exact material-and-degree return needed for a new edge. #4
changes middle degree to grade end and #5 adds grade III. The old immediate
hold therefore survives, while its GDT707 three-item extension is stopped.

## The five shorter paths

A073, A070, A029, A017 and A004 all have the same best cut at two items. Their
third item is the first overextension:

- A073 changes to dry Arzneikompositum and restarts the grade;
- A070 restarts with broad `trocken` after the hot-dry checkpoint;
- A029 adds a new dry, measured, completed middle-stage product;
- A017 contradicts middle degree with cold grade-start;
- A004 changes the just-written middle degree to grade end.

A024 also has a tempting later #9 `oechedy`, “fertige, bis zur Mittelstufe
getrocknete Masse”. It matches drying and middle degree better than #7, but the
first terminal product #7 and the new quantity/material start #8 intervene.
The no-skip first-terminal rule therefore cannot jump to #9.

These are useful practical fragments, but still lack enough material, degree
or action agreement for new graph edges.

## Exact graph effect

C021 forms the isolated component M014. Only #2 and #6 are edge nodes. #3
`dair`, #4 `al` and #5 `qokedy` remain visible hull-only attribute carriers.
The cumulative graph is now 20 edges / 14 components / 37 unique nodes / 43
incidences / 45 hull and render positions. Shared nodes remain six; hull-only
positions rise to eight.

All 479 token glosses, 51 line translations and three bound spans remain
unchanged. The independent validator performs more than 83,000 checks. The
GDT388 packet remains formally inaccessible and not score-ready.

## Next useful move

Run the same first-terminal-product scan over every one of the 42 delayed
nominal windows, without skipping an earlier field. That will show whether
A012 is a unique readable closure or one member of a broader variable batch
architecture, using no new page and no new word meaning.
