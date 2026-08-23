# Taschenbuch des Meisterlesers

Die linke Spalte ist die einheitliche Meisterkarte. Jede rechts notierte Oberfläche wird zuerst auf diese Karte zurückgeführt; erst danach wird der kurze Werkstattsinn gelesen. Die Einträge sind eine kreative Rekonstruktion für die zehn festen Seiten.

## Schnellregel

1. Sichtbare Form im 230-Formen-Schlüssel nachschlagen.
2. Die eindeutige Meisterkarte und ihren Komponentenbau einsetzen.
3. Karten innerhalb der Aussage von links nach rechts lesen; ein physischer Zeilenwechsel beendet die Aussage nicht.
4. `q` und `s` ändern in dieser Ausgabe nicht die Kartenbedeutung; sie gehören zur Schreiberhülle.
5. Der konkrete Bildbesitzer ergänzt Material, Gefäß, Körperstelle oder Himmelsadresse.

## M01

| Meister | registrierte Formen | kurzer Sinn | Bau |
|---|---|---|---|
| `chodaly` | `chodaly` | Zutat dorthin | `HO_INGREDIENT+AL_TO+Y_ITEM` |
| `cho` | `cho|sho` | Zutat | `HO_INGREDIENT` |
| `schoal` | `schoal` | Zutat dorthin | `HO_INGREDIENT+AL_TO` |
| `dchey` | `dchey` | Wurzel | `MEMORIZED_WHOLE_CARD` |
| `choy` | `choy` | diese Zutat | `HO_INGREDIENT+Y_CURRENT` |

## M02

| Meister | registrierte Formen | kurzer Sinn | Bau |
|---|---|---|---|
| `rol` | `rol` | weiterfuehren | `R_FRAME+OL_CONTINUE` |
| `oldy` | `oldy` | fortsetzen; Schluss | `OL_CONTINUE+DY_CLOSE` |
| `otol` | `otol` | danach fortsetzen | `OT_FOLLOW+OL_CONTINUE` |
| `oteey` | `oteey` | langer Folgeposten | `OT_FOLLOW+GRADE_2+Y_ITEM` |
| `keol` | `keol` | kurz weiterfuehren | `E_SHORT+OL_CONTINUE` |
| `teol` | `teol` | kurz weiterfuehren | `E_SHORT+OL_CONTINUE` |
| `qotchy` | `qotchy` | Folgeposten | `OT_FOLLOW+CHY_ITEM` |
| `chey` | `chey|chy|dy|shy|sy|y` | dieser Posten | `Y_CURRENT_ITEM_CARD` |
| `qolky` | `qolky` | weiterfuehren | `Q_FRAME+OL_CONTINUE+KY_PATH` |
| `otedy` | `otedy` | kurze Folge; Schluss | `OT_FOLLOW+GRADE_1+CLOSE` |
| `dchol` | `dchol|schol` | Voriges | `DCHOL_SCHOL_PREVIOUS_ITEM_WHOLE` |
| `cheol` | `cheol|chol|ol|qol|sol|tol` | fortsetzen | `OL_CONTINUE` |
| `qolchey` | `qolchey` | diesen Posten weiterfuehren | `OL_CONTINUE+Y_CURRENT` |
| `qotchol` | `qotchol` | danach weiterfuehren | `OT_FOLLOW+OL_CONTINUE` |
| `otchey` | `otchey` | Folgeposten | `OT_FOLLOW+Y_CURRENT_ITEM` |
| `qoteedy` | `qoteedy` | lange Folge; Schluss | `OT_FOLLOW+GRADE_2+CLOSE` |

## M03

| Meister | registrierte Formen | kurzer Sinn | Bau |
|---|---|---|---|
| `chokcheo` | `chokcheo` | Auszug zugeben | `CH_RENDERER+OK_ADD+CHEO_EXTRACT` |
| `dl` | `dl` | Zusatz | `DL_BATH_ADDITIVE_WHOLE_CARD` |
| `otchor` | `otchor|qotchor` | Folgeansatz | `OT_FOLLOW+OR_BATCH` |
| `ycheor` | `ycheor` | Auszugsansatz | `Y_ITEM+CHEO_EXTRACT+OR_BATCH` |
| `chor` | `chor|or|shor|sor` | Ansatz | `OR_BATCH` |
| `cheoar` | `cheoar` | Auszug entnehmen | `CHEO_EXTRACT+AR_SOURCE` |
| `chochor` | `chochor` | Zutatenansatz | `HO_INGREDIENT+OR_BATCH` |
| `kchoar` | `kchoar` | Auszug daraus | `K_HULL+CHEO_EXTRACT+AR_FROM` |
| `dshedy` | `dshedy` | Frischwasser | `DSHE_FRESH_WATER+DY_CLOSE` |
| `chealror` | `chealror` | Ansatz von dort zur Zielstelle | `AL_TO+R_FRAME+OR_BATCH` |
| `cholor` | `cholor|olor` | Fortsetzungsansatz | `OL_CONTINUE+OR_BATCH` |

## M04

| Meister | registrierte Formen | kurzer Sinn | Bau |
|---|---|---|---|
| `okain` | `okain|qokain` | eine Portion zugeben | `OK+AIN_PORTION` |
| `qotedaiin` | `qotedaiin` | kurzes Folgemass | `OT_FOLLOW+E_SHORT+AIIN_MEASURE` |
| `oiiin` | `oiiin|soiiin` | Sollstufe | `IIN_TARGET_STAGE` |
| `solkaiin` | `solkaiin` | bis Sollmass sammeln | `SOLK_COLLECT+AIIN_MEASURE` |
| `aiin` | `aiin|chaiin|daiin|saiin|taiin` | Sollmaß | `AIIN_TARGET_MEASURE` |
| `ykain` | `ykain` | Postenportion | `Y_ITEM+AIN_PORTION` |
| `kaiiin` | `kaiiin` | Weichstufe | `K_SOFT+IIN_TARGET_STAGE` |
| `otaiin` | `otaiin|sotaiin` | Folgemaß | `OT_FOLLOW+AIIN_MEASURE` |
| `shoyty` | `shoyty` | Zutatenteil | `HO_INGREDIENT+Y_CURRENT+TY_PART` |
| `otytchol` | `otytchol` | naechsten Teilposten weiterfuehren | `OT_FOLLOW+TY_PART+OL_CONTINUE` |
| `orain` | `orain` | Ansatzportion | `OR_BATCH+AIN_PORTION` |
| `chety` | `chety|chty` | Teil abtrennen | `CH_PARTITION+TY_PART` |
| `chodaiin` | `chodaiin` | Zutatenmaß | `HO_INGREDIENT+AIIN_MEASURE` |
| `cheeety` | `cheeety` | ganzen Teilposten | `EEE_FULL+TY_PART` |
| `olkain` | `olkain|qolkain` | weitere Portion | `OL_CONTINUE+AIN_PORTION` |
| `chkain` | `chkain|kain` | eine Portion | `AIN_PORTION` |
| `etyd` | `etyd` | kleiner Restteil | `E_SHORT+TY_PART+D_LOCAL` |
| `shfydaiin` | `shfydaiin` | Standmaß | `SHFY_STAND+AIIN_MEASURE` |
| `okaiin` | `okaiin|qokaiin` | auf Sollmaß einstellen | `OK_SET+AIIN_TARGET_MEASURE` |
| `chldaiin` | `chldaiin` | Absetzmaß | `CHLD_SETTLE+AIIN_MEASURE` |
| `chedain` | `chedain` | Portion umsetzen | `CHED_TRANSFER+AIN_PORTION` |
| `ykan` | `ykan` | dieser Anteil | `Y_ITEM+AIN_PORTION` |
| `cthaiin` | `cthaiin` | Fertigmaß | `CTH_READY+AIIN_MEASURE` |
| `ykaiin` | `ykaiin` | Postenmaß | `Y_ITEM+AIIN_MEASURE` |
| `daiiin` | `daiiin` | Öffnungsstufe | `DA+IIN_PORT_GRADE` |

## M05

| Meister | registrierte Formen | kurzer Sinn | Bau |
|---|---|---|---|
| `chary` | `chary` | daraus | `AR_FROM+Y_CURRENT` |
| `oykchor` | `oykchor` | Gefaess | `MEMORIZED_VESSEL_CARD` |
| `raly` | `raly` | diesen Posten dorthin | `AL_TO+Y_CURRENT` |
| `char` | `char|dar|sar` | daraus | `AR_FROM` |
| `ral` | `ral` | zur Zielstelle | `R_FRAME+AL_TO` |
| `dain` | `dain` | Tuch | `DAIN_CLOTH_WHOLE` |
| `olsaly` | `olsaly` | untere Zielstelle | `OLS_BELOW+AL_TO+Y_ITEM` |
| `daldy` | `daldy` | Nebenoeffnung; Schluss | `D_SIDE_FRAME+AL_TO+CLOSE_EXACT` |
| `otal` | `otal|qotal` | danach dorthin | `OT_NEXT+AL_TO` |
| `ldalor` | `ldalor` | Endziel | `LD_END+AL_TO` |
| `ly` | `ly` | Gefaess | `MEMORIZED_VESSEL_CARD` |
| `otar` | `otar` | danach von dort | `OT_NEXT+AR_FROM` |
| `al` | `al|chal|cheal|dal|sal|tal` | dorthin | `AL_TO` |
| `os` | `os` | Gefaess | `MEMORIZED_VESSEL_CARD` |
| `talam` | `talam` | am Ziel verwahren | `T_STORE_FRAME+AL_TO+AM_STORE` |

## M06

| Meister | registrierte Formen | kurzer Sinn | Bau |
|---|---|---|---|
| `chdal` | `chdal` | dort umsetzen | `CHD_TRANSFER+AL_TO` |
| `ldy` | `ldy` | abziehen; Ende | `L_OUT+CLOSE_EXACT` |
| `okchedy` | `okchedy|qokchedy` | umsetzen; Schluss | `OK+CHED_TRANSFER+CLOSE` |
| `lchy` | `lchy` | abziehen | `LCH_WITHDRAW+Y_ITEM` |
| `lchedar` | `lchedar` | von dort abführen | `L_OUT+CHED_TRANSFER+AR_FROM` |
| `chair` | `chair` | Wasserzulauf | `CH_INLET+AIR_WATER` |
| `chckhal` | `chckhal` | zur Zielstelle durchleiten | `CKH_THROUGH+AL_TO` |
| `kair` | `kair` | Beckenwasser | `K_BASIN+AIR_WATER` |
| `dchedy` | `dchedy|schedy|tchedy` | umsetzen; Schluss | `CHED_TRANSFER+TERMINAL` |
| `olchedy` | `olchedy|qolchedy` | fortsetzen; Schluss | `OL_CONTINUE+CHED_TRANSFER+TERMINAL_CLOSE` |
| `lar` | `lar` | von dort abfuehren | `L_OUT+AR_FROM` |
| `lo` | `lo` | abfuehren | `L_OUT+O_RESIDUAL_BRANCH` |
| `dalchdy` | `dalchdy` | dorthin umsetzen; Schluss | `D+AL_TO+CHD_TRANSFER+CLOSE` |
| `chckhy` | `chckhy|shckhy` | durchleiten | `CKH_THROUGH+Y_ITEM` |
| `cheedar` | `cheedar` | von dort umsetzen | `CHED_TRANSFER+AR_FROM` |
| `shecthedchy` | `shecthedchy` | bereiten Posten umsetzen | `CTH_READY+CHED_TRANSFER+Y_CURRENT` |
| `lchedal` | `lchedal` | Auslass | `L_OUT+CHED_TRANSFER+AL_TO` |
| `otchedy` | `otchedy|qotchedy` | Folgeumsetzung; Schluss | `OT_FOLLOW+CHED_TRANSFER+TERMINAL_CLOSE` |
| `sheckhal` | `sheckhal` | kurz zur Zielstelle durchleiten | `CKH_THROUGH+E_SHORT+AL_TO` |
| `chedchy` | `chedchy` | umsetzen | `CHED_TRANSFER+CHY_ITEM` |
| `ls` | `ls` | Auslass | `L_OUT+S_PORT` |
| `lcheey` | `lcheey` | Klarlauf abfuehren | `L_OUT+CHEEY_CLEAR_FLOW` |
| `otchdy` | `otchdy` | Folgeumsetzung; Schluss | `OT_FOLLOW+CHD_TRANSFER+TERMINAL_CLOSE` |
| `pchedy` | `pchedy` | einführen; Schluss | `P_IN+CHED_TRANSFER+TERMINAL` |
| `chdy` | `chdy|chedy` | umsetzen | `CHD~CHED_TRANSFER+Y_ITEM` |
| `okair` | `okair` | Wasser einlassen | `OK_SET+AIR_WATER` |
| `qokchdy` | `qokchdy` | umsetzen; Schluss | `OK+CHD_TRANSFER+CLOSE` |
| `skar` | `skar` | von dort ausgiessen | `SK_POUR+AR_FROM` |
| `dairydy` | `dairydy` | Wasserlauf schliessen; Schluss | `D_TERMINAL_FRAME+AIR_WATER+Y_ITEM+CLOSE_EXACT` |
| `lol` | `lol` | von dort weiterfuehren | `L_OUT+OL_CONTINUE` |
| `tshol` | `tshol` | Zutat entnehmen | `T_FRAME+HO_INGREDIENT+L_OUT` |
| `schedair` | `schedair` | Wasser weiterleiten | `SCHED_LEAD+AIR_WATER` |
| `pchedal` | `pchedal` | Einlass | `P_IN+CHED_TRANSFER+AL_TO` |
| `lched` | `lched` | abführen | `L_OUT+CHED_TRANSFER` |
| `sheckhy` | `sheckhy` | kurz durchleiten | `CKH_THROUGH+E_SHORT+Y_CURRENT` |
| `lcheckhedy` | `lcheckhedy` | abseihen; Schluss | `L_OUT+CKHE_STRAIN+TERMINAL` |
| `dchdy` | `dchdy` | umsetzen; Schluss | `D+CHD_TRANSFER+CLOSE` |
| `lchedy` | `lchedy` | abführen; Schluss | `L_OUT+CHED_TRANSFER+TERMINAL` |
| `qockhey` | `qockhey` | kurzen Durchlauf ansetzen | `OK_SET+CKH_THROUGH+E_SHORT+Y_CURRENT` |
| `lochedy` | `lochedy` | Rest abfuehren; Schluss | `L_OUT+O_RESIDUAL_BRANCH+CHED_TRANSFER+CLOSE_EXACT` |
| `lcheckhy` | `lcheckhy` | Ausgangsdurchlass | `L_OUT+CKH_THROUGH+Y_ITEM` |

## M07

| Meister | registrierte Formen | kurzer Sinn | Bau |
|---|---|---|---|
| `okeey` | `okeey|qokeey` | länger ansetzen | `OK_SET+GRADE_2+Y_OPEN` |
| `sheedy` | `sheedy` | länger absetzen; Schluss | `SHED_SETTLE+GRADE_2+DY_CLOSE` |
| `okey` | `okey|qokey` | kurz ansetzen | `OK_SET+GRADE_1+Y_OPEN` |
| `qokokchy` | `qokokchy` | erneut ansetzen | `OK_SET+OK_REPEAT+Y_CURRENT` |
| `solkeey` | `solkeey` | länger sammeln | `SOLK_COLLECT+EE_LONG+Y_ITEM` |
| `qokol` | `qokol` | Fortsetzung einsetzen | `OK_SET+OL_CONTINUE` |
| `choky` | `choky|oky|qoky` | Posten ansetzen | `OK_SET+Y_OPEN` |
| `cheeky` | `cheeky` | länger wärmen | `CHK_WARM+GRADE_2+Y_OPEN` |
| `tchody` | `tchody` | kalt stellen | `TCHO_COOL+DY_CLOSE` |
| `lshedy` | `lshedy` | waschen; Schluss | `LSH_WASH+DY_CLOSE` |
| `okal` | `okal|qokal` | dort ansetzen | `OK_SET+AL_TO` |
| `okchol` | `okchol` | Fortsetzung einsetzen | `OK_SET+CH_WRAPPER+OL_CONTINUE` |
| `qokar` | `qokar` | daraus ansetzen | `OK_SET+AR_FROM` |
| `olkeedy` | `olkeedy|solkeedy` | länger sammeln; Schluss | `SOLK_COLLECT+EE_LONG+TERMINAL` |
| `solkey` | `solkey` | kurz sammeln | `SOLK_COLLECT+E_SHORT+Y_ITEM` |
| `qokaly` | `qokaly` | dies dort ansetzen | `OK_SET+AL_TO+Y_ITEM` |
| `sshkchdy` | `sshkchdy` | schwenken | `SSHK_SWIVEL_WHOLE+CLOSE` |
| `sotodan` | `sotodan` | danach anwenden | `S_FRAME+OT_FOLLOW+DAN_APPLY` |
| `kchal` | `kchal` | an der Zielstelle bearbeiten | `KCH_PROCESS+AL_TO` |
| `qokeedy` | `qokeedy` | länger ansetzen; Schluss | `OK_SET+GRADE_2+DY_CLOSE` |
| `qokedy` | `qokedy` | kurz ansetzen; Schluss | `OK_SET+GRADE_1+DY_CLOSE` |
| `rshedy` | `rshedy` | Waschgang | `RSHE_WASH_WHOLE_CARD+DY_CLOSE` |
| `kchol` | `kchol` | weiter bearbeiten | `KCH_PROCESS+OL_CONTINUE` |
| `qokeedal` | `qokeedal` | dort länger halten | `OK_SET+EE_HOLD+AL_TO` |
| `cheeckhody` | `cheeckhody` | auftragen | `CHEECKHO_APPLY_WHOLE_CARD+DY_CLOSE` |
| `ody` | `ody` | kühlen | `ODY_COOL+TERMINAL_CLOSE` |
| `chokchy` | `chokchy|okchy|qokchy` | Posten ansetzen | `OK_SET+CH_WRAPPER+Y_OPEN` |
| `ytey` | `ytey` | fuellen | `MEMORIZED_WHOLE_CARD` |
| `chkeedy` | `chkeedy` | länger wärmen; Schluss | `CHK_WARM+GRADE_2+DY_CLOSE` |
| `shedal` | `shedal` | dort absetzen | `SHED_SETTLE+AL_TO` |
| `sh` | `sh` | Staengel | `MEMORIZED_WHOLE_CARD` |
| `kchy` | `kchy` | diesen Posten bearbeiten | `KCH_PROCESS+Y_CURRENT` |
| `kchey` | `kchey` | diesen Posten kurz bearbeiten | `KCH_PROCESS+E_SHORT+Y_CURRENT` |
| `lkedy` | `lkedy` | nachwaschen | `LKEDY_REWASH_WHOLE+CLOSE` |
| `cheedy` | `cheedy|shedy|tedy` | absetzen; Schluss | `SHED_SETTLE+GRADE_1+DY_CLOSE` |
| `cfhy` | `cfhy` | auswringen | `MEMORIZED_WHOLE_CARD` |
| `lsho` | `lsho` | Waschgang | `LSH_WASH` |
| `qokeeedy` | `qokeeedy` | vollständig ansetzen; Schluss | `OK_SET+GRADE_3+DY_CLOSE` |
| `shckhedy` | `shckhedy` | seihen; Schluss | `CKHE_STRAIN+TERMINAL` |
| `cheky` | `cheky` | kurz wärmen | `CHK_WARM+GRADE_1+Y_OPEN` |
| `solshedy` | `solshedy` | weiter absetzen; Schluss | `OL_CONTINUE+SHED_SETTLE+CLOSE` |
| `okeeol` | `okeeol` | länger fortführen | `OK_SET+GRADE_2+OL_CONTINUE` |
| `qokshedy` | `qokshedy` | absetzen; Schluss | `OK_SET+SHED_SETTLE+CLOSE` |
| `ches` | `ches` | teilen | `MEMORIZED_WHOLE_CARD` |
| `cphy` | `cphy` | nachseihen | `MEMORIZED_WHOLE_CARD` |
| `qokylddy` | `qokylddy` | befestigen | `OK+Y_ITEM+LDDY_FASTEN_CLOSE` |
| `chkeey` | `chkeey` | länger wärmen | `CHK_WARM+GRADE_2+Y_CURRENT` |

## M08

| Meister | registrierte Formen | kurzer Sinn | Bau |
|---|---|---|---|
| `oltchy` | `oltchy` | bereit weiterfuehren | `OL_CONTINUE+CTH_READY+Y_CURRENT` |
| `qekey` | `qekey` | roh | `MEMORIZED_WHOLE_CARD` |
| `qcthey` | `qcthey|shcthey` | kurz bereithalten | `CTH_READY+GRADE_1+Y_CURRENT` |
| `dsheol` | `dsheol` | kurz weiter ruhen lassen | `SH_REST+E_SHORT+OL_CONTINUE` |
| `sheey` | `sheey` | laenger ruhen | `SH_REST+EE_LONG+Y_CURRENT` |
| `rsheal` | `rsheal` | kurz am Ziel ruhen | `R_FRAME+SH_REST+E_SHORT+AL_TO` |
| `octheol` | `octheol` | bereit weiterfuehren | `CTH_READY+OL_CONTINUE` |
| `qoctholy` | `qoctholy` | bereiten Posten weiterfuehren | `CTH_READY+OL_CONTINUE+Y_CURRENT` |
| `cheey` | `cheey|shey` | Klarlauf | `SHEY_CLEAR_LIQUID_WHOLE` |
| `shecthy` | `shecthy` | kurz bereit halten | `CTH_READY+E_SHORT+Y_CURRENT` |
| `tshey` | `tshey` | Klarlauf | `T_FRAME+SHEY_CLEAR_FLOW` |
| `cthoor` | `cthoor` | Ansatz bereit | `CTH_READY+OR_BATCH` |
| `checthy` | `checthy|cthy|shcthy` | bereit | `CTH_READY+Y_CURRENT` |
