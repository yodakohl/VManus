# GDT212 — readable bath illustration/text grounding

## Outcome

**SETTING_HYDRAULICS_WEAKLY_VISUALLY_GROUNDED_INDICATION_FIELDS_NOT_RECOVERED**

The full 32-entry Morgan/ALIM overlap sharpens GDT210.  Readable bath
illustrations weakly expose access/setting and non-generic water organization,
but they do not reliably expose procedure, outcome, or the detailed indication
layer.  This is exactly the calibration needed before using q13 imagery as a
semantic guide.

## Paired role tests

| Visual catalogue feature | Readable text role | 2x2 `a/b/c/d` | Risk difference | one-sided p | four-pair adjusted p | Result |
|---|---|---:|---:|---:|---:|---|
| ACCESS_OR_SETTING | LOCATION_ACCESS | 13/7/4/8 | +0.317 | 0.0848 | 0.3393 | WEAK_VISUAL_GROUNDING |
| NON_GENERIC_WATER_SYSTEM | HYDRAULIC_PHYSICAL | 14/2/9/7 | +0.312 | 0.0567 | 0.2268 | WEAK_VISUAL_GROUNDING |
| SPECIFIC_USE_ACTION | PROCEDURE_CAUTION | 10/10/10/2 | -0.333 | 0.9905 | 1.0000 | NOT_VISUALLY_GROUNDED |
| BED_OR_DEPARTURE_NARRATIVE | OUTCOME_TESTIMONY | 1/7/5/19 | -0.083 | 0.8515 | 1.0000 | NOT_VISUALLY_GROUNDED |

No pair survives the four-pair correction.  The two intended-direction leads
are nevertheless coherent and small: visible access/setting raises readable
LOCATION_ACCESS prevalence by 0.317, and a visible
non-generic water system raises HYDRAULIC_PHYSICAL prevalence by
0.312.  Their leave-one-entry-out gains are only
+0.632 and +1.285 bits over 32
decisions.

The treatment/action bridge fails directionally: textual procedure/caution is
more common when the catalogue lacks a specific depicted action.  Outcome
testimony is likewise not recovered by narrative-looking bed/departure scenes.
Most importantly, INDICATION occurs in all 32 texts, while an explicit bodily
condition cue appears in only 14/32 catalogue scenes.  Pictures
therefore omit much of the medically important textual payload.

## Consequence for q13

The strongest defensible transfer is narrower than “the figures tell us the
disease.”  Pools, streams, caves, stairs, enclosures and connecting structures
can weakly support a `SETTING_OR_HYDRAULIC_DESCRIPTION` layer.  Figures and
gestures cannot, on this calibration, identify an indication, procedure, or
outcome field.  Thus GDT210's therapeutic-balneological page theory remains
plausible, but GDT212 shifts the actionable visual anchor toward the physical
hydraulic/access layer and away from patient/disease glossing.

No Voynich text was scored in GDT212, no host was assigned a role, and no word,
language, plaintext or translation follows.  No f84 source or payload was
accessed.
