# GDT669 — V46 concrete workshop register

Status: `PASS_165_TARGET_POSITIONS__V46_CONCRETE_RECIPE_REGISTER`

## Result

GDT669 closes all 37 forms and 165 occurrences in the fixed V45 frontier. The
forms occur on 165 lines across 95 already released pages. No page or image is
added.

| Measure | V45 | V46 | Change |
|---|---:|---:|---:|
| known token positions | 23,832 | 23,997 | +165 |
| unknown token positions | 8,507 | 8,342 | −165 |
| complete multi-token lines | 1,153 | 1,191 | +38 |
| reader-stable complete lines | 299 | 306 | +7 |
| one-hole lines | 180 | 170 | −10 |
| reader-stable one-hole lines | 38 | 38 | 0 |
| working glossary surfaces | 1,350 | 1,387 | +37 |
| dictionary entries | 2,022 | 2,071 | +49 |

The 49 dictionary additions are 37 surface defaults and twelve local practical
rendering cards. They are not 49 asserted plaintext words.

## Architecture

The final deck has 35 role-composed cards and two learned exact wholes. It
reuses all 54 inherited roles and adds two narrow preparation heads:

- `OY_PREP_BASE=oy`: Ansatz in Grundform, supported by naked `oy` (12 panel
  occurrences), `oychey`, and target `oytor`;
- `OKY_HOT_PREP_BASE=oky`: heißer Ansatz in Grundform, supported by naked
  `oky` (89 occurrences) and target `okytaiin`.

These blocks solve an internal-`y` scope problem without turning `y` into a
general infix. They may not be exported to arbitrary `oy`/`oky` substrings.

## Two learned reader aliases

`lkchdal` and `eeckhy` are deliberately not decomposed.

- At f105v.13, ZL3b has `lkchdal`; IT2a and RF1b both have `lkeedal`. The V46
  default “Holzdroge vollständig erhitzen und Rohdroge I abmessen” follows the
  known reader family, while ZL3b dispatch remains
  `LEARNED_LKCHDAL_WHOLE`.
- At f51r.7, ZL3b has `eeckhy`; both other readers have `chckhy`. The concrete
  default is “Arzneikompositum trocken in Grundform,” but no invisible
  `CH_DRY` atom is inserted into the ZL3b surface.

This is the mixed-codebook model in its useful form: productive technical
stems where spelling supports them, memorized whole cards where aligned
readers expose a genuine alias.

## The moisture spine

The most frequent new family is internally consistent:

| surface | positions | composition | V46 default |
|---|---:|---|---|
| `shear` | 22 | `SH_MOIST+E_MIDDLE+AR_FRACTION_I` | erste Fraktion bis zur Mittelstufe einweichen |
| `sh` | 14 | `SH_MOIST` | einweichen |
| `shedaiin` | 10 | `SH_MOIST+E_MIDDLE+D_MEASURE+AIIN_III` | drei Dosen bis zur Mittelstufe eingeweichter Droge |
| `shek` | 10 | `SH_MOIST+E_MIDDLE+K_HOT` | bis zur Mittelstufe einweichen und erhitzen |

Free `sh` is a short imperative, not a material name. Nine of its fourteen
positions retain the free action. Three use a visibly aligned local reader
merge; the remaining contexts are recorded separately. No competing `SHE`
stem is needed.

## Material and operation corrections

`olkair` now obeys the established initial O+L rule:

`O_PREP+L_WOOD+K_HOT+AIR_FRACTION_II`

It is “zweite erhitzte Holzdrogenfraktion im Ansatz,” not a bound
`OL_MATERIAL` form placed illegally at the beginning.

`tcheodal` retains every visible operation in order:

`T_COLD+CH_DRY+E_MIDDLE+O_PREP+D_MEASURE+AL_RAW_I`

The manual rendering is: “Kühle ab, trockne bis zur Mittelstufe, setze an und
miss Rohdroge I ab.” The earlier temptation to reorder this into smoother
modern prose is rejected.

Other useful concrete cards include `cthal` “Kraut- oder Blattdroge aus
Rohdroge I,” `dals` “eine Charge Rohdroge I abmessen,” `dalar` “erste Fraktion
Rohdroge I abmessen,” `lkeol` “Holzdrogenstoff bis zur Mittelstufe erhitzen,”
and `oeees` “Ansatzcharge der letzten Stufe.”

## Passage examples

Twenty source-exact passages were manually smoothed and kept separate from the
deterministic token renderer.

An independent final reader accepted fourteen unchanged and corrected six
without changing a card: one state had been turned into an extra command,
three process directions had been flattened, one alternative material reading
had disappeared, and one implicit object was ungrammatical. A root consistency
pass caught the same directional flattening in two further lines. All eight
corrections are applied in the sealed manual-passage source.

`f50r.6`

> Erhitze hiervon auf Stufe II; weiche die erste Fraktion bis zur Mittelstufe
> ein. Grundansatz; heiß und bis zur mittleren Trockenstufe gebracht; Rohdroge
> I leicht erhitzt im Ansatz; kalte Drogenportion; eine Portion vollständig
> getrockneter Droge; Holzdrogenansatz vollständig erhitzt und abgeschlossen;
> drei Maße; leicht erhitzter Ansatz.

`f20r.3`

> Bis zur Kühlendstufe; Trockenansatz; Trockenansatz, Dosis III; feuchter
> Ansatz. Nimm leicht getrocknete Droge; bis zur mittleren Trockenstufe
> gebracht. Kühle ab, trockne bis zur Mittelstufe, setze an und miss Rohdroge I
> ab; miss die erste Fraktion
> Rohdroge I ab.

`f56v.7`

> Erhitze, trockne und setze an; erhitze erneut, trockne erneut und schließe
> ab. Trockengut; Feuchtgut; Trockengut. Trockne den kalten Ansatz und schließe
> den Posten ab.

These are executable working readings, but their fluency is not proof of
plaintext identity.

## Next frontier

V46 exposes 28 new one-hole lines with 28 distinct surfaces. The ten leading
full-panel counts are:

| surface | positions |
|---|---:|
| `otair` | 22 |
| `ytey` | 10 |
| `cphy` | 9 |
| `chekain` | 7 |
| `chedol` | 5 |
| `shkaiin` | 5 |
| `kchaiin` | 4 |
| `qoiiin` | 4 |
| `otodar` | 3 |
| `ka` | 2 |

The next round should start with `otair`, then test the `ytey`, `cph`, and
`k/ain` families against the unchanged 56-role sheet before adding any block.

## Limits

V46 is a concrete exploratory work theory, not a decipherment. It establishes
neither a source language nor phonetic values, and it does not identify water,
wine, oil, salt, a vessel, a specific plant, illness, patient, or cure unless a
separate licensed card supplies that information. Structural tags and German
workshop renderings remain distinct and replaceable.
