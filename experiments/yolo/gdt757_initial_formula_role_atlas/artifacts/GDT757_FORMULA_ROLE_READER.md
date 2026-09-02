# GDT757 formula-role reader

## Current compact dictionary

These are complete-form working readings. They do not decompose EVA spelling.

| whole | primary candidate | role | placement | rivals | confidence |
|---|---|---|---|---|---|
| `pchor` | **nimm** | `RECIPE_OPENING` | P-start 6/7; P-end 0/7 | Zubereitung / Rezept / für / gegen | `C1_PLACEMENT_CONSTRAINED` |
| `ychor` | **ferner / ebenso** | `ITEM_CONTINUATION` | P-start 0/13; P-end 3/13 | ferner: nimm / nimm | `C2_GEOMETRY_STRONG_EXPLORATORY` |
| `polaiin` | **Zubereitung / Rezept** | `ENTRY_HEADING` | P-start 7/7; P-end 0/7 | nimm / für / gegen | `C2_GEOMETRY_STRONG_EXPLORATORY` |
| `pol` | **Zubereitung / Eintrag** | `ENTRY_HEADING` | P-start 7/11; P-end 2/11 | für / gegen / nimm | `C1_PLACEMENT_CONSTRAINED` |
| `ycheol` | **danach** | `PROCESS_CONTINUATION` | P-start 0/8; P-end 2/8 | ferner / zum Schluss | `C2_GEOMETRY_STRONG_EXPLORATORY` |
| `ychol` | **danach / als Nächstes** | `PROCESS_CONTINUATION` | P-start 0/8; P-end 3/8 | ferner / zum Schluss | `C2_GEOMETRY_STRONG_EXPLORATORY` |
| `dcheol` | **danach / darauf** | `PROCESS_CONTINUATION` | P-start 0/5; P-end 1/5 | ferner / bewahre anschließend auf | `C1_PLACEMENT_CONSTRAINED` |
| `paiin` | **drei Teile / dritte Menge** | `QUANTITY_HEADING` | P-start 2/5; P-end 1/5 | ferner / nimm | `C0_FORCED_EXPLORATORY` |
| `qokchor` | **mische hinein** | `ADDITION_COMMAND` | P-start 0/5; P-end 0/5 | ferner / nimm | `C1_PLACEMENT_CONSTRAINED` |
| `tshol` | **für / gegen** | `INDICATION_OPENING` | P-start 4/5; P-end 0/5 | Heilmittel / Eintrag / nimm | `C2_GEOMETRY_STRONG_EXPLORATORY` |
| `ycheor` | **zum Schluss** | `CLOSURE_FORMULA` | P-start 1/5; P-end 3/5 | ferner / danach | `C2_GEOMETRY_STRONG_EXPLORATORY` |

## The decisive split

`pchor` and `ychor` are edit-distance-one complete forms but occupy opposite paragraph frames. `pchor` opens 6/7 of its initial paragraphs; `ychor` opens 0/13. This supports two learned formula wholes—recipe/entry opening versus Item-like continuation—without assigning a meaning to `p` or `y`.

The neighboring `ycheol`, `ychol`, `dcheol`, and `ycheor` wholes jointly contribute 26 initial lines, only one paragraph start, and nine paragraph ends. Their current readings therefore stay in an internal continuation/closure family.

## Complete formula-only line reader

The marker is translated; the untouched body remains EVA in brackets so this artifact does not smuggle generic filler into the line.

### `pchor` → nimm

- f9v.5 (P1; start=1; end=0): **nimm**: [ypcheey qotor ypchy olcfholy to ar chty daiiin]
- f19r.1 (P1; start=1; end=0): **nimm**: [qodchy qotshy dy tchy qotchy qoky daiin dchydy]
- f21r.1 (P1; start=1; end=0): **nimm**: [o eeockhy o fychey ypchey qopcheody otaiin chan]
- f52v.1 (P1; start=1; end=0): **nimm**: [chcphol cphaiiin otcheor ytor kol chocphar]
- f83r.9 (P1; start=1; end=0): **nimm**: [checphedy qokedy lsheedy qokchdy r shedkedy qopshdy qopy]
- f86v5.27 (P2; start=0; end=0): **nimm**: [ypchor aiin otar shody pchykar ytar odar oeees aral om]
- f105v.18 (P1; start=1; end=0): **nimm**: [chedaiin okaiin cholkal qolkaiin oltchdy qopchsd opair orair karaim]

### `ychor` → ferner / ebenso

- f6v.8 (P3; start=0; end=0): **ferner / ebenso**: [chor okchey qokom]
- f9v.11 (P7; start=0; end=0): **ferner / ebenso**: [chshoty oky kaiin]
- f17v.15 (P15; start=0; end=0): **ferner / ebenso**: [cthy cheeky cheo otor oteol]
- f19v.9 (P2; start=0; end=0): **ferner / ebenso**: [oky chor ytol chol oky ddor]
- f22v.7 (P2; start=0; end=0): **ferner / ebenso**: [chor qokchol chory]
- f23r.5 (P2; start=0; end=1): **ferner / ebenso**: [qokchol ytym chol dair chol ar ol ol dol dain]
- f24r.8 (P8; start=0; end=0): **ferner / ebenso**: [s om qoear daiin qokeol]
- f45v.9 (P5; start=0; end=0): **ferner / ebenso**: [cthy chol qokom sy sa ykchom]
- f86v5.20 (P3; start=0; end=0): **ferner / ebenso**: [ar aiin ytaly otaiin ykaiin otal ytar aiin ytaiiil]
- f93r.28 (P28; start=0; end=0): **ferner / ebenso**: [odol chodaiin s]
- f99r.52 (P6; start=0; end=1): **ferner / ebenso**: [ols or agairom]
- f102v2.35 (P6; start=0; end=0): **ferner / ebenso**: [sheol por sheeor shekeey qoky cheo teody qokeol daiin]
- f106r.9 (P2; start=0; end=1): **ferner / ebenso**: [chol qokain chocphol lchedy qocheo qokar]

### `polaiin` → Zubereitung / Rezept

- f79r.26 (P1; start=1; end=0): **Zubereitung / Rezept**: [olteedy qotchey dykeedy qokchdy opchedy shol ory]
- f102r1.3 (P1; start=1; end=0): **Zubereitung / Rezept**: [shocthy qoteol loiiin oteeor cpheodar sholdaiin]
- f108v.5 (P1; start=1; end=0): **Zubereitung / Rezept**: [okedain okal otchedy qokeedy raraiin o keedy qokar qokal dam]
- f113v.10 (P1; start=1; end=0): **Zubereitung / Rezept**: [oteol otedyar aral kedy qokeedy olar aiin kchey dal otor ar opchey ro]
- f113v.21 (P1; start=1; end=0): **Zubereitung / Rezept**: [otar qotain chtol tarol cheol kaiin chp kcheos okar aar lo]
- f113v.45 (P1; start=1; end=0): **Zubereitung / Rezept**: [arol shear okeeeody ls ar lkeey opchedy qokchdy ota aram]
- f113v.47 (P1; start=1; end=0): **Zubereitung / Rezept**: [ksheeol lkaiin tair shey qotain ar akal shey qopchedy ldy]

### `pol` → Zubereitung / Eintrag

- f22r.1 (P1; start=1; end=0): **Zubereitung / Eintrag**: [olshy fcholy shol dpchy oty okoly daiin opchy s ocphy]
- f77r.38 (P1; start=1; end=0): **Zubereitung / Eintrag**: [shedy qoeedy qokaiin chcphey qol ltaiin shedy qol]
- f79r.21 (P1; start=1; end=0): **Zubereitung / Eintrag**: [shar sharpchey otshey okaos aiin okshey dalkeeeyry]
- f79r.38 (P4; start=0; end=1): **Zubereitung / Eintrag**: [olkeeey sheol qokeey]
- f79v.37 (P1; start=1; end=0): **Zubereitung / Eintrag**: [ol shal kain okeey lkeey qokal otchsdy okeshdy]
- f80v.42 (P5; start=0; end=0): **Zubereitung / Eintrag**: [ol aiin olkal shar shedy qokol chdy ldol dar al]
- f82v.30 (P3; start=0; end=0): **Zubereitung / Eintrag**: [olor chey qokain shedy qokaiin olchesy ol r aindar]
- f86v6.19 (P7; start=0; end=1): **Zubereitung / Eintrag**: [sheopchey pchecfhey or aiiin qokaiin cholkar]
- f103v.20 (P1; start=1; end=0): **Zubereitung / Eintrag**: [char otar okaiin shay oteal okain qotal shedy qokeey lolain]
- f107v.43 (P1; start=1; end=0): **Zubereitung / Eintrag**: [keeeo kaiisr qokeey chckhy lkchaly lkeey opchey rar aiin cheokaly]
- f113v.42 (P1; start=1; end=0): **Zubereitung / Eintrag**: [keeo dy qoeees aiin or aiin oteol fchedy otchey dar otakeol ol]

### `ycheol` → danach

- f17v.9 (P9; start=0; end=0): **danach**, [shol kchol choltaiin ol]
- f24v.7 (P2; start=0; end=0): **danach**, [daid dar olom]
- f80v.12 (P6; start=0; end=0): **danach**, [kain shey qokain chedy qokol olkain shy l]
- f102r1.10 (P3; start=0; end=0): **danach**, [sholdy chol chol ykeeol dol doleodaiin dal cthedy]
- f104v.13 (P2; start=0; end=0): **danach**, [cheody qoeechdy qokeol qotaiin chedar cheo lkaiin cheetar aiin cheitaiin]
- f104v.30 (P2; start=0; end=0): **danach**, [kaiin cheody shaiin qoeeol otair or cheeody okcheey lkair ar ar adam]
- f106r.33 (P2; start=0; end=1): **danach**, [chokaiin sheody chody qokaiin ar akair aiir okaly]
- f108r.34 (P4; start=0; end=1): **danach**, [chckhy qokedy okain]

### `ychol` → danach / als Nächstes

- f6r.8 (P8; start=0; end=0): **danach / als Nächstes**, [ckhor pchar sheo ckhaiin]
- f14r.6 (P6; start=0; end=0): **danach / als Nächstes**, [oir okor choor ockhy]
- f17v.5 (P5; start=0; end=0): **danach / als Nächstes**, [chol dolcheey tchol dar ckhy]
- f18v.7 (P7; start=0; end=0): **danach / als Nächstes**, [dor chod qokol daiin qokol dar dy]
- f24v.9 (P4; start=0; end=0): **danach / als Nächstes**, [chol or chor om]
- f93v.10 (P10; start=0; end=1): **danach / als Nächstes**, [chs ckhy s cheeol]
- f99v.43 (P7; start=0; end=1): **danach / als Nächstes**, [olkeeoldy]
- f106r.14 (P2; start=0; end=1): **danach / als Nächstes**, [okaiin olcheey dolchedy otair otal chedy okeor]

### `dcheol` → danach / darauf

- f77v.39 (P11; start=0; end=0): **danach / darauf**, [kchedy soey qokal qokal shedy sholdy qotal dar]
- f80r.19 (P9; start=0; end=0): **danach / darauf**, [shedy qokeel qotaiin chtal schcthy qokal chcthy qokain okain oloky]
- f104v.5 (P5; start=0; end=1): **danach / darauf**, [chdeey oeeodain s airol chedal]
- f108r.22 (P2; start=0; end=0): **danach / darauf**, [shol dal qokaiin otal ol shedy qokey chey lor aiin okeeam]
- f115r.24 (P3; start=0; end=0): **danach / darauf**, [qokeol or ar aiin cheey okeeeo or chl lor ol otlaiin cheeor ary]

### `paiin` → drei Teile / dritte Menge

- f10v.1 (P1; start=1; end=0): **drei Teile / dritte Menge**: [daiin sheo pcheey qoty daiin cthor otydy sain]
- f35r.9 (P1; start=1; end=0): **drei Teile / dritte Menge**: [chear aiin chear shorchaiin]
- f39v.12 (P6; start=0; end=0): **drei Teile / dritte Menge**: [alaiin otal chd okar am okar cheodal ockhy]
- f86v6.45 (P16; start=0; end=1): **drei Teile / dritte Menge**: [otar otolkshy qokshey ar otalky chear aiodam]
- f107v.6 (P2; start=0; end=0): **drei Teile / dritte Menge**: [okaiin qokaiy olkeedy qokeey qotaiin oky lkal otaiin aiin qokaldy]

### `qokchor` → mische hinein

- f11v.4 (P4; start=0; end=0): **mische hinein**, [cholol chyky dchy qoky ctho tchey tu]
- f18r.3 (P3; start=0; end=0): **mische hinein**, [chor ey or chey qokchol dy ytcharg]
- f18r.8 (P4; start=0; end=0): **mische hinein**, [ckhol olody okal dy dary]
- f32r.3 (P3; start=0; end=0): **mische hinein**, [chor cthol chol dol dcheodain daiin]
- f44r.10 (P3; start=0; end=0): **mische hinein**, [okchy qoto ykol choky choky chol dam]

### `tshol` → für / gegen

- f11r.1 (P1; start=1; end=0): **für / gegen**: [schoal cfhy shfydaiin cphy shey tchody shoyty]
- f20v.5 (P1; start=1; end=0): **für / gegen**: [folchol otor shol shor fshodchy otchy chcphy dy]
- f23r.6 (P1; start=1; end=0): **für / gegen**: [y kor qokaiin yky dar okol dchey daiidal dam ytcho ldals]
- f23v.6 (P1; start=1; end=0): **für / gegen**: [shor shkshy okol daiin otshor olsar]
- f50r.3 (P3; start=0; end=0): **für / gegen**: [kar sheedy okeody qokedy chody kchdy pchdy chkaiin odam]

### `ycheor` → zum Schluss

- f3r.2 (P2; start=0; end=0): **zum Schluss**, [chor dam qotcham cham]
- f3r.20 (P3; start=0; end=1): **zum Schluss**, [chol odaiin chol s aiin okol or am]
- f6v.21 (P16; start=0; end=1): **zum Schluss**, [chor octham]
- f10r.6 (P1; start=1; end=0): **zum Schluss**, [cthy chor cthaiin qoctholy dy chy taiin shy]
- f11v.7 (P7; start=0; end=1): **zum Schluss**, [ksho dor cthey s chold]

## Rejected shortcut

The high-triad initials `ykar`, `yteedy`, `qotor`, and `dchey` are not promoted to global formula words because their line-initial purity is below 0.70. They remain possible contextual left-edge content or local formula uses.

## Neighbor inventory

| left | right | relation | paragraph-start rates |
|---|---|---|---|
| `pchor` | `ychor` | `OPENER_VS_CONTINUATION_CONTRAST` | 0.857143 / 0.000000 |
| `ychor` | `ychol` | `INTERNAL_CONTINUATION_OR_CLOSURE_FAMILY` | 0.000000 / 0.000000 |
| `ychor` | `ycheor` | `INTERNAL_CONTINUATION_OR_CLOSURE_FAMILY` | 0.000000 / 0.200000 |
| `ycheol` | `ychol` | `INTERNAL_CONTINUATION_OR_CLOSURE_FAMILY` | 0.000000 / 0.000000 |
| `ycheol` | `dcheol` | `INTERNAL_CONTINUATION_OR_CLOSURE_FAMILY` | 0.000000 / 0.000000 |
| `ycheol` | `ycheor` | `INTERNAL_CONTINUATION_OR_CLOSURE_FAMILY` | 0.000000 / 0.200000 |

No candidate is a confirmed lexeme. The practical result is an eleven-whole formula inventory with explicit rivals and a predictive distinction between opening, continuation, addition and closure positions.
