# Kanonisches Arbeitswörterbuch der zehn Seiten

## 38 Komponenten

| Komponente | Rolle | Arbeitsbedeutung | Karten / Ereignisse |
|---|---|---|---|
| `AIIN` | QUANTITY | vorgeschriebenes Maß | 10 / 39 |
| `AIN` | QUANTITY | Portion | 9 / 19 |
| `AIR` | PATH_MEDIUM | laufender Bestand | 5 / 5 |
| `AL` | TARGET | bezeichnete Stelle | 22 / 39 |
| `AR` | SOURCE | von dort | 10 / 14 |
| `CFH` | ACTION | auswringen | 1 / 1 |
| `CH` | ACTION | abziehen | 15 / 16 |
| `CHD` | ACTION | umsetzen | 22 / 48 |
| `CHK` | ACTION | wärmen | 4 / 7 |
| `CKH` | PATH_MEDIUM | Durchlass | 9 / 14 |
| `CTH` | STATE | bereit | 8 / 15 |
| `DA` | MODIFIER | zweite | 1 / 1 |
| `DY` | CLOSE | Schluss | 37 / 89 |
| `E` | GRADE | kurz | 34 / 49 |
| `EE` | GRADE | länger | 17 / 40 |
| `EEE` | GRADE | vollständig | 2 / 2 |
| `HO` | MATERIAL | Gabe | 5 / 8 |
| `IIN` | STATE | Sollstufe | 3 / 4 |
| `K` | ACTION | zuführen | 18 / 21 |
| `L` | ACTION | führen | 18 / 27 |
| `LD` | ACTION | befestigen | 1 / 1 |
| `LS` | SEQUENCE | weiter | 1 / 1 |
| `LSH` | ACTION | waschen | 2 / 3 |
| `O` | PROCESS | Arbeitsgang | 18 / 19 |
| `OK` | ACTION | ansetzen | 23 / 79 |
| `OL` | SEQUENCE | fortsetzen | 25 / 49 |
| `OR` | PREPARATION | Ansatz | 10 / 18 |
| `OS` | TARGET | Arbeitsfach | 1 / 1 |
| `OT` | SEQUENCE | danach | 16 / 26 |
| `P` | ACTION | hineingeben | 3 / 3 |
| `R` | ACTION | abkühlen | 6 / 6 |
| `S` | ACTION | teilen | 1 / 1 |
| `SH` | ACTION | halten | 20 / 25 |
| `SHED` | ACTION | absetzen | 3 / 15 |
| `SOLK` | ACTION | auffangen | 5 / 7 |
| `T` | ACTION | eintragen | 9 / 10 |
| `TALAM` | ACTION | verwahren | 1 / 1 |
| `Y` | ITEM | dieser Posten | 60 / 124 |

## 173 exakte Karten

| Karte | Oberflächen | Zerlegung | portable Lesung | beobachtete Aktionssinne |
|---|---|---|---|---|
| `PROC001` | `dchey` | `CH+E+Y` | diesen Posten kurz abziehen | abnehmen |
| `PROC002` | `cthoor` | `CTH+O+OR` | bereit · Arbeitsgang · Ansatz | NOT_AN_ACTION_CARD |
| `PROC003` | `char|dar|sar` | `AR` | von dort | NOT_AN_ACTION_CARD |
| `PROC004` | `chety|chty` | `T+Y` | diesen Posten eintragen | eintragen|übertragen |
| `PROC005` | `os` | `OS` | Arbeitsfach | NOT_AN_ACTION_CARD |
| `PROC006` | `chair` | `CH+AIR` | den laufenden Posten durch laufender Bestand abziehen | ablaufen lassen |
| `PROC007` | `otytchol` | `OT+Y+T+CH+OL` | danach fortsetzen diesen Posten eintragen und abziehen | eintragen + abnehmen |
| `PROC008` | `choky|oky|qoky` | `OK+Y` | diesen Posten ansetzen | anlegen|einleiten|einsetzen |
| `PROC009` | `aiin|chaiin|daiin|saiin|taiin` | `AIIN` | vorgeschriebenes Maß | NOT_AN_ACTION_CARD |
| `PROC010` | `etyd` | `E+T+Y` | diesen Posten kurz eintragen | eintragen |
| `PROC011` | `chokchy|okchy|qokchy` | `OK+Y` | diesen Posten ansetzen | ansetzen|einsetzen |
| `PROC012` | `qotchol` | `OT+CH+OL` | danach fortsetzen den laufenden Posten abziehen | abnehmen |
| `PROC013` | `cheol|chol|ol|qol|sol|tol` | `OL` | fortsetzen | NOT_AN_ACTION_CARD |
| `PROC014` | `checthy|cthy|shcthy` | `CTH+Y` | bereit · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC015` | `ycheor` | `Y+CH+E+OR` | diesen Posten kurz abziehen | abziehen |
| `PROC016` | `chor|or|shor|sor` | `OR` | Ansatz | NOT_AN_ACTION_CARD |
| `PROC017` | `cthaiin` | `CTH+AIIN` | bereit · vorgeschriebenes Maß | NOT_AN_ACTION_CARD |
| `PROC018` | `qoctholy` | `O+CTH+OL+Y` | Arbeitsgang · bereit · fortsetzen · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC019` | `chey|chy|dy|shy|sy|y` | `Y` | dieser Posten | NOT_AN_ACTION_CARD |
| `PROC020` | `otchor|qotchor` | `OT+CH+OR` | danach den Ansatz abziehen | abziehen |
| `PROC021` | `otol` | `OT+OL` | danach · fortsetzen | NOT_AN_ACTION_CARD |
| `PROC022` | `cholor|olor` | `OL+OR` | fortsetzen · Ansatz | NOT_AN_ACTION_CARD |
| `PROC023` | `oykchor` | `O+Y+K+OR` | diesen Posten zuführen | zugeben |
| `PROC024` | `kaiiin` | `K+IIN` | den laufenden Posten zuführen bis Sollstufe | zugeben |
| `PROC025` | `chodaiin` | `CH+O+AIIN` | den Arbeitsgang nach vorgeschriebenes Maß abziehen | abziehen |
| `PROC026` | `tshol` | `T+SH+OL` | fortsetzen den laufenden Posten eintragen und halten | eintragen + halten |
| `PROC027` | `schoal` | `SH+O+AL` | den Arbeitsgang an bezeichnete Stelle halten | an Ort halten |
| `PROC028` | `cfhy` | `CFH+Y` | diesen Posten auswringen | auswringen |
| `PROC029` | `shfydaiin` | `SH+Y+AIIN` | diesen Posten nach vorgeschriebenes Maß halten | halten |
| `PROC030` | `cphy` | `P+Y` | diesen Posten hineingeben | hineingeben |
| `PROC031` | `cheey|shey` | `SH+EE+Y` | diesen Posten länger halten | halten |
| `PROC032` | `tchody` | `T+CH+O+DY` | den Arbeitsgang eintragen und abziehen; Schritt schließen | abschließend eintragen + abziehen |
| `PROC033` | `shoyty` | `SH+O+Y+T+Y` | diesen Posten halten und eintragen | halten + eintragen |
| `PROC034` | `dchol|schol` | `OL` | fortsetzen | NOT_AN_ACTION_CARD |
| `PROC035` | `kchy` | `K+Y` | diesen Posten zuführen | zugeben |
| `PROC036` | `qotchy` | `OT+Y` | danach · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC037` | `okchol` | `OK+OL` | fortsetzen den laufenden Posten ansetzen | einsetzen |
| `PROC038` | `okaiin|qokaiin` | `OK+AIIN` | den laufenden Posten nach vorgeschriebenes Maß ansetzen | einleiten|einsetzen |
| `PROC039` | `ykain` | `Y+K+AIN` | diesen Posten nach Portion zuführen | dosiert zugeben |
| `PROC040` | `ykan` | `Y+K+AIN` | diesen Posten nach Portion zuführen | zugeben |
| `PROC041` | `ody` | `O+DY` | Arbeitsgang; Schritt schließen | NOT_AN_ACTION_CARD |
| `PROC042` | `chdy|chedy` | `CHD+Y` | diesen Posten umsetzen | abmessen und umsetzen|umsetzen |
| `PROC043` | `talam` | `TALAM` | den laufenden Posten verwahren | verwahren |
| `PROC044` | `ykaiin` | `Y+K+AIIN` | diesen Posten nach vorgeschriebenes Maß zuführen | dosiert zugeben |
| `PROC045` | `cheoar` | `CH+E+O+AR` | den Arbeitsgang von dort kurz abziehen | entnehmen |
| `PROC046` | `cheeky` | `CHK+EE+Y` | diesen Posten länger wärmen | temperieren|warm halten |
| `PROC047` | `oldy` | `OL+DY` | fortsetzen; Schritt schließen | NOT_AN_ACTION_CARD |
| `PROC048` | `okal|qokal` | `OK+AL` | den laufenden Posten an bezeichnete Stelle ansetzen | anlegen |
| `PROC049` | `oltchy` | `OL+T+Y` | fortsetzen diesen Posten eintragen | eintragen |
| `PROC050` | `orain` | `OR+AIN` | Ansatz · Portion | NOT_AN_ACTION_CARD |
| `PROC051` | `chochor` | `HO+CH+OR` | den Gabe und Ansatz abziehen | abziehen |
| `PROC052` | `cho|sho` | `HO` | Gabe | NOT_AN_ACTION_CARD |
| `PROC053` | `chodaly` | `HO+AL+Y` | Gabe · bezeichnete Stelle · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC054` | `kchol` | `K+OL` | fortsetzen den laufenden Posten zuführen | zuführen |
| `PROC055` | `al|chal|cheal|dal|sal|tal` | `AL` | bezeichnete Stelle | NOT_AN_ACTION_CARD |
| `PROC056` | `choy` | `HO+Y` | Gabe · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC057` | `cheeckhody` | `CH+EE+CKH+O+DY` | den Arbeitsgang durch Durchlass länger abziehen; Schritt schließen | ablaufen lassen |
| `PROC058` | `sh` | `SH` | den laufenden Posten halten | halten |
| `PROC059` | `kchey` | `K+E+Y` | diesen Posten kurz zuführen | zugeben |
| `PROC060` | `qokokchy` | `OK+OK+Y` | diesen Posten ansetzen und ansetzen | einsetzen + einsetzen |
| `PROC061` | `chokcheo` | `OK+CH+E+O` | den Arbeitsgang kurz ansetzen und abziehen | ansetzen + abziehen |
| `PROC062` | `kchal` | `K+AL` | den laufenden Posten an bezeichnete Stelle zuführen | zuführen |
| `PROC063` | `kchoar` | `K+HO+AR` | den Gabe von dort zuführen | zugeben |
| `PROC064` | `sotodan` | `OT+O+AIN` | danach · Arbeitsgang · Portion | NOT_AN_ACTION_CARD |
| `PROC065` | `otchey` | `OT+Y` | danach · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC066` | `keol` | `K+E+OL` | fortsetzen den laufenden Posten kurz zuführen | zugeben |
| `PROC067` | `qokedy` | `OK+E+DY` | den laufenden Posten kurz ansetzen; Schritt schließen | einwirken lassen |
| `PROC068` | `kair` | `K+AIR` | den laufenden Posten durch laufender Bestand zuführen | einspeisen |
| `PROC069` | `chkain|kain` | `K+AIN` | den laufenden Posten nach Portion zuführen | dosiert zugeben |
| `PROC070` | `olkain|qolkain` | `OL+K+AIN` | fortsetzen den laufenden Posten nach Portion zuführen | dosiert zugeben |
| `PROC071` | `rol` | `R+OL` | fortsetzen den laufenden Posten abkühlen | abkühlen lassen |
| `PROC072` | `dl` | `L` | den laufenden Posten führen | durchleiten|führen |
| `PROC073` | `sheckhal` | `SH+E+CKH+AL` | den laufenden Posten an bezeichnete Stelle durch Durchlass kurz halten | zurückhalten |
| `PROC074` | `qokeedal` | `OK+EE+AL` | den laufenden Posten an bezeichnete Stelle länger ansetzen | anlegen |
| `PROC075` | `chckhy|shckhy` | `CKH+Y` | Durchlass · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC076` | `dchedy|schedy|tchedy` | `CHD+DY` | den laufenden Posten umsetzen; Schritt schließen | durchleiten|umfüllen|überführen |
| `PROC077` | `sshkchdy` | `SH+K+CHD+DY` | den laufenden Posten halten und zuführen und umsetzen; Schritt schließen | halten + zugeben + überführen |
| `PROC078` | `cheedy|shedy|tedy` | `SHED+DY` | den laufenden Posten absetzen; Schritt schließen | ablagern|absetzen lassen |
| `PROC079` | `olchedy|qolchedy` | `OL+CHD+DY` | fortsetzen den laufenden Posten umsetzen; Schritt schließen | überführen |
| `PROC080` | `okain|qokain` | `OK+AIN` | den laufenden Posten nach Portion ansetzen | einsetzen |
| `PROC081` | `ral` | `R+AL` | den laufenden Posten an bezeichnete Stelle abkühlen | abkühlen lassen |
| `PROC082` | `qokchdy` | `OK+CHD+DY` | den laufenden Posten ansetzen und umsetzen; Schritt schließen | einsetzen + überführen |
| `PROC083` | `cheky` | `CHK+E+Y` | diesen Posten kurz wärmen | warm halten |
| `PROC084` | `lsho` | `LSH+O` | den Arbeitsgang waschen | waschen |
| `PROC085` | `okey|qokey` | `OK+E+Y` | diesen Posten kurz ansetzen | wirken lassen |
| `PROC086` | `lshedy` | `LSH+E+DY` | den laufenden Posten kurz waschen; Schritt schließen | durchwaschen |
| `PROC087` | `qolky` | `SOLK+Y` | diesen Posten auffangen | auffangen |
| `PROC088` | `lchedal` | `L+CHD+AL` | den laufenden Posten an bezeichnete Stelle führen und umsetzen | hinleiten + umfüllen |
| `PROC089` | `otar` | `OT+AR` | danach · von dort | NOT_AN_ACTION_CARD |
| `PROC090` | `ytey` | `T+E+Y` | diesen Posten kurz eintragen | übertragen |
| `PROC091` | `okchedy|qokchedy` | `OK+CHD+DY` | den laufenden Posten ansetzen und umsetzen; Schritt schließen | einsetzen + überführen |
| `PROC092` | `okeey|qokeey` | `OK+EE+Y` | diesen Posten länger ansetzen | anlegen|wirken lassen |
| `PROC093` | `teol` | `E+OL` | kurz · fortsetzen | NOT_AN_ACTION_CARD |
| `PROC094` | `dchdy` | `CHD+DY` | den laufenden Posten umsetzen; Schritt schließen | umfüllen |
| `PROC095` | `ly` | `L+Y` | diesen Posten führen | führen |
| `PROC096` | `dsheol` | `SH+E+OL` | fortsetzen den laufenden Posten kurz halten | halten |
| `PROC097` | `oiiin|soiiin` | `O+IIN` | Arbeitsgang · Sollstufe | NOT_AN_ACTION_CARD |
| `PROC098` | `olkeedy|solkeedy` | `SOLK+EE+DY` | den laufenden Posten länger auffangen; Schritt schließen | auffangen und stehen lassen |
| `PROC099` | `shckhedy` | `SH+CKH+E+DY` | den laufenden Posten durch Durchlass kurz halten; Schritt schließen | zurückhalten |
| `PROC100` | `qokeedy` | `OK+EE+DY` | den laufenden Posten länger ansetzen; Schritt schließen | einwirken lassen |
| `PROC101` | `lcheckhy` | `L+CKH+Y` | diesen Posten durch Durchlass führen | durchleiten |
| `PROC102` | `lched` | `L+CHD` | den laufenden Posten führen und umsetzen | führen + umsetzen |
| `PROC103` | `lcheckhedy` | `L+CKH+E+DY` | den laufenden Posten durch Durchlass kurz führen; Schritt schließen | durchleiten |
| `PROC104` | `qokaly` | `OK+AL+Y` | diesen Posten an bezeichnete Stelle ansetzen | anlegen |
| `PROC105` | `solkaiin` | `SOLK+AIIN` | den laufenden Posten nach vorgeschriebenes Maß auffangen | bis zum Maß auffangen |
| `PROC106` | `octheol` | `O+CTH+E+OL` | Arbeitsgang · bereit · kurz · fortsetzen | NOT_AN_ACTION_CARD |
| `PROC107` | `chkeey` | `CHK+EE+Y` | diesen Posten länger wärmen | warm halten |
| `PROC108` | `ldy` | `L+DY` | den laufenden Posten führen; Schritt schließen | abführen |
| `PROC109` | `oteey` | `OT+EE+Y` | danach · länger · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC110` | `sheckhy` | `SH+E+CKH+Y` | diesen Posten durch Durchlass kurz halten | zurückhalten |
| `PROC111` | `dshedy` | `SH+E+DY` | den laufenden Posten kurz halten; Schritt schließen | ruhen lassen |
| `PROC112` | `otaiin|sotaiin` | `OT+AIIN` | danach · vorgeschriebenes Maß | NOT_AN_ACTION_CARD |
| `PROC113` | `qokar` | `OK+AR` | den laufenden Posten von dort ansetzen | einsetzen |
| `PROC114` | `solshedy` | `OL+SH+E+DY` | fortsetzen den laufenden Posten kurz halten; Schritt schließen | ruhen lassen |
| `PROC115` | `ls` | `LS` | weiter | NOT_AN_ACTION_CARD |
| `PROC116` | `lchy` | `L+CH+Y` | diesen Posten führen und abziehen | führen + abnehmen |
| `PROC117` | `qcthey|shcthey` | `CTH+E+Y` | bereit · kurz · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC118` | `lcheey` | `L+EE+Y` | diesen Posten länger führen | führen |
| `PROC119` | `qokeeedy` | `OK+EEE+DY` | den laufenden Posten vollständig ansetzen; Schritt schließen | einsetzen |
| `PROC120` | `lchedy` | `L+CHD+DY` | den laufenden Posten führen und umsetzen; Schritt schließen | abführen + abmessen und umsetzen|abführen + überführen|hinleiten + umfüllen |
| `PROC121` | `lar` | `L+AR` | den laufenden Posten von dort führen | ableiten |
| `PROC122` | `tshey` | `SH+E+Y` | diesen Posten kurz halten | halten |
| `PROC123` | `lchedar` | `L+CHD+AR` | den laufenden Posten von dort führen und umsetzen | ableiten + umfüllen |
| `PROC124` | `ches` | `CH+E+S` | den laufenden Posten kurz abziehen und teilen | abnehmen + abteilen |
| `PROC125` | `pchedy` | `P+CHD+DY` | den laufenden Posten hineingeben und umsetzen; Schritt schließen | einfüllen + überführen |
| `PROC126` | `rsheal` | `R+SH+E+AL` | den laufenden Posten an bezeichnete Stelle kurz abkühlen und halten | abkühlen lassen + ruhen lassen |
| `PROC127` | `daldy` | `AL+DY` | bezeichnete Stelle; Schritt schließen | NOT_AN_ACTION_CARD |
| `PROC128` | `rshedy` | `R+SHED+DY` | den laufenden Posten abkühlen und absetzen; Schritt schließen | auskühlen lassen + absetzen lassen |
| `PROC129` | `qoteedy` | `OT+EE+DY` | danach · länger; Schritt schließen | NOT_AN_ACTION_CARD |
| `PROC130` | `lochedy` | `L+O+CHD+DY` | den Arbeitsgang führen und umsetzen; Schritt schließen | abführen + überführen |
| `PROC131` | `otal|qotal` | `OT+AL` | danach · bezeichnete Stelle | NOT_AN_ACTION_CARD |
| `PROC132` | `chkeedy` | `CHK+EE+DY` | den laufenden Posten länger wärmen; Schritt schließen | anwärmen |
| `PROC133` | `chedchy` | `CHD+Y` | diesen Posten umsetzen | umsetzen |
| `PROC134` | `pchedal` | `P+CHD+AL` | den laufenden Posten an bezeichnete Stelle hineingeben und umsetzen | einfüllen + umfüllen |
| `PROC135` | `otedy` | `OT+E+DY` | danach · kurz; Schritt schließen | NOT_AN_ACTION_CARD |
| `PROC136` | `shecthedchy` | `SH+E+CTH+CHD+Y` | diesen Posten kurz halten und umsetzen bis bereit | halten + umsetzen |
| `PROC137` | `chary` | `AR+Y` | von dort · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC138` | `okair` | `OK+AIR` | den laufenden Posten durch laufender Bestand ansetzen | einleiten |
| `PROC139` | `sheedy` | `SH+EE+DY` | den laufenden Posten länger halten; Schritt schließen | ruhen lassen |
| `PROC140` | `lo` | `L+O` | den Arbeitsgang führen | führen |
| `PROC141` | `qokshedy` | `OK+SH+E+DY` | den laufenden Posten kurz ansetzen und halten; Schritt schließen | einwirken lassen + ruhen lassen |
| `PROC142` | `shedal` | `SHED+AL` | den laufenden Posten an bezeichnete Stelle absetzen | ablagern |
| `PROC143` | `shecthy` | `SH+E+CTH+Y` | diesen Posten kurz halten bis bereit | halten |
| `PROC144` | `dalchdy` | `AL+CHD+DY` | den laufenden Posten an bezeichnete Stelle umsetzen; Schritt schließen | umfüllen |
| `PROC145` | `otchedy|qotchedy` | `OT+CHD+DY` | danach den laufenden Posten umsetzen; Schritt schließen | überführen |
| `PROC146` | `cheedar` | `EE+AR` | länger · von dort | NOT_AN_ACTION_CARD |
| `PROC147` | `chldaiin` | `L+AIIN` | den laufenden Posten nach vorgeschriebenes Maß führen | ableiten |
| `PROC148` | `chealror` | `AL+R+OR` | den Ansatz an bezeichnete Stelle abkühlen | abkühlen lassen |
| `PROC149` | `cheeety` | `EEE+T+Y` | diesen Posten vollständig eintragen | eintragen |
| `PROC150` | `schedair` | `CHD+AIR` | den laufenden Posten durch laufender Bestand umsetzen | durchleiten |
| `PROC151` | `chedain` | `CHD+AIN` | den laufenden Posten nach Portion umsetzen | abmessen und umsetzen |
| `PROC152` | `qotedaiin` | `OT+E+AIIN` | danach · kurz · vorgeschriebenes Maß | NOT_AN_ACTION_CARD |
| `PROC153` | `olsaly` | `OL+AL+Y` | fortsetzen · bezeichnete Stelle · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC154` | `qolchey` | `OL+Y` | fortsetzen · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC155` | `qokylddy` | `OK+Y+LD+DY` | diesen Posten ansetzen und befestigen; Schritt schließen | einsetzen + festbinden |
| `PROC156` | `dain` | `AIN` | Portion | NOT_AN_ACTION_CARD |
| `PROC157` | `sheey` | `SH+EE+Y` | diesen Posten länger halten | halten |
| `PROC158` | `okeeol` | `OK+EE+OL` | fortsetzen den laufenden Posten länger ansetzen | wirken lassen |
| `PROC159` | `lkedy` | `L+K+E+DY` | den laufenden Posten kurz führen und zuführen; Schritt schließen | abführen + zugeben |
| `PROC160` | `qokol` | `OK+OL` | fortsetzen den laufenden Posten ansetzen | einsetzen |
| `PROC161` | `qockhey` | `O+CKH+E+Y` | Arbeitsgang · Durchlass · kurz · dieser Posten | NOT_AN_ACTION_CARD |
| `PROC162` | `dairydy` | `AIR+Y+DY` | laufender Bestand · dieser Posten; Schritt schließen | NOT_AN_ACTION_CARD |
| `PROC163` | `chckhal` | `CH+CKH+AL` | den laufenden Posten an bezeichnete Stelle durch Durchlass abziehen | ablaufen lassen |
| `PROC164` | `solkey` | `SOLK+E+Y` | diesen Posten kurz auffangen | auffangen |
| `PROC165` | `skar` | `K+AR` | den laufenden Posten von dort zuführen | zuführen |
| `PROC166` | `otchdy` | `OT+CHD+DY` | danach den laufenden Posten umsetzen; Schritt schließen | überführen |
| `PROC167` | `lol` | `L+OL` | fortsetzen den laufenden Posten führen | hinleiten |
| `PROC168` | `chdal` | `CHD+AL` | den laufenden Posten an bezeichnete Stelle umsetzen | umfüllen |
| `PROC169` | `daiiin` | `DA+IIN` | zweite · Sollstufe | NOT_AN_ACTION_CARD |
| `PROC170` | `solkeey` | `SOLK+EE+Y` | diesen Posten länger auffangen | auffangen |
| `PROC171` | `qekey` | `E+K+E+Y` | diesen Posten kurz kurz zuführen | zugeben |
| `PROC172` | `raly` | `R+AL+Y` | diesen Posten an bezeichnete Stelle abkühlen | abkühlen lassen |
| `PROC173` | `ldalor` | `L+AL+OR` | den Ansatz an bezeichnete Stelle führen | hinleiten |
