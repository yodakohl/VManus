# GDT782 — recurrent-six target-external field adjudication

Status: `PASS__20_CACHE_OCCURRENCES__14_READER_EXACT__6_TARGET_MASKED__8_TARGET_EXTERNAL__65_EXTERNAL_NEIGHBORS__5_REVISED__1_KEPT__270_CONTEXTUAL__106_FALLBACKS__230_CONSUMED__ZERO_COMPONENT_EXPORT`

## Result

The six recurrent GDT781 forms reconstruct as 20 cached positions: 14 are
reader-exact, comprising six masked GDT781 targets and eight external fields;
six are reader-nonexact and never vote. The external fields revise five
working cards and retain one. No form is erased into a generic action phrase.

| whole | GDT781 default | GDT782 default | action | confidence | reader outcome |
|---|---|---|---|---|---|
| `cheedaiin` | Trockenmenge, Mittelstufe | **Trockenmenge, Endstufe** | REVISE | C1_MANUAL_STAGE_TIEBREAK_C0_IDENTITY | 3\_OF\_3\_REVISE\_SAME\_CANDIDATE |
| `chedor` | trockene Stoffportion | **getrockneter Arzneistoff** | REVISE | C1_GRAMMAR_COMPLEMENT_C0_IDENTITY | 2\_OF\_3\_SELECT\_REFINEMENT\_\_1\_KEEP\_PORTION\_DISSENT |
| `chockhar` | Trockenzubereitung | **erhitzter Ansatz** | REVISE | C0_SINGLE_EXTERNAL_FIELD_C0_IDENTITY | 3\_OF\_3\_REVISE\_HOT\_DIRECTION\_\_2\_OF\_3\_DEDUPLICATE\_PART |
| `keeor` | erhitzter Arzneistoff | **getrockneter Arzneistoff** | REVISE | C0_AGGRESSIVE_FIELD_TRANSFER_C0_IDENTITY | 2\_OF\_3\_SELECT\_DIRECT\_DRY\_\_1\_FIELD\_SCOPE\_DISSENT |
| `shdair` | Arzneistoff | **Arzneistoff** | KEEP | C1_ROLE_CONFIRMATION_C0_IDENTITY | 2\_OF\_3\_KEEP\_NARROW\_MATERIAL\_\_1\_MOIST\_PORTION\_DISSENT |
| `sheckhal` | feuchte Arzneimischung | **trockene Arzneimischung** | REVISE | C1_SINGLE_R2_PLUS_OLD_ANALOGY_C0_IDENTITY | 3\_OF\_3\_REVISE\_DRY\_DIRECTION\_\_2\_OF\_3\_RETAIN\_MATERIAL |

The most useful repair is syntactic rather than cosmetic. At `f105v.26`,
`or aiin` is already the registered exact working construction “drei
Portionen”. Keeping `chedor=trockene Stoffportion` would produce “drei
Portionen trockene Stoffportion”. GDT782 therefore makes the following
replaceable field reading:

> [lkl:?] | [sheeodees:Leservariante] | ⟨kalter Ansatz, Grad III⟩ | [otar:?] | [otal:?] | ⟦Menge: drei Portionen⟧ | ⟦Stoff: getrockneter Arzneistoff⟧ | [alkaiin:?] | [chs:?] | [alkaiin:?] | ⟪ry:Altglosse gesperrt⟫

This marked line is not plaintext: double brackets are working targets or
registered constructions, angle brackets are clean complete-whole donor
cards, vertical bars delimit record fields, and unresolved or quarantined
material remains visibly marked. The eight lines adjudicate aggregate cards;
they do not license the target defaults at those external positions.

## Eight target-external fields

| target | locus | immediate left | immediate right | clean axes within R3 | exact construction |
|---|---|---|---|---|---|
| `keeor` | `f17v.22` | chey=DRY|MIDDLE_STAGE | cheeol=DRY|MATERIAL|END_STAGE | `DRY|PART|MATERIAL|MIDDLE_STAGE|END_STAGE` | NONE |
| `sheckhal` | `f83v.20` | tedy=NONEXACT | sheeckhy=OPEN_EXACT | `DRY|MATERIAL|MIDDLE_STAGE` | NONE |
| `cheedaiin` | `f86v3.27` | cheeor=DRY|AMOUNT|MATERIAL|END_STAGE | LINE_EDGE | `DRY|AMOUNT|MATERIAL|END_STAGE` | NONE |
| `chockhar` | `f104r.18` | or=AMOUNT|MATERIAL | otalkshedy=NONEXACT | `HOT|AMOUNT|MATERIAL|LEVEL_II` | NONE |
| `chedor` | `f105v.26` | aiin=AMOUNT | alkaiin=OPEN_EXACT | `AMOUNT|MATERIAL` | drei Portionen |
| `shdair` | `f106v.32` | polos=NONEXACT | sheky=HOT|MOIST|PROCESS|MIDDLE_STAGE | `HOT|MOIST|AMOUNT|PROCESS|CLOSE|MIDDLE_STAGE|END_STAGE` | NONE |
| `cheedaiin` | `f107r.10` | sheal=MOIST|MATERIAL|MIDDLE_STAGE | chey=DRY|MIDDLE_STAGE | `DRY|MOIST|MATERIAL|MIDDLE_STAGE` | NONE |
| `cheedaiin` | `f112v.24` | ckhedy=PREPARATION|CLOSE|MIDDLE_STAGE|END_STAGE | cheedy=NONEXACT | `PREPARATION|CLOSE|MIDDLE_STAGE|END_STAGE` | NONE |

The three `cheedaiin` fields leave MIDDLE and END tied 2:2; the line-final
DRY/AMOUNT/END field and the earlier GDT748 external END series provide only
the manual tiebreak toward `Trockenmenge, Endstufe`. `keeor` sits in one dense
dry/material field, which supports a DRY/MATERIAL display without directly
excluding the orthogonal HOT axis. `sheckhal` has one clean R2 dry/material
donor that does oppose its old MOIST direction. In both cases, transferring
DRY into the target remains an explicitly aggressive C0/C1 working choice. `chockhar`
has only one outside occurrence, so its
`erhitzter Ansatz` revision remains C0 despite the useful HOT/II plus portion
frame. `shdair` stays the narrower `Arzneistoff`: one reader preferred
`feuchte Stoffportion`, but the moisture/process material follows the target
and need not be lexical content of the target itself.

## Deliberately preserved disagreement

Three readings were retained: a field-grammar reader, a historical apothecary
reader, and a surface-first census reader. They agree on the directional
revision for four cards. The census reader would retain a portion in
`chedor`, while the other two remove it to avoid doubling the adjacent amount
construction. It would also move `shdair` to a moist portion; the other two
keep the narrower material head because the moist/process field is
post-target. The dissent remains in the public assessment table.

## Renderer impact

The six target spans remain the same six exact, already consumed GDT781
spans. Five displayed defaults change and one is confirmed. Therefore the
full renderer remains 270/376 contextual, 106 fallback and 230 uniquely
consumed right tokens. No unrelated row changes its inherited value,
precedence or consumption.

## Leakage and evidence hygiene

Every target token was removed before its field was read. No other cohort
target occurs within radius three. Within that scored radius, one field
contains `cheeor`, an old clean whole that was also an analogy source for the
different cohort target `chedor`; it was never an analogy source for
`cheedaiin`, and the scorecard publishes a sensitivity with that cross-cohort
donor removed. A second cross-cohort source, `cheor`, is visible only at
distance four on the `sheckhal` line and contributes no field vote. Nonexact rows,
source-composed cards and literal powder/seed/root/wood remnants are visible
but cannot vote as clean donors. In particular, the distant `okeol` context is
shown only with GDT754's later `Wärme-/Mittelstufenfeld; genaue Funktion und
Träger offen` whole-form hypothesis. Its obsolete source-built “Grundansatz …
erwärmt” prose is retained only in the provenance column and contributes no
field vote.

The reader also takes the later GDT768 whole-form display for `cthy` as
`Blattgut`; it does not revive the older `CTH-Drogenmaterial` wording.

The clean pool reconstructs 770
readings over 769 complete
surfaces. Historical pharmacy evidence contributes only a mixed
quality/material/degree and amount/ingredient record architecture; no
historical spelling is matched to EVA.

## Claim ceiling

These are concrete, replaceable complete-whole renderer defaults, not decoded
words. GDT782 confirms zero lexemes, plaintext clauses, numbers, units,
specific substances or EVA component values. It opens no new page, image,
OCR or transcription; `f84` and `f84r` remain sealed.

## Reproduction

```bash
python3 -B experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/run.py
python3 -B experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/artifacts/GDT782_GDT388_EXTERNAL_FIELD_PACKET.tsv
```

The independent validator byte-replays the runner-owned artifacts and this
report. The 5 changed target patches and the retained
`shdair` patch are fully enumerated.
