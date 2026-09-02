# GDT740 direct-attachment reader

These remain occurrence-scoped working renders, not plaintext translations.
Direct contacts are attachment-eligible but can lose to a boundary or flank conflict.
Radius-two contacts are held by default; two enumerated same-direction relays survive.

## Attachment result

Across 95 formerly specific targets: ATTACHED_PROVISIONAL_REVERSE=13, ATTACHED_STRONG=6, ATTACHED_SUPPORTED=32, DIRECT_BOUNDARY_HOLD=1, DIRECT_COMPONENT_CONFLICT_OPEN=2, DIRECT_FLANK_CONFLICT_OPEN=1, KEEP_CARRIER_ONLY=3, MODE_DOWNGRADED_OPEN=5, NEAR_ONLY_HOLD=30, RELAY_R2_MANUAL=2.

## Twelve-form profile

| whole | occurrences | axis kept | carrier kept | fully open | changed | common render |
|---|---:|---:|---:|---:|---:|---|
| `lain` | 4 | 2 | 2 | 1 | 0 | interner Trockenheitsgrad II des Materials |
| `lcheedy` | 6 | 0 | 2 | 4 | 3 | Zustandsstufe II; Zustandsachse offen; Träger offen |
| `lcheol` | 8 | 1 | 1 | 6 | 2 | Statusfeld; Zustandsachse offen; Träger offen |
| `lkaiin` | 42 | 9 | 13 | 28 | 8 | Skalarstufe III; Dimension offen |
| `lkain` | 27 | 4 | 5 | 21 | 8 | Skalarstufe II; Dimension offen |
| `lkar` | 29 | 6 | 3 | 22 | 3 | Skalarstufe I; Dimension offen |
| `lsheedy` | 4 | 0 | 0 | 4 | 3 | Zustandsstufe II; Zustandsachse offen; Träger offen |
| `pcheol` | 10 | 1 | 3 | 7 | 2 | Status-Eintrag; Zustandsachse offen; Träger offen |
| `rain` | 14 | 5 | 6 | 6 | 6 | Skalarstufe II; Dimension offen; interner Rückbezug |
| `rsheedy` | 2 | 0 | 0 | 2 | 1 | Zustandsstufe II; Zustandsachse offen; interner Rückbezug; Träger offen |
| `sain` | 53 | 7 | 7 | 43 | 12 | Skalarstufe II; Dimension offen; Eintrag |
| `skaiin` | 3 | 1 | 1 | 2 | 1 | Skalarstufe III; Dimension offen |

## Twenty cached passage checks

### G739-R01 — f111v.31 (S/B)

- EVA line: `pochey oteain chekain cheal lain chey qokain chey lkain chal ldy llm`
- Targets: **lain → interner Trockenheitsgrad II des Materials || lkain → Skalarstufe II; Dimension offen**
- Attachment: lain=ATTACHED_SUPPORTED || lkain=NO_SELECTED_HOST
- Manual check: KEEP_FIRST_TARGET_ONLY — Direct cheal-lain supports the first target; the later lkain must not borrow it.
- Cellwise audit display: [pochey:?]; [oteain:?]; bis zur Mittelstufe trocknen, dann auf Stufe II erhitzen; Rohstoffklasse I, bis zur Mittelstufe getrocknet; interner Trockenheitsgrad II des Materials; [chey:?]; [qokain:?]; [chey:?]; Skalarstufe II; Dimension offen; [chal:?]; [ldy:?]; [llm:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R02 — f46r.13 (H/B)

- EVA line: `ar akaiin shol okeey chol dar ols lain y`
- Targets: **lain → interne Skalarstufe II des Materials; Dimension offen**
- Attachment: lain=ATTACHED_SUPPORTED
- Manual check: KEEP_CARRIER_ONLY — Direct ols-lain plausibly supplies a broad material carrier but no scalar axis.
- Cellwise audit display: [ar:?]; heiße Rohstoffportion, Stufe III; [shol:?]; [okeey:?]; [chol:?]; [dar:?]; Drogenstoffposten; interne Skalarstufe II des Materials; Dimension offen; [y:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R03 — f104v.20 (S/B)

- EVA line: `or sheeo lcheedy qokeey qochey qotcheedy qotchedy qokol chor chorol chdar otam`
- Targets: **lcheedy → Zustandsstufe II der Zubereitung; Zustandsachse offen**
- Attachment: lcheedy=KEEP_CARRIER_ONLY
- Manual check: KEEP_CARRIER_ONLY — Direct preparation carrier is coherent; result/end is not independently attached and returns to state.
- Cellwise audit display: [or:?]; vollständig eingeweichter Ansatz; Zustandsstufe II der Zubereitung; Zustandsachse offen; vollständig erhitzt; [qochey:?]; kalt und trocken, Endstufe erreicht; abgeschlossen; [qotchedy:?]; erhitzen; [chor:?]; [chorol:?]; [chdar:?]; [otam:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R04 — f107v.12 (S/B)

- EVA line: `qokeey lcheol chol kaiin olkal shedy qokaly odar choty qokaiin otam`
- Targets: **lcheol → Statusfeld; Zustandsachse offen; Träger offen**
- Attachment: lcheol=NO_SELECTED_HOST
- Manual check: KEEP_OPEN — Hot neighbors do not license the favored dry axis.
- Cellwise audit display: vollständig erhitzt; Statusfeld; Zustandsachse offen; Träger offen; [chol:?]; heiß, Grad III; [olkal:?]; [shedy:?]; erhitze Rohdroge I leicht und schließe ab; Anteil I abmessen; kalter Trockenansatz; [qokaiin:?]; [otam:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R05 — f78v.17 (B/B)

- EVA line: `qol sheedy qol lcheol lchdy dchdy da qar olkal dy`
- Targets: **lcheol → Statusfeld; Zustandsachse offen; Träger offen**
- Attachment: lcheol=NEAR_ONLY_HOLD
- Manual check: DOWNGRADE_RADIUS_TWO — The dry host lies behind an independently emitted intervening cell.
- Cellwise audit display: [qol:?]; [sheedy:?]; [qol:?]; Statusfeld; Zustandsachse offen; Träger offen; [lchdy:?]; Trockendroge abmessen und fertigstellen; [da:?]; [qar:?]; [olkal:?]; [dy:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R06 — f103r.9 (S/B)

- EVA line: `oteeos ar cheal okeey shey lkaiin shey lkeor otaiin shedy otey l dy okeedaram`
- Targets: **lkaiin → Skalarstufe III; Dimension offen**
- Attachment: lkaiin=NO_SELECTED_HOST
- Manual check: KEEP_OPEN — Moist direct context and hot radius-two context do not select a clean axis.
- Cellwise audit display: [oteeos:?]; [ar:?]; Rohstoffklasse I, bis zur Mittelstufe getrocknet; [okeey:?]; [shey:?]; Skalarstufe III; Dimension offen; [shey:?]; [lkeor:?]; [otaiin:?]; [shedy:?]; bis zur Mittelstufe abgekühlter Ansatz; [l:?]; [dy:?]; [okeedaram:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R07 — f80r.52 (B/B)

- EVA line: `sol tl shey qoklcheey lkaiin ol olor aiin y daiin cheol kain`
- Targets: **lkaiin → Skalarstufe III; Dimension offen**
- Attachment: lkaiin=NO_SELECTED_HOST
- Manual check: KEEP_OPEN — No selecting host reaches the target.
- Cellwise audit display: [sol:?]; [tl:?]; [shey:?]; [qoklcheey:?]; Skalarstufe III; Dimension offen; [ol:?]; Zutat; [aiin:?]; [y:?]; [daiin:?]; [cheol:?]; [kain:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R08 — f76r.44 (T/B)

- EVA line: `poleedaran shckhy qoty ykar alol lkaiin ol shedy otain okar opar kolpy`
- Targets: **lkaiin → Skalarstufe III des Materials; Dimension offen**
- Attachment: lkaiin=ATTACHED_SUPPORTED
- Manual check: KEEP_CARRIER_ONLY — Direct material carrier survives; the amount cue lies behind another unit.
- Cellwise audit display: [poleedaran:?]; [shckhy:?]; [qoty:?]; nimm hiervon die erste erhitzte Drogenfraktion; Drogenstoff aus Rohdroge I; Skalarstufe III des Materials; Dimension offen; [ol:?]; [shedy:?]; [otain:?]; [okar:?]; [opar:?]; [kolpy:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R09 — f76r.9 (T/B)

- EVA line: `shed al shckhy r ain chcphedy ain olkeey lkar ain otchy lkain chedy dar daly`
- Targets: **lkar → Skalarstufe I; Dimension offen || lkain → Skalarstufe II; Dimension offen**
- Attachment: lkar=NO_SELECTED_HOST || lkain=NO_SELECTED_HOST
- Manual check: KEEP_OPEN — Quality amount and part cues do not form one target microentry.
- Cellwise audit display: Einweichen bis zur mittleren Stufe abschließen; [al:?]; [shckhy:?]; [r:?]; [ain:?]; Arzneikompositum bis zur Mittelstufe trocknen und abschließen; [ain:?]; [olkeey:?]; Skalarstufe I; Dimension offen; [ain:?]; [otchy:?]; Skalarstufe II; Dimension offen; [chedy:?]; [dar:?]; abgewogener Rohstoffposten I, Grundform
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R10 — f86v3.20 (C/B)

- EVA line: `lshodair ykcho dar chody ykeeody qochey chckhey lkar ary`
- Targets: **lkar → Mengen-/Portionsstufe I des Materialteils**
- Attachment: lkar=ATTACHED_PROVISIONAL_REVERSE
- Manual check: KEEP_DIRECT — The immediate scalar-to-material contact is locally coherent but remains reverse-order provisional.
- Cellwise audit display: [lshodair:?]; [ykcho:?]; [dar:?]; [chody:?]; [ykeeody:?]; [qochey:?]; Arzneikompositum: bis zur Mittelstufe getrocknet; Mengen-/Portionsstufe I des Materialteils; Drogenfraktion I, abgeschlossen
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R11 — f76r.52 (T/B)

- EVA line: `olsheed qokedy qokeedy qokedy lkedy lsheedy okar shedy otain`
- Targets: **lsheedy → Zustandsstufe II; Zustandsachse offen; Träger offen**
- Attachment: lsheedy=MODE_DOWNGRADED_OPEN
- Manual check: DOWNGRADE_MODE_ONLY — Endpoint best-fit has no attached result host and returns to state with open axis and carrier.
- Cellwise audit display: [olsheed:?]; [qokedy:?]; [qokeedy:?]; [qokedy:?]; [lkedy:?]; Zustandsstufe II; Zustandsachse offen; Träger offen; [okar:?]; [shedy:?]; [otain:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R12 — f83r.7 (B/B)

- EVA line: `solshed lsheedy qeeedy qoky o qol rsheedy qokedy qoteedy qoteedy`
- Targets: **lsheedy → Zustandsstufe II; Zustandsachse offen; Träger offen**
- Attachment: lsheedy=NO_SELECTED_HOST
- Manual check: KEEP_OPEN — Thermal context supplies neither moist axis nor carrier.
- Cellwise audit display: [solshed:?]; Zustandsstufe II; Zustandsachse offen; Träger offen; [qeeedy:?]; leicht erhitzt; [o:?]; [qol:?]; [rsheedy:?]; [qokedy:?]; vollständig abgekühlt, abgeschlossen; vollständig abgekühlt, abgeschlossen
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R13 — f100r.12 (P/A)

- EVA line: `pcheol sheod qocpheeckhy shodol da oto choos sheey cho s`
- Targets: **pcheol → Status-Eintrag; Zustandsachse offen; Träger offen**
- Attachment: pcheol=NO_SELECTED_HOST
- Manual check: KEEP_OPEN_ENTRY — Line-initial status form has no eligible attached payload.
- Cellwise audit display: Status-Eintrag; Zustandsachse offen; Träger offen; [sheod:?]; [qocpheeckhy:?]; [shodol:?]; [da:?]; [oto:?]; [choos:?]; [sheey:?]; Trockenansatz; [s:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R14 — f82v.11 (B/B)

- EVA line: `pcheol dar qokeey cheeky qokal dal shedy pchdy rol qotedy rol`
- Targets: **pcheol → Status-Eintrag; Zustandsachse offen; Träger offen**
- Attachment: pcheol=NO_SELECTED_HOST
- Manual check: KEEP_OPEN_ENTRY — Measure and heat context supplies neither favored dry axis nor direct carrier.
- Cellwise audit display: Status-Eintrag; Zustandsachse offen; Träger offen; [dar:?]; vollständig erhitzt; vollständig getrocknet, dann leicht erhitzt; [qokal:?]; [dal:?]; [shedy:?]; [pchdy:?]; [rol:?]; bis zur Mittelstufe abgekühlt, abgeschlossen; [rol:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R15 — f116r.36 (S/B)

- EVA line: `qokeey rain shey okeey lkain l dain chey sheckhy qy qokl ain`
- Targets: **rain → Heißgrad II; interner Rückbezug || lkain → Skalarstufe II; Dimension offen**
- Attachment: rain=ATTACHED_SUPPORTED || lkain=NO_SELECTED_HOST
- Manual check: KEEP_RAIN_ONLY — Direct qokeey-rain quality-grade contact survives; later lkain remains open.
- Cellwise audit display: vollständig erhitzt; Heißgrad II; interner Rückbezug; [shey:?]; [okeey:?]; Skalarstufe II; Dimension offen; [l:?]; [dain:?]; [chey:?]; [sheckhy:?]; [qy:?]; [qokl:?]; [ain:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R16 — f77v.8 (B/B)

- EVA line: `qokeeey shedy qokeedy qodykey qokedy rsheedy taiiin sheol teedy yry`
- Targets: **rsheedy → Zustandsstufe II; Zustandsachse offen; interner Rückbezug; Träger offen**
- Attachment: rsheedy=NEAR_ONLY_HOLD
- Manual check: DOWNGRADE_RADIUS_TWO_AND_RESULT — Moist material lies beyond a separate token and endpoint best-fit does not independently support result mode.
- Cellwise audit display: [qokeeey:?]; [shedy:?]; [qokeedy:?]; [qodykey:?]; [qokedy:?]; Zustandsstufe II; Zustandsachse offen; interner Rückbezug; Träger offen; [taiiin:?]; feuchtes Material; vollständig abgekühlt, abgeschlossen; [yry:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R17 — f82r.31 (B/B)

- EVA line: `cheol ol rsheedy lchedy qoty lcheeor qokain cheedy lched`
- Targets: **rsheedy → Zustandsstufe II; Zustandsachse offen; interner Rückbezug; Träger offen**
- Attachment: rsheedy=NO_SELECTED_HOST
- Manual check: KEEP_OPEN — Dry-dominated context does not justify automatic moist speech.
- Cellwise audit display: [cheol:?]; [ol:?]; Zustandsstufe II; Zustandsachse offen; interner Rückbezug; Träger offen; [lchedy:?]; [qoty:?]; [lcheeor:?]; [qokain:?]; vollständig getrocknet, abgeschlossen; [lched:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R18 — f10v.1 (H/A)

- EVA line: `paiin daiin sheo pcheey qoty daiin cthor otydy sain`
- Targets: **sain → Skalarstufe II; Dimension offen**
- Attachment: sain=DIRECT_BOUNDARY_HOLD
- Manual check: BOUNDARY_HOLD — The radius-two amount cue and direct preparation cue both terminate at the intervening closure field.
- Cellwise audit display: [paiin:?]; [daiin:?]; Feuchtzubereitung; [pcheey:?]; [qoty:?]; [daiin:?]; eine Portion Pflanzendroge; kalter Ansatz in Grundform, fertig; Skalarstufe II; Dimension offen
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R19 — f58r.36 (S/A)

- EVA line: `skaiin shokal chockhy qoky chcthy ykeeshy shoekar`
- Targets: **skaiin → Qualitätsstufe III im heiß/feucht-Feld des Zubereitungsmaterials; Eintrag**
- Attachment: skaiin=ATTACHED_SUPPORTED
- Manual check: KEEP_DIRECT_HEADER_PAYLOAD — Direct line-initial target and following host form a plausible header-payload pair.
- Cellwise audit display: Qualitätsstufe III im heiß/feucht-Feld des Zubereitungsmaterials; Eintrag; Feuchtansatz aus heißem Rohstoff Klasse I, Anfangsstufe; [chockhy:?]; leicht erhitzt; [chcthy:?]; [ykeeshy:?]; [shoekar:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.

### G739-R20 — f111v.48 (S/B)

- EVA line: `psalar cheey qekal cheykaiin tain chal al skaiin okchedy opchdal opchy`
- Targets: **skaiin → Skalarstufe III; Dimension offen**
- Attachment: skaiin=NO_SELECTED_HOST
- Manual check: KEEP_OPEN — Weak and unclear neighbors leave the scalar dimension open.
- Cellwise audit display: [psalar:?]; [cheey:?]; [qekal:?]; [cheykaiin:?]; [tain:?]; [chal:?]; [al:?]; Skalarstufe III; Dimension offen; [okchedy:?]; [opchdal:?]; [opchy:?]
- Display note: semicolon-separated cellwise working defaults; no clause or attachment is implied outside the focal target.
