# GDT742 report — role-separated radius-two carrier relay

## Outcome

One small grammar change adds useful content without manufacturing a new
quality reading: a mixed AXIS+CARRIER contact may relay its carrier independently
when the frame, boundary and formal direction are clean, carrier coverage is
complete in both middle and host, and the competing axis has no continuity.

Across the complete inherited deck, this adds exactly two carrier roles and no
axis role:

| occurrence | local result added by GDT742 |
|---|---|
| `f77v.33 rain` | `[Carrier=MATERIAL; axis open]` |
| `f112r.36 sain` | `[Carrier=PREPARATION; axis open]` |

The visible German renderer says “Skalarstufe II des Materials; Dimension
offen; Abschlussbezug” and “Skalarstufe II der Zubereitung; Dimension offen;
Eintrag.” Only the carrier genitives are new here. `Skalarstufe II`, `Eintrag`
and `Abschlussbezug` are inherited renderer fragments, and MATERIAL/PREPARATION
are model tags rather than decoded manuscript words or literal ingredients.

## Why these two move

At `f77v.33`, the cached end frame is:

```text
qotal dal rain
```

The target requests MATERIAL; both middle and radius-two host carry the full
MATERIAL field, the formal H3 direction points toward that frame, the middle is
known/exact/open, and the candidate COLD axis does not pass through it.

At `f112r.36`, the cached initial frame is:

```text
sain ol checkhy
```

The target requests PREPARATION; middle and host both carry PREPARATION, the H2
direction agrees, and the quality axis again has no continuity. The longer
cached line continues with additional PREPARATION-tagged cells, but the rule
does not need that longer run to trigger.

These two contacts share one declared reduced role-isomorphic signature. The
signature deliberately normalizes away concrete carrier identity: one case is
MATERIAL and the other PREPARATION. Their pairing is useful model compression,
not an independent historical confirmation.

## Nearest held boundaries

The rule is not merely a lookup for two occurrences. It also stays silent at
the closest structural counterexamples in the 41-contact deck:

- D0062 has the same clean mixed-role geometry, but its requested
  PART+PREPARATION carrier is only partly present in the middle.
- D0166 is another initial `sain` mixed-role frame with matching direction and
  open boundary, but the middle carries no PREPARATION field.
- D0068 lacks middle carrier coverage and has conflicting quality content.
- D0015 has full carrier continuity but crosses a strict-head middle and lacks
  the admitted common frame/direction combination.

The independent validator reconstructs barrier, quality continuity and carrier
coverage from the atomic GDT741 columns and checks that all four remain held.

## The genuine D0075 alternative

D0075 should not be described as disproved. Its cached line begins:

```text
ykeeey lkain chckhy chokain chckhal sheckhedy ...
```

To the right of `lkain` lies a convincing PREPARATION-tagged run, so a forward
carrier binding is practically plausible. Against that reading, the inherited
H4 direction points left toward still-unknown `ykeeey`, while the rightward
quality relation is only partial rather than absent. At least two field readings
remain live: a reference/closure toward the preceding field or a boundary before
the following preparation run, versus direct forward binding into that run.

GDT742 therefore keeps both D0075 candidate roles inactive. `HOLD` means “not
promoted under the current direction-respecting grammar,” not “no PREPARATION
relation exists.” D0040 likewise suggests a future HOT-only intersection rather
than the full current axis, and D0184 remains behind a PROCESS/PASS middle.

## Renderer consequence

| channel | GDT741 | GDT742 |
|---|---:|---:|
| axis-specific positions | 36 | 36 |
| broad carrier-bound positions | 43 | 45 |
| positions with any specific channel | 56 | 58 |
| fully open positions | 146 | 144 |

Four rows of the original eight-role candidate deck remain inactive on three
targets: AXIS at D0040, AXIS+CARRIER at D0075, and AXIS at D0184. In addition,
the axis channels of the two newly carrier-bound targets remain open. This
distinction matters: GDT742 made two positions partly informative, not fully
decoded.

## Validation and ceiling

The independent validator recomputes all 41 radius-two decisions from atomic
fields, checks the 62 direct contacts are unchanged, verifies the exact two-row
delta across contact/candidate/renderer/focus/edge artifacts, rebuilds all
outputs byte-identically and confirms the GDT388 packet is `INVALID_PACKET`.

The field-continuation idea is compatible with compact late-medieval
table/recipe organization, but no historical witness identifies these EVA
forms, carrier tags or word order. GDT742 adds no word, component, plaintext,
ingredient, patient, species, disease, cure, unit, page, image or transcription.

## Next useful move

Use the same cached deck to test whether a longer uninterrupted same-carrier run
can ever override formal direction without pulling held negatives with it. The
test should focus on D0075 and all direction-reversed controls, while D0040's
HOT-only intersection remains a separate axis hypothesis. If neither extension
compresses more than its seed, keep those roles open and move from attachment
polish to concrete whole-field semantic bridges.

## Reproduction

```bash
python3 experiments/yolo/gdt742_r2_open_collision_adjudication/src/run.py
python3 experiments/yolo/gdt742_r2_open_collision_adjudication/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt742_r2_open_collision_adjudication/artifacts/GDT742_GDT388_TWO_CARRIER_RELAY_EDGE_PACKET.tsv
```

The final relation command is expected to return `INVALID_PACKET`.
