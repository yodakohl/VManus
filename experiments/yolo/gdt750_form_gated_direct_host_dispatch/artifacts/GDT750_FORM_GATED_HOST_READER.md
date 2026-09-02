# GDT750 form-gated direct-host reader

The direct-host rule alone fails. The active rule requires a complete-form
distance-one host, a distance-one form prior supported by at least two
reference wholes, an immediate non-CLOSE contact, and no axis conflict.

## Calibration

| variant | positions | TP | FP | precision | recall | disposition |
|---|---:|---:|---:|---:|---:|---|
| V0_DIRECT_RAW_R1 | 342 | 203 | 371 | 0.354 | 0.104 | REJECT_DIRECT_HOST_TRANSFER |
| V1_DIRECT_NO_CLOSE_R1 | 310 | 186 | 331 | 0.360 | 0.095 | REJECT_DIRECT_HOST_TRANSFER |
| V2_D1_MULTI_FORM_R1_NO_CLOSE_ACTIVE | 15 | 19 | 0 | 1.000 | 0.010 | ACTIVE_OCCURRENCE_RENDERER |
| V3_D1_MULTI_FORM_R2_NO_CLOSE_DISCOVERY | 24 | 28 | 0 | 1.000 | 0.014 | DISCOVERY_ONLY_RADIUS_TWO |
| V4_D2_MULTI_FORM_R1_NO_CLOSE_SENSITIVITY | 64 | 67 | 21 | 0.761 | 0.034 | SENSITIVITY_ONLY_DISTANCE_TWO |
| V5_D2_MULTI_FORM_R2_NO_CLOSE_SENSITIVITY | 97 | 101 | 30 | 0.771 | 0.052 | SENSITIVITY_ONLY_DISTANCE_TWO |

## Seventeen complete forms

### `chdy` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `DRY`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `cheey` — A1_ACTIVE_SINGLE_OCCURRENCE_FORM_GATED_HOST

- GDT749 prior: `DRY`; distance-one form prior: `DRY|END_STAGE`
- Active positions/pages: 1/1; axes: `END_STAGE:1`
- Decision: Speak only the listed occurrence axes; do not globalize them beyond the form-gated direct-host positions.
  - `f102v2.38`: **End-/Vollstufe**; host `1:ckheey:END_STAGE:d1`; `dar cheey ckheey qokeor okey chos sho ykeey okeeo rain`

### `cheky` — A1_ACTIVE_SINGLE_OCCURRENCE_FORM_GATED_HOST

- GDT749 prior: `MIDDLE_STAGE`; distance-one form prior: `DRY|END_STAGE`
- Active positions/pages: 1/1; axes: `DRY:1`
- Decision: One active DRY occurrence rivals the former MIDDLE_STAGE default; global stage remains open.
  - `f66v.8`: **trockener Zustand**; host `1:chety:COLD|DRY:d1`; `dchekeedy cheody qokchdy qokol keedy cheky chety kody`

### `cheol` — A3_ACTIVE_CROSS_PAGE_FORM_GATED_HOST

- GDT749 prior: `DRY`; distance-one form prior: `DRY`
- Active positions/pages: 2/2; axes: `DRY:2`
- Decision: Speak only the listed occurrence axes; do not globalize them beyond the form-gated direct-host positions.
  - `f87r.15`: **trockener Zustand**; host `1:cheos:DRY:d1`; `shos cheol cheos ckhey saiin qockheo ldaiin`
  - `f88r.10`: **trockener Zustand**; host `-1:cheos:DRY:d1`; `qokeol cheol saiin cheos cheol doleeey or cheom cheojam`

### `kchdy` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `HOT`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `lkeey` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `HOT`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `okal` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `HOT`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `okechy` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `HOT`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain GDT749's rivalized global working card without an occurrence renderer.

### `okedy` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `HOT`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `okeey` — A3_ACTIVE_CROSS_PAGE_FORM_GATED_HOST

- GDT749 prior: `HOT`; distance-one form prior: `HOT|END_STAGE`
- Active positions/pages: 14/10; axes: `HOT:13|END_STAGE:13`
- Decision: At active positions render a hot end-state when both axes occur; retain HOT/END as a complete-form role, not a lexeme.
  - `f102v2.36`: **heißer Zustand**; host `-1:okey:HOT|MIDDLE_STAGE:d1`; `okeeor cheey okeey sor eeey okey okey okeey qokeor`
  - `f103r.27`: **heißer Zustand an der End-/Vollstufe**; host `1:qokeey:HOT|END_STAGE:d1`; `qokechy okeey qokeey lkeeody sheey qokeey lkeol tchey qokeey okeey qokaly`
  - `f103r.50`: **heißer Zustand an der End-/Vollstufe**; host `-1:qokeey:HOT|END_STAGE:d1`; `ssheey l shey qol cheey chey qokeey okeey qokain cheey qotain`
  - `f103v.4`: **heißer Zustand an der End-/Vollstufe**; host `-1:qokeey:HOT|END_STAGE:d1`; `y cheey qokeey okeey lkees ol qoteedy ykeedy`
  - `f108r.27`: **heißer Zustand an der End-/Vollstufe**; host `1:qokeey:HOT|END_STAGE:d1`; `ychedain orcheory qoaiin okeey qokeey chdal okedy qokedy okedam chdy`
  - `f108r.42`: **heißer Zustand an der End-/Vollstufe**; host `1:qokeey:HOT|END_STAGE:d1`; `okeey qokeey qokeedy qokeey chedal chedy qokeey okeedain otain oolals`
  - `f108r.5`: **End-/Vollstufe**; host `-1:oteey:COLD|END_STAGE:d1`; `tchokedy chey oteey okeey lkededy okche y pchofar cheo pchedy qotedy otol`
  - `f112r.13`: **heißer Zustand an der End-/Vollstufe**; host `-1:qokeey:HOT|END_STAGE:d1`; `sor aiin chdy ches qokeey okeey otaiin chcthy oteey dy`
  - `f112r.9`: **heißer Zustand an der End-/Vollstufe**; host `1:qokeey:HOT|END_STAGE:d1`; `saiin ol okeey qokeey y chedy teedy qokchy qokar y`
  - `f17v.20`: **heißer Zustand an der End-/Vollstufe**; host `-1:ykeey:HOT|END_STAGE:d1`; `ykeey okeey cheor chol sho odaiin`
  - `f3r.14`: **heißer Zustand an der End-/Vollstufe**; host `1:qokeey:HOT|END_STAGE:d1`; `chor qodair okeey qokeey`
  - `f76r.16`: **heißer Zustand an der End-/Vollstufe**; host `-1:qokeey:HOT|END_STAGE:d1`; `qotes chedy shckhy qokeey okeey kain checkhy qokeedy qotey qotain chekair`
  - `f79r.31`: **heißer Zustand an der End-/Vollstufe**; host `-1:ykeey:HOT|END_STAGE:d1`; `polshey oltshedy sheol ykeey okeey cheor sheedy ol`
  - `f81v.11`: **heißer Zustand an der End-/Vollstufe**; host `-1:qokeey:HOT|END_STAGE:d1`; `yshey qokeey okeey oky ykeey qoky oky lky olchy ky dsholyd`

### `olkaiin` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `HOT`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `olkar` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `HOT`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `oty` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `COLD`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `qokaiin` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `HOT`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `qokedy` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `END_STAGE`; distance-one form prior: `NONE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain the prior only as a silent hypothesis.

### `sheey` — A1_ACTIVE_SINGLE_OCCURRENCE_FORM_GATED_HOST

- GDT749 prior: `END_STAGE`; distance-one form prior: `MOIST|END_STAGE`
- Active positions/pages: 1/1; axes: `MOIST:1|END_STAGE:1`
- Decision: Speak only the listed occurrence axes; do not globalize them beyond the form-gated direct-host positions.
  - `f111v.27`: **feuchter/eingeweichter Zustand an der End-/Vollstufe**; host `1:tsheey:COLD|MOIST|END_STAGE:d1`; `ol sheey tsheey alkar sheey otain ches shy qokl chey qoklcheor ldar llo`

### `qochey` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST

- GDT749 prior: `DRY|MIDDLE_STAGE`; distance-one form prior: `DRY|MIDDLE_STAGE`
- Active positions/pages: 0/0; axes: `NONE`
- Decision: No active direct host; retain GDT749's rivalized global working card without an occurrence renderer.
