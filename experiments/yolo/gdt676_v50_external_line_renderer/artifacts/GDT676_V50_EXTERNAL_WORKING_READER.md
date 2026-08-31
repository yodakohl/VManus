# GDT676 — V50 external 51-line working reader

Every source token remains visible. `⟦surface:?⟧` is an unresolved position; broad carriers remain named rather than silently concretized.

## f102v2.3 · QUANTITY_LABEL

**ZL3b:** `oror`

**Tokenwerte:** zwei Portionen

**Arbeitslesung:** Zwei Portionen.

**Aktionen:** NONE (NONE)

**Rest:** 0 offen; NONE

**Audit:** HOLD: oror ist hier ein vollständiges Mengenlabel.

## f104v.2 · NOMINAL_REGISTER

**ZL3b:** `ychedaiin qoteed chockhy otaiin ydaiin qokamdy otarar alched otair oram`

**Tokenwerte:** [ychedaiin:?] | [qoteed:?] | Arzneikompositum im Trockenansatz am Gradanfang | kalt im Zubereitungsrahmen, Grad III | davon drei Maße | [qokamdy:?] | [otarar:?] | Rohdroge I, bis zur Mittelstufe getrocknet und abgeschlossen | zweite kalte Drogenfraktion im Ansatz | [oram:?]

**Arbeitslesung:** ⟦ychedaiin:?⟧ · ⟦qoteed:?⟧ · Arzneikompositum im Trockenansatz, Gradanfang · kalt im Zubereitungsrahmen, Grad III · davon drei Maße · ⟦qokamdy:?⟧ · ⟦otarar:?⟧ · Rohdroge I, bis Mittelstufe getrocknet und abgeschlossen · zweite kalte Drogenfraktion im Ansatz · ⟦oram:?⟧.

**Aktionen:** NONE (NONE)

**Rest:** 5 offen; ychedaiin|qoteed|qokamdy|otarar|oram

**Audit:** HOLD/SPLIT: alched ist hier klar resultative Rohdroge, kein Trocknungsbefehl.

## f105r.2 · MIXED_RECORD

**ZL3b:** `dshees yey cheey raiin otchdy qodor ches or cheey okees odar cheody qody`

**Tokenwerte:** Dosis oder Charge vollständig eingeweichter Arzneispecies | [yey:?] | trocken am Ende des Grades | Wurzel, Typ/Charge III | kalt-trockener Ansatz am Anfang des Grades, abgeschlossen | [qodor:?] | trockenes Drogenmaterial, Mittelstufe | Drogenportion | trocken am Ende des Grades | Charge vollständig erhitzten Ansatzes | erste Ansatzfraktion abmessen | getrockneter Ansatz | stelle die Zubereitung fertig

**Arbeitslesung:** Dosis oder Charge vollständig eingeweichter Arzneispecies · ⟦yey:?⟧ · trocken, Endstufe · Wurzel, Charge III · kalt-trockener Ansatz, Anfangsstufe, abgeschlossen · ⟦qodor:?⟧ · trockenes Drogenmaterial, Mittelstufe · Drogenportion · trocken, Endstufe · Charge vollständig erhitzten Ansatzes · erste Ansatzfraktion abmessen · getrockneter Ansatz · Zubereitung fertigstellen.

**Aktionen:** 11|13 (odar|qody)

**Rest:** 2 offen; yey|qodor

**Audit:** HOLD: dshees ist nominale Dosis/Charge; die Handlungen stehen erst am Zeilenende.

## f105r.31 · NOMINAL_REGISTER

**ZL3b:** `kodeey lchl shx ar aiijy cpheesy okal lkedy lkar chedy qokaiin or fchoky`

**Tokenwerte:** [kodeey:?] | getrocknetes Drogenholz | [shx:?] | Drogenfraktion I | [aiijy:?] | [cpheesy:?] | Rohstoffklasse I im Ansatz, heiß am Gradanfang | erhitzte Holzdroge, Mittelstufe, fertig | heiße Holzfraktion I | trocken in der Mitte des Grades, abgeschlossen | heiß, Grad III | Drogenportion | [fchoky:?]

**Arbeitslesung:** ⟦kodeey:?⟧ · getrocknetes Drogenholz · ⟦shx:?⟧ · Drogenfraktion I · ⟦aiijy:?⟧ · ⟦cpheesy:?⟧ · Rohstoffklasse I im heißen Anfangsansatz · erhitzte Holzdroge, Mittelstufe, fertig · heiße Holzfraktion I · trocken, Mittelstufe, abgeschlossen · heiß, Grad III · Drogenportion · ⟦fchoky:?⟧.

**Aktionen:** NONE (NONE)

**Rest:** 5 offen; kodeey|shx|aiijy|cpheesy|fchoky

**Audit:** HOLD: lchl als getrocknetes Drogenholz passt in das Holz-/Fraktionsregister.

## f105v.1 · MIXED_RECORD

**ZL3b:** `polairy oair olpcheey ykaiin olpchedy opchedaiin dairody ypcheddy sairy`

**Tokenwerte:** [polairy:?] | [oair:?] | [olpcheey:?] | erhitze hiervon auf Stufe III | fertiggestelltes Trockenpulver aus Holzdrogenansatz | [opchedaiin:?] | [dairody:?] | [ypcheddy:?] | [sairy:?]

**Arbeitslesung:** ⟦polairy:?⟧ · ⟦oair:?⟧ · ⟦olpcheey:?⟧ · hiervon auf Stufe III erhitzen · fertiggestelltes Trockenpulver aus Holzdrogenansatz · ⟦opchedaiin:?⟧ · ⟦dairody:?⟧ · ⟦ypcheddy:?⟧ · ⟦sairy:?⟧.

**Aktionen:** 4 (ykaiin)

**Rest:** 7 offen; polairy|oair|olpcheey|opchedaiin|dairody|ypcheddy|sairy

**Audit:** HOLD/SPLIT: olpchedy bezeichnet das Ergebnis der unmittelbar vorausgehenden Erhitzung.

## f105v.14 · ACTION_SEQUENCE

**ZL3b:** `pchedaiin chckhdy qokaiir olpchedy olord aiiin tail odar kard chtchy`

**Tokenwerte:** [pchedaiin:?] | Arzneikompositum: trocken, Gradanfang, abgeschlossen | nimm die dritte erhitzte Drogenfraktion | fertiggestelltes Trockenpulver aus Holzdrogenansatz | [olord:?] | Menge-/Klassenwert IV | [tail:?] | erste Ansatzfraktion abmessen | [kard:?] | Droge kalt trocknen und leicht nachtrocknen

**Arbeitslesung:** ⟦pchedaiin:?⟧ · trockenes Arzneikompositum, Anfangsstufe, abgeschlossen · dritte erhitzte Drogenfraktion nehmen · fertiggestelltes Trockenpulver aus Holzdrogenansatz · ⟦olord:?⟧ · Menge/Klasse IV · ⟦tail:?⟧ · erste Ansatzfraktion abmessen · ⟦kard:?⟧ · Droge kalt trocknen und leicht nachtrocknen.

**Aktionen:** 3|8|10 (qokaiir|odar|chtchy)

**Rest:** 4 offen; pchedaiin|olord|tail|kard

**Audit:** HOLD/SPLIT: olpchedy ist das entnommene Fertigpulver, nicht ein zweiter Befehl.

## f106r.23 · MIXED_RECORD

**ZL3b:** `ychedy qckhedy dair al qokedy shecphy qokchy otedy dar aror`

**Tokenwerte:** Eintrag: getrocknete Droge, fertig | bereite das Arzneikompositum bis zur Mittelstufe und schließe ab | abgemessene Fraktion II | Rohstoffklasse I | heiß in der Mitte des Grades, abgeschlossen | bis zur Mittelstufe eingeweichtes und abgeschlossenes Arzneikompositum | heiß und trocken am Anfang des Grades | kalter Ansatz in der Mitte des Grades, abgeschlossen | abgemessene Fraktion I | [aror:?]

**Arbeitslesung:** Getrocknete Droge, fertig · Arzneikompositum bis Mittelstufe bereiten und abschließen · abgemessene Fraktion II · Rohstoffklasse I · heiß, Mittelstufe, abgeschlossen · bis Mittelstufe eingeweichtes und abgeschlossenes Arzneikompositum · heiß-trocken, Anfangsstufe · kalter Ansatz, Mittelstufe, abgeschlossen · abgemessene Fraktion I · ⟦aror:?⟧.

**Aktionen:** 2 (qckhedy)

**Rest:** 1 offen; aror

**Audit:** HOLD/SPLIT: shecphy ist ein eingeweichtes Fertigergebnis innerhalb einer gestuften Fraktionszeile.

## f107r.2 · MIXED_RECORD

**ZL3b:** `dchey qoteos aiin shedy oteed qor aiin cheockhy olkeey qotain chey qeeey lor`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | [qoteos:?] | Menge III | feucht in der Mitte des Grades, abgeschlossen | [oteed:?] | nimm eine Drogenportion | Menge III | trocken angesetztes Arzneikompositum am Gradanfang | Holzdrogenansatz vollständig erhitzt | kalt im qo-Rahmen, Grad II | trocken in der Mitte des Grades | [qeeey:?] | Holzportion

**Arbeitslesung:** Eine Dosis bis Mittelstufe trocknen und abschließen · ⟦qoteos:?⟧ · Menge III · feucht, Mittelstufe, abgeschlossen · ⟦oteed:?⟧ · eine Drogenportion nehmen · Menge III · trocken angesetztes Arzneikompositum, Anfangsstufe · Holzdrogenansatz vollständig erhitzt · kalt im qo-Rahmen, Grad II · trocken, Mittelstufe · ⟦qeeey:?⟧ · Holzportion.

**Aktionen:** 1|6 (dchey|qor)

**Rest:** 3 offen; qoteos|oteed|qeeey

**Audit:** HOLD: zeileninitiales dchey trägt hier eine echte Handlungsvalenz.

## f107r.40 · NOMINAL_REGISTER

**ZL3b:** `lolkaiin chey qokaiin chal aiin okaiin olkar otair okal okal`

**Tokenwerte:** [lolkaiin:?] | trocken in der Mitte des Grades | heiß, Grad III | Rohstoffklasse I, trocken am Gradanfang | Menge III | heiß, Grad III, im Ansatzrahmen | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | zweite kalte Drogenfraktion im Ansatz | Rohstoffklasse I im Ansatz, heiß am Gradanfang | Rohstoffklasse I im Ansatz, heiß am Gradanfang

**Arbeitslesung:** ⟦lolkaiin:?⟧ · trocken, Mittelstufe · heiß, Grad III · Rohstoffklasse I, trocken, Anfangsstufe · Menge III · heiß, Grad III, im Ansatz · erste erhitzte Drogenfraktion im Ansatz · zweite kalte Drogenfraktion im Ansatz · Rohstoffklasse I im heißen Anfangsansatz · Rohstoffklasse I im heißen Anfangsansatz.

**Aktionen:** NONE (NONE)

**Rest:** 1 offen; lolkaiin

**Audit:** HOLD: olkar ist eine erhitzte Fraktion; die mögliche Holzbindung bleibt offen.

## f10r.2 · MIXED_RECORD

**ZL3b:** `dchey cthoor char chty os chair otytchol oky daiin etyd`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | [cthoor:?] | Trockenfraktion I | trocken-kalt am Gradanfang | Ansatzcharge | [chair:?] | [otytchol:?] | heißer Ansatz am Anfang des Grades | Grad-/Maßwert III | [etyd:?]

**Arbeitslesung:** Eine Dosis bis Mittelstufe trocknen und abschließen · ⟦cthoor:?⟧ · Trockenfraktion I · trocken-kalt, Anfangsstufe · Ansatzcharge · ⟦chair:?⟧ · ⟦otytchol:?⟧ · heißer Ansatz, Anfangsstufe · Grad/Maß III · ⟦etyd:?⟧.

**Aktionen:** 1 (dchey)

**Rest:** 4 offen; cthoor|chair|otytchol|etyd

**Audit:** HOLD: dchey kann zeileninitial als Anweisung stehen; der Rest spezifiziert Charge und Stufe.

## f112r.36 · QUANTITY_LABEL

**ZL3b:** `sain ol checkhy olchain okeey olam`

**Tokenwerte:** Saatgut, Typ/Charge II | Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz | trockenes Arzneikompositum am Gradanfang | [olchain:?] | heißer Ansatz am Ende des Grades | ein Maß Ansatz-/Drogenmaterial; Holzbindung offen

**Arbeitslesung:** Saatgut, Charge II · Ansatz/Gut · trockenes Arzneikompositum, Anfangsstufe · ⟦olchain:?⟧ · heißer Ansatz, Endstufe · ein Maß Ansatz-/Drogenmaterial.

**Aktionen:** NONE (NONE)

**Rest:** 1 offen; olchain

**Audit:** HOLD: olam ist sicher ein Maß; Stoffklasse beziehungsweise Holzbindung bleibt offen.

## f112v.10 · QUANTITY_LABEL

**ZL3b:** `dain sheey okchedy oror`

**Tokenwerte:** Grad-/Maßwert II | feucht am Ende des Grades | heiß-trockener Ansatz in der Mitte des Grades, abgeschlossen | zwei Portionen

**Arbeitslesung:** Grad/Maß II · feucht, Endstufe · heiß-trockener Ansatz, Mittelstufe, abgeschlossen · zwei Portionen.

**Aktionen:** NONE (NONE)

**Rest:** 0 offen; NONE

**Audit:** HOLD: vollständiges Zustands- und Mengenlabel; oror passt ohne Zusatzannahme.

## f113v.12 · QUANTITY_LABEL

**ZL3b:** `solchedy otsheody arl olchey oror`

**Tokenwerte:** getrockneter Samen/Saatgutstoff/-ansatz | [otsheody:?] | erste Holzdrogenfraktion | [olchey:?] | zwei Portionen

**Arbeitslesung:** Getrockneter Samen-/Saatgutansatz · ⟦otsheody:?⟧ · erste Holzdrogenfraktion · ⟦olchey:?⟧ · zwei Portionen.

**Aktionen:** NONE (NONE)

**Rest:** 2 offen; otsheody|olchey

**Audit:** HOLD: oror quantifiziert das vorausgehende Fraktionsregister.

## f113v.17 · NOMINAL_REGISTER

**ZL3b:** `saraiin shedy lcheey olkar okaiin cthororaiin yteeeor`

**Tokenwerte:** [saraiin:?] | feucht in der Mitte des Grades, abgeschlossen | Drogenholz, trocken gebunden, Form II | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | heiß, Grad III, im Ansatzrahmen | [cthororaiin:?] | [yteeeor:?]

**Arbeitslesung:** ⟦saraiin:?⟧ · feucht, Mittelstufe, abgeschlossen · trocken gebundenes Drogenholz, Form II · erste erhitzte Drogenfraktion im Ansatz · heiß, Grad III, im Ansatz · ⟦cthororaiin:?⟧ · ⟦yteeeor:?⟧.

**Aktionen:** NONE (NONE)

**Rest:** 3 offen; saraiin|cthororaiin|yteeeor

**Audit:** HOLD: olkar ist nominale erhitzte Fraktion; keine Imperativvalenz vorhanden.

## f113v.3 · QUANTITY_LABEL

**ZL3b:** `sar aiin chotar okeeodar qokain olol olam`

**Tokenwerte:** Samenfraktion I | Menge III | [chotar:?] | [okeeodar:?] | heiß, Grad II | Holzdrogen-Grundansatz | ein Maß Ansatz-/Drogenmaterial; Holzbindung offen

**Arbeitslesung:** Samenfraktion I · Menge III · ⟦chotar:?⟧ · ⟦okeeodar:?⟧ · heiß, Grad II · Holzdrogen-Grundansatz · ein Maß Ansatz-/Drogenmaterial.

**Aktionen:** NONE (NONE)

**Rest:** 2 offen; chotar|okeeodar

**Audit:** HOLD: olam schließt ein Mengenetikett ab; Holzbezug ist möglich, aber nicht erzwungen.

## f114r.24 · NOMINAL_REGISTER

**ZL3b:** `tchedaiin oldal chor chpcheey chcphey cphochy chos aiir chty chopo sair cphy dair`

**Tokenwerte:** [tchedaiin:?] | abgemessener Drogenrohstoff I | Pflanzen-/Reproduktionsteil | [chpcheey:?] | bis zur Mittelstufe getrocknetes und abgeschlossenes Arzneikompositum | [cphochy:?] | eine Charge Trockenansatz | [aiir:?] | trocken-kalt am Gradanfang | [chopo:?] | Samenfraktion II | Arzneikompositum in Grundform | abgemessene Fraktion II

**Arbeitslesung:** ⟦tchedaiin:?⟧ · abgemessener Drogenrohstoff I · Pflanzen-/Reproduktionsteil · ⟦chpcheey:?⟧ · bis Mittelstufe getrocknetes und abgeschlossenes Arzneikompositum · ⟦cphochy:?⟧ · Charge Trockenansatz · ⟦aiir:?⟧ · trocken-kalt, Anfangsstufe · ⟦chopo:?⟧ · Samenfraktion II · Arzneikompositum in Grundform · abgemessene Fraktion II.

**Aktionen:** NONE (NONE)

**Rest:** 5 offen; tchedaiin|chpcheey|cphochy|aiir|chopo

**Audit:** HOLD/SPLIT: chcphey ist ein benanntes Trockenprodukt zwischen Materialangaben.

## f114r.26 · QUANTITY_LABEL

**ZL3b:** `ycheeodaiin olkaiir qokaiin chodaiin okar olkaiin okaiin cheody airoy olam`

**Tokenwerte:** [ycheeodaiin:?] | [olkaiir:?] | heiß, Grad III | Trockenansatz, Dosis III | heiße Drogenfraktion I im Ansatz | heiße Drogenbasis, Stufe III | heiß, Grad III, im Ansatzrahmen | getrockneter Ansatz | [airoy:?] | ein Maß Ansatz-/Drogenmaterial; Holzbindung offen

**Arbeitslesung:** ⟦ycheeodaiin:?⟧ · ⟦olkaiir:?⟧ · heiß, Grad III · Trockenansatz, Dosis III · heiße Drogenfraktion I im Ansatz · heiße Drogenbasis, Stufe III · heiß, Grad III, im Ansatz · getrockneter Ansatz · ⟦airoy:?⟧ · ein Maß Ansatz-/Drogenmaterial.

**Aktionen:** NONE (NONE)

**Rest:** 3 offen; ycheeodaiin|olkaiir|airoy

**Audit:** HOLD: olam ist der Abschluss eines gestuften Mengenregisters.

## f114v.36 · MIXED_RECORD

**ZL3b:** `tshey oidal op shoko otchey qopchol qopaiin qotar al kal ram`

**Tokenwerte:** kalt und feucht in der Mitte des Grades | [oidal:?] | [op:?] | [shoko:?] | kalt-trockener Ansatz in der Mitte des Grades | nimm getrockneten Pulverstoff | [qopaiin:?] | kalte Drogenfraktion I | Rohstoffklasse I | Rohstoffklasse I, heiß am Gradanfang | Wurzel/Wurzeldroge: Maß-/Einheitsform I

**Arbeitslesung:** Kalt-feucht, Mittelstufe · ⟦oidal:?⟧ · ⟦op:?⟧ · ⟦shoko:?⟧ · kalt-trockener Ansatz, Mittelstufe · getrockneten Pulverstoff nehmen · ⟦qopaiin:?⟧ · kalte Drogenfraktion I · Rohstoffklasse I · Rohstoffklasse I im heißen Anfangsansatz · Wurzeldroge, Einheit I.

**Aktionen:** 6 (qopchol)

**Rest:** 4 offen; oidal|op|shoko|qopaiin

**Audit:** HOLD: qopchol hat mit dem expliziten Pulverstoff eine natürliche Entnahmevalenz.

## f115r.1 · MIXED_RECORD

**ZL3b:** `fdar qopchol qochedain otedy cheop ol teeedy oroiir oechedy oteedy qotchedy`

**Tokenwerte:** [fdar:?] | nimm getrockneten Pulverstoff | [qochedain:?] | kalter Ansatz in der Mitte des Grades, abgeschlossen | [cheop:?] | Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz | vollständig abgekühlt und abgeschlossen | [oroiir:?] | [oechedy:?] | kalter Ansatz am Ende des Grades, abgeschlossen | kalt und trocken in der Mitte des Grades, abgeschlossen

**Arbeitslesung:** ⟦fdar:?⟧ · getrockneten Pulverstoff nehmen · ⟦qochedain:?⟧ · kalter Ansatz, Mittelstufe, abgeschlossen · ⟦cheop:?⟧ · Ansatz/Gut · vollständig abgekühlt und abgeschlossen · ⟦oroiir:?⟧ · ⟦oechedy:?⟧ · kalter Ansatz, Endstufe, abgeschlossen · kalt-trocken, Mittelstufe, abgeschlossen.

**Aktionen:** 2 (qopchol)

**Rest:** 5 offen; fdar|qochedain|cheop|oroiir|oechedy

**Audit:** HOLD: qopchol bleibt konkrete Entnahme; die nachfolgenden Wörter sind überwiegend Zustandsresultate.

## f115r.23 · ACTION_SEQUENCE

**ZL3b:** `dchey keey qokeod chody qokcho s checthy qokeeey keeey lol chedy qokchedy ldy`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | heiß am Ende des Grades | [qokeod:?] | Trockenansatz, abgeschlossen | erhitze, trockne und setze an | Samen-/Saatgutposten | trockenes CTH-Drogenmaterial; im Herbal trockenes Blatt-/Krautgut | stark erhitzt, Endstufe III | [keeey:?] | Holzstoff | trocken in der Mitte des Grades, abgeschlossen | heiß und trocken in der Mitte des Grades, abgeschlossen | Holzdroge, fertig aufbereitet

**Arbeitslesung:** Eine Dosis bis Mittelstufe trocknen und abschließen · heiß, Endstufe · ⟦qokeod:?⟧ · Trockenansatz, abgeschlossen · erhitzen, trocknen und ansetzen · Samen-/Saatgutposten · trockenes Blatt-/Krautgut · stark erhitzt, Endstufe III · ⟦keeey:?⟧ · Holzstoff · trocken, Mittelstufe, abgeschlossen · heiß-trocken, Mittelstufe, abgeschlossen · Holzdroge, fertig aufbereitet.

**Aktionen:** 1|5 (dchey|qokcho)

**Rest:** 2 offen; qokeod|keeey

**Audit:** HOLD: initiales dchey und qokcho bilden eine plausible zweiteilige Arbeitsfolge.

## f116r.12 · MIXED_RECORD

**ZL3b:** `qoin ar cholches okain dain cheey okeey otain olchdy otal dain olam`

**Tokenwerte:** [qoin:?] | Drogenfraktion I | [cholches:?] | heiß im Zubereitungsrahmen, Grad II | Grad-/Maßwert II | trocken am Ende des Grades | heißer Ansatz am Ende des Grades | kalt im Zubereitungsrahmen, Grad II | Drogenstoff trocknen und fertigstellen | Rohstoffklasse I im Ansatz, kalt am Gradanfang | Grad-/Maßwert II | ein Maß Ansatz-/Drogenmaterial; Holzbindung offen

**Arbeitslesung:** ⟦qoin:?⟧ · Drogenfraktion I · ⟦cholches:?⟧ · heiß, Grad II, im Zubereitungsrahmen · Grad/Maß II · trocken, Endstufe · heißer Ansatz, Endstufe · kalt, Grad II, im Zubereitungsrahmen · Drogenstoff trocknen und fertigstellen · Rohstoffklasse I im kalten Anfangsansatz · Grad/Maß II · ein Maß Ansatz-/Drogenmaterial.

**Aktionen:** 9 (olchdy)

**Rest:** 2 offen; qoin|cholches

**Audit:** HOLD MIT BINDUNGSFRAGE: olam bleibt Maß; wahrscheinlich bindet dain unmittelbar daran.

## f23r.6 · MIXED_RECORD

**ZL3b:** `tshol y kor qokaiin yky dar okol dchey daiidal dam ytcho ldals`

**Tokenwerte:** [tshol:?] | hierzu: | heiße Drogenportion | heiß, Grad III | hierzu leicht erhitzen | abgemessene Fraktion I | heißer Ansatzstoff | abgemessene Trockendroge der Mittelstufe, abgeschlossen | [daiidal:?] | Dosis I | [ytcho:?] | [ldals:?]

**Arbeitslesung:** ⟦tshol:?⟧ · hierzu · heiße Drogenportion · heiß, Grad III · hierzu leicht erhitzen · abgemessene Fraktion I · heißer Ansatzstoff · abgemessene Trockendroge der Mittelstufe, abgeschlossen · ⟦daiidal:?⟧ · Dosis I · ⟦ytcho:?⟧ · ⟦ldals:?⟧.

**Aktionen:** 5 (yky)

**Rest:** 4 offen; tshol|daiidal|ytcho|ldals

**Audit:** HOLD/SPLIT: dchey an Position 8 ist nominales Trockenprodukt, nicht nochmals ein Befehl.

## f24v.15 · ACTION_SEQUENCE

**ZL3b:** `dchey kchod dchal ochdy`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | [kchod:?] | [dchal:?] | [ochdy:?]

**Arbeitslesung:** Eine Dosis bis Mittelstufe trocknen und abschließen · ⟦kchod:?⟧ · ⟦dchal:?⟧ · ⟦ochdy:?⟧.

**Aktionen:** 1 (dchey)

**Rest:** 3 offen; kchod|dchal|ochdy

**Audit:** HOLD: dchey ist als Initialhandlung möglich; der Gegenstand bleibt durch drei offene Stellen unbekannt.

## f26r.2 · NOMINAL_REGISTER

**ZL3b:** `dchey aiin adeeody ykecthey chedy ytedy dy checthedy ls`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | Menge III | [adeeody:?] | [ykecthey:?] | trocken in der Mitte des Grades, abgeschlossen | [ytedy:?] | Qualitäts-/Wertfeld geschlossen | [checthedy:?] | [ls:?]

**Arbeitslesung:** Abgemessene Trockendroge der Mittelstufe, abgeschlossen · Menge III · ⟦adeeody:?⟧ · ⟦ykecthey:?⟧ · trocken, Mittelstufe, abgeschlossen · ⟦ytedy:?⟧ · Qualitäts-/Wertfeld geschlossen · ⟦checthedy:?⟧ · ⟦ls:?⟧.

**Aktionen:** NONE (NONE)

**Rest:** 5 offen; adeeody|ykecthey|ytedy|checthedy|ls

**Audit:** OVERRIDE: dchey aiin muss hier nominal als Produkt plus Menge gelesen werden; Imperativ plus Menge III ist zeilenweit inkohärent.

## f27r.9 · MIXED_RECORD

**ZL3b:** `dchey keeod shotchey chol oty chy tolg`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | [keeod:?] | [shotchey:?] | trocken; nominal trockenes Gut/Material | kalter Ansatz am Anfang des Grades | trocken am Anfang des Grades | [tolg:?]

**Arbeitslesung:** Eine Dosis bis Mittelstufe trocknen und abschließen · ⟦keeod:?⟧ · ⟦shotchey:?⟧ · Trockengut · kalter Ansatz, Anfangsstufe · trocken, Anfangsstufe · ⟦tolg:?⟧.

**Aktionen:** 1 (dchey)

**Rest:** 3 offen; keeod|shotchey|tolg

**Audit:** HOLD: dchey bleibt Initialhandlung; folgende Zustände können ihr Ergebnis spezifizieren.

## f30r.9 · ACTION_SEQUENCE

**ZL3b:** `dchey qochar chol keeaiin chcthey chor cheky`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | [qochar:?] | trocken; nominal trockenes Gut/Material | [keeaiin:?] | Krautdroge bis zur mittleren Stufe trocknen | Pflanzen-/Reproduktionsteil | bis zur mittleren Trockenstufe, dann leicht erhitzen

**Arbeitslesung:** Eine Dosis bis Mittelstufe trocknen und abschließen · ⟦qochar:?⟧ · Trockengut · ⟦keeaiin:?⟧ · Krautdroge bis zur Mittelstufe trocknen · Pflanzen-/Reproduktionsteil · bis zur mittleren Trockenstufe bringen, dann leicht erhitzen.

**Aktionen:** 1|5|7 (dchey|chcthey|cheky)

**Rest:** 2 offen; qochar|keeaiin

**Audit:** HOLD: dchey passt in eine dreigliedrige Trocknungs- und Erhitzungsfolge.

## f49r.16 · NOMINAL_REGISTER

**ZL3b:** `qocho cheey dchey qotchody`

**Tokenwerte:** [qocho:?] | trocken am Ende des Grades | abgemessene Trockendroge der Mittelstufe, abgeschlossen | [qotchody:?]

**Arbeitslesung:** ⟦qocho:?⟧ · trocken, Endstufe · abgemessene Trockendroge der Mittelstufe, abgeschlossen · ⟦qotchody:?⟧.

**Aktionen:** NONE (NONE)

**Rest:** 2 offen; qocho|qotchody

**Audit:** HOLD/SPLIT: dchey ist zwischen Zustandswörtern ein nominales Trockenprodukt.

## f56r.6 · NOMINAL_REGISTER

**ZL3b:** `ykcho dy dchey keey daiin y`

**Tokenwerte:** [ykcho:?] | Qualitäts-/Wertfeld geschlossen | abgemessene Trockendroge der Mittelstufe, abgeschlossen | heiß am Ende des Grades | Grad-/Maßwert III | Eintrag abgeschlossen

**Arbeitslesung:** ⟦ykcho:?⟧ · Qualitäts-/Wertfeld geschlossen · abgemessene Trockendroge der Mittelstufe, abgeschlossen · heiß, Endstufe · Grad/Maß III · Eintrag abgeschlossen.

**Aktionen:** NONE (NONE)

**Rest:** 1 offen; ykcho

**Audit:** HOLD/SPLIT: dchey ist Bestandteil eines abgeschlossenen Qualitätsregisters.

## f75r.3 · MIXED_RECORD

**ZL3b:** `qokain chal orchey qey kain sheeky ltain olkar or`

**Tokenwerte:** heiß, Grad II | Rohstoffklasse I, trocken am Gradanfang | [orchey:?] | [qey:?] | heiß, Grad II | vollständig einweichen, erhitzen und abschließen | [ltain:?] | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | Drogenportion

**Arbeitslesung:** Heiß, Grad II · Rohstoffklasse I, trocken, Anfangsstufe · ⟦orchey:?⟧ · ⟦qey:?⟧ · heiß, Grad II · vollständig einweichen, erhitzen und abschließen · ⟦ltain:?⟧ · erste erhitzte Drogenfraktion im Ansatz · Drogenportion.

**Aktionen:** 6 (sheeky)

**Rest:** 3 offen; orchey|qey|ltain

**Audit:** HOLD: olkar bleibt nominale Fraktion innerhalb einer Zustands-/Handlungszeile.

## f76v.10 · MIXED_RECORD

**ZL3b:** `cphdor shedal qopchdy dshedy shedy tchedy lsheetal shecphy daiin dy`

**Tokenwerte:** [cphdor:?] | feuchte abgemessene Rohstoffmenge I in der Gradmitte | nimm fertig getrocknetes Pulver | weiche eine Dosis Droge bis zur Mittelstufe ein und schließe ab | feucht in der Mitte des Grades, abgeschlossen | kalt und trocken in der Mitte des Grades, abgeschlossen | [lsheetal:?] | bis zur Mittelstufe eingeweichtes und abgeschlossenes Arzneikompositum | Grad-/Maßwert III | Qualitäts-/Wertfeld geschlossen

**Arbeitslesung:** ⟦cphdor:?⟧ · feuchte abgemessene Rohstoffmenge I, Mittelstufe · fertig getrocknetes Pulver nehmen · eine Dosis Droge bis Mittelstufe einweichen und abschließen · feucht, Mittelstufe, abgeschlossen · kalt-trocken, Mittelstufe, abgeschlossen · ⟦lsheetal:?⟧ · bis Mittelstufe eingeweichtes und abgeschlossenes Arzneikompositum · Grad/Maß III · Qualitäts-/Wertfeld geschlossen.

**Aktionen:** 3|4 (qopchdy|dshedy)

**Rest:** 2 offen; cphdor|lsheetal

**Audit:** HOLD/SPLIT: shecphy ist das eingeweichte Resultat der vorausgehenden Operation.

## f77r.38 · ACTION_SEQUENCE

**ZL3b:** `pol shedy qoeedy qokaiin chcphey qol ltaiin shedy qol`

**Tokenwerte:** Pulverstoff | feucht in der Mitte des Grades, abgeschlossen | nimm den vollständig fertiggestellten Ansatz | heiß, Grad III | bis zur Mittelstufe getrocknetes und abgeschlossenes Arzneikompositum | Drogenstoff zugeben | [ltaiin:?] | feucht in der Mitte des Grades, abgeschlossen | Drogenstoff zugeben

**Arbeitslesung:** Pulverstoff · feucht, Mittelstufe, abgeschlossen · vollständig fertiggestellten Ansatz nehmen · heiß, Grad III · bis Mittelstufe getrocknetes und abgeschlossenes Arzneikompositum · Drogenstoff zugeben · ⟦ltaiin:?⟧ · feucht, Mittelstufe, abgeschlossen · Drogenstoff zugeben.

**Aktionen:** 3|6|9 (qoeedy|qol|qol)

**Rest:** 1 offen; ltaiin

**Audit:** HOLD/SPLIT: chcphey ist das getrocknete Zugabegut zwischen Nehmen und zweimaligem Zugeben.

## f77v.7 · ACTION_SEQUENCE

**ZL3b:** `olshedy qolsheedy qy rr ycheedy okedy lshedy chs shdal chedy qolky`

**Tokenwerte:** Holzdroge im Ansatz vollständig eingeweicht | vollständig eingeweichten und fertigen Drogenstoff zugeben | [qy:?] | [rr:?] | trockne hiervon vollständig und stelle es fertig | heißer Ansatz in der Mitte des Grades, abgeschlossen | eingeweichtes Drogenholz | Trockengut, Grundform | feuchte abgemessene Rohstoffmenge I am Gradanfang | trocken in der Mitte des Grades, abgeschlossen | leicht erhitzten Drogenstoff hinzugeben

**Arbeitslesung:** Holzdroge im Ansatz, vollständig eingeweicht · vollständig eingeweichten und fertigen Drogenstoff zugeben · ⟦qy:?⟧ · ⟦rr:?⟧ · hiervon vollständig trocknen und fertigstellen · heißer Ansatz, Mittelstufe, abgeschlossen · eingeweichtes Drogenholz · Trockengut, Grundform · feuchte abgemessene Rohstoffmenge I, Anfangsstufe · trocken, Mittelstufe, abgeschlossen · leicht erhitzten Drogenstoff zugeben.

**Aktionen:** 2|5|11 (qolsheedy|ycheedy|qolky)

**Rest:** 2 offen; qy|rr

**Audit:** HOLD/SPLIT: bei qolsheedy ist nur qol die Zugabehandlung; sheedy bezeichnet bereits fertiges Feuchtgut.

## f7r.2 · MIXED_RECORD

**ZL3b:** `dcheey keo r shor dold dchey kchey otchy cheody`

**Tokenwerte:** eine Dosis vollständig trocknen und abschließen | [keo:?] | Wurzel | Blüten-/Fruchtstand; reproduktiver Teil | [dold:?] | abgemessene Trockendroge der Mittelstufe, abgeschlossen | heiß und trocken in der Mitte des Grades | kalt-trockener Ansatz am Anfang des Grades | getrockneter Ansatz

**Arbeitslesung:** Eine Dosis vollständig trocknen und abschließen · ⟦keo:?⟧ · Wurzel · Blüten-/Fruchtstand · ⟦dold:?⟧ · abgemessene Trockendroge der Mittelstufe, abgeschlossen · heiß-trocken, Mittelstufe · kalt-trockener Ansatz, Anfangsstufe · getrockneter Ansatz.

**Aktionen:** 1 (dcheey)

**Rest:** 2 offen; keo|dold

**Audit:** HOLD/SPLIT: dcheey ist der Initialbefehl; späteres dchey ist nominales Ergebnis.

## f80r.17 · ACTION_SEQUENCE

**ZL3b:** `solky sheckhy sheky shkeol qokar sheky chetain ol olkar okain sheky qokal da`

**Tokenwerte:** [solky:?] | feuchtes Arzneikompositum am Gradanfang | bis zur Mittelstufe einweichen, erhitzen und abschließen | [shkeol:?] | heiße Drogenfraktion I | bis zur Mittelstufe einweichen, erhitzen und abschließen | [chetain:?] | Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | heiß im Zubereitungsrahmen, Grad II | bis zur Mittelstufe einweichen, erhitzen und abschließen | Rohstoffklasse I, heiß am Gradanfang | [da:?]

**Arbeitslesung:** ⟦solky:?⟧ · feuchtes Arzneikompositum, Anfangsstufe · bis Mittelstufe einweichen, erhitzen und abschließen · ⟦shkeol:?⟧ · heiße Drogenfraktion I · bis Mittelstufe einweichen, erhitzen und abschließen · ⟦chetain:?⟧ · Ansatz/Gut · erste erhitzte Drogenfraktion im Ansatz · heiß, Grad II, im Zubereitungsrahmen · bis Mittelstufe einweichen, erhitzen und abschließen · Rohstoffklasse I im heißen Anfangsansatz · ⟦da:?⟧.

**Aktionen:** 3|6|11 (sheky|sheky|sheky)

**Rest:** 4 offen; solky|shkeol|chetain|da

**Audit:** HOLD: olkar bleibt das erhitzte Fraktionsobjekt zwischen den wiederholten Behandlungsschritten.

## f80v.27 · NOMINAL_REGISTER

**ZL3b:** `pshol kain olkar shey qokain dal oltaiin okain shal qoty`

**Tokenwerte:** eingeweichter Pulverstoff | heiß, Grad II | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | feucht in der Mitte des Grades | heiß, Grad II | abgemessene Rohstoffmenge I | [oltaiin:?] | heiß im Zubereitungsrahmen, Grad II | Rohstoffklasse I, feucht am Gradanfang | kalt am Anfang des Grades

**Arbeitslesung:** Eingeweichter Pulverstoff · heiß, Grad II · erste erhitzte Drogenfraktion im Ansatz · feucht, Mittelstufe · heiß, Grad II · abgemessene Rohstoffmenge I · ⟦oltaiin:?⟧ · heiß, Grad II, im Zubereitungsrahmen · Rohstoffklasse I, feucht, Anfangsstufe · kalt, Anfangsstufe.

**Aktionen:** NONE (NONE)

**Rest:** 1 offen; oltaiin

**Audit:** HOLD: olkar passt als nominale erhitzte Fraktion in ein fast geschlossenes Stoffregister.

## f80v.35 · ACTION_SEQUENCE

**ZL3b:** `tol oltain olkar y qol qol kain okiin ol kain shey ldy`

**Tokenwerte:** kalt; nominal kaltes Gut/Material | [oltain:?] | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | hierzu: | Drogenstoff zugeben | Drogenstoff zugeben | heiß, Grad II | [okiin:?] | Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz | heiß, Grad II | feucht in der Mitte des Grades | Holzdroge, fertig aufbereitet

**Arbeitslesung:** Kaltes Gut · ⟦oltain:?⟧ · erste erhitzte Drogenfraktion im Ansatz · hierzu · Drogenstoff zugeben · Drogenstoff zugeben · heiß, Grad II · ⟦okiin:?⟧ · Ansatz/Gut · heiß, Grad II · feucht, Mittelstufe · Holzdroge, fertig aufbereitet.

**Aktionen:** 5|6 (qol|qol)

**Rest:** 2 offen; oltain|okiin

**Audit:** HOLD: olkar ist Zugabegut; die zwei qol sind die tatsächlichen Imperative.

## f83v.12 · NOMINAL_REGISTER

**ZL3b:** `daiin shckhy qoeeo lldar cheey qoal qokeedy olkar sheedy qokain olal`

**Tokenwerte:** Grad-/Maßwert III | Arzneikompositum: feucht, Gradanfang | [qoeeo:?] | [lldar:?] | trocken am Ende des Grades | Rohstoffklasse I | heiß am Ende des Grades, abgeschlossen | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | feucht am Ende des Grades, abgeschlossen | heiß, Grad II | Ansatz aus Holzrohstoff, Form I

**Arbeitslesung:** Grad/Maß III · feuchtes Arzneikompositum, Anfangsstufe · ⟦qoeeo:?⟧ · ⟦lldar:?⟧ · trocken, Endstufe · Rohstoffklasse I · heiß, Endstufe, abgeschlossen · erste erhitzte Drogenfraktion im Ansatz · feucht, Endstufe, abgeschlossen · heiß, Grad II · Holzrohstoffansatz, Form I.

**Aktionen:** NONE (NONE)

**Rest:** 2 offen; qoeeo|lldar

**Audit:** HOLD: olkar ist nominal und zwischen abgeschlossenen Zustandsstufen eingebettet.

## f85r2.5 · NOMINAL_REGISTER

**ZL3b:** `ockhdar olkar shoral`

**Tokenwerte:** [ockhdar:?] | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | [shoral:?]

**Arbeitslesung:** ⟦ockhdar:?⟧ · erste erhitzte Drogenfraktion im Ansatz (nur ZL3b; Leser-Rivale olkor/ar) · ⟦shoral:?⟧.

**Aktionen:** NONE (NONE)

**Rest:** 2 offen; ockhdar|shoral

**Audit:** QUARANTÄNE: Die ZL3b-Lesung olkar bleibt als Arbeitshypothese sichtbar; IT2a/RF1b ersetzen die entscheidende Form durch olkor beziehungsweise ar, und beide Nachbarn sind offen.

## f86v3.13 · MIXED_RECORD

**ZL3b:** `osheey orsheey tcheody qokain qodaiin olkar chedaiin y chedy qokady cholkain`

**Tokenwerte:** [osheey:?] | [orsheey:?] | abkühlen, bis zur Mittelstufe trocknen, ansetzen und fertigstellen | heiß, Grad II | Qualitätsgrad III | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | abgemessene Trockendroge, Dosis III | hierzu: | trocken in der Mitte des Grades, abgeschlossen | erhitze einen gleichen Teil und schließe ab | [cholkain:?]

**Arbeitslesung:** ⟦osheey:?⟧ · ⟦orsheey:?⟧ · abkühlen, bis Mittelstufe trocknen, ansetzen und fertigstellen · heiß, Grad II · Qualitätsgrad III · erste erhitzte Drogenfraktion im Ansatz · abgemessene Trockendroge, Dosis III · hierzu · trocken, Mittelstufe, abgeschlossen · einen gleichen Teil erhitzen und abschließen · ⟦cholkain:?⟧.

**Aktionen:** 3|10 (tcheody|qokady)

**Rest:** 3 offen; osheey|orsheey|cholkain

**Audit:** HOLD: olkar ist das Fraktionsobjekt zwischen zwei Arbeitsanweisungen.

## f86v3.18 · MIXED_RECORD

**ZL3b:** `pchedaiin dchedy qokchdy qopchol shol sheody solkam`

**Tokenwerte:** [pchedaiin:?] | abgemessene Trockendroge, fertig | heiß und trocken am Anfang des Grades, abgeschlossen | nimm getrockneten Pulverstoff | feucht; nominal feuchtes Gut/Material | angefeuchteter Ansatz, abgeschlossen | [solkam:?]

**Arbeitslesung:** ⟦pchedaiin:?⟧ · abgemessene Trockendroge, fertig · heiß-trocken, Anfangsstufe, abgeschlossen · getrockneten Pulverstoff nehmen · Feuchtgut · angefeuchteter Ansatz, abgeschlossen · ⟦solkam:?⟧.

**Aktionen:** 4 (qopchol)

**Rest:** 2 offen; pchedaiin|solkam

**Audit:** HOLD: qopchol hat konkrete Entnahmevalenz und ein direktes Pulverobjekt.

## f86v3.19 · ACTION_SEQUENCE

**ZL3b:** `dchey otain olkechy qokam chol kchdy chol tchdy dar aiindy`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | kalt im Zubereitungsrahmen, Grad II | [olkechy:?] | nimm ein Maß und erhitze es | trocken; nominal trockenes Gut/Material | heiß und trocken am Anfang des Grades, abgeschlossen | trocken; nominal trockenes Gut/Material | kalt und trocken am Anfang des Grades, abgeschlossen | abgemessene Fraktion I | [aiindy:?]

**Arbeitslesung:** Eine Dosis bis Mittelstufe trocknen und abschließen · kalt, Grad II, im Zubereitungsrahmen · ⟦olkechy:?⟧ · ein Maß nehmen und erhitzen · Trockengut · heiß-trocken, Anfangsstufe, abgeschlossen · Trockengut · kalt-trocken, Anfangsstufe, abgeschlossen · abgemessene Fraktion I · ⟦aiindy:?⟧.

**Aktionen:** 1|4 (dchey|qokam)

**Rest:** 2 offen; olkechy|aiindy

**Audit:** HOLD: initiales dchey ist mit der späteren Maßentnahme eine kohärente Arbeitsfolge.

## f86v5.2 · ACTION_SEQUENCE

**ZL3b:** `losair yteody qokar shy qokar shor qopchol tal ol ytol otam otam`

**Tokenwerte:** [losair:?] | Eintrag/Bezug: kalte Zubereitung, abgeschlossen | heiße Drogenfraktion I | feucht am Anfang des Grades | heiße Drogenfraktion I | Blüten-/Fruchtstand; reproduktiver Teil | nimm getrockneten Pulverstoff | Rohstoffklasse I, kalt am Gradanfang | Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz | kühle hiervon den Drogenstoff ab | ein Maß kalten Ansatzes | ein Maß kalten Ansatzes

**Arbeitslesung:** ⟦losair:?⟧ · kalte Zubereitung, abgeschlossen · heiße Drogenfraktion I · feucht, Anfangsstufe · heiße Drogenfraktion I · Blüten-/Fruchtstand · getrockneten Pulverstoff nehmen · Rohstoffklasse I, kalt, Anfangsstufe · Ansatz/Gut · hiervon den Drogenstoff abkühlen · ein Maß kalten Ansatzes · ein Maß kalten Ansatzes.

**Aktionen:** 7|10 (qopchol|ytol)

**Rest:** 1 offen; losair

**Audit:** HOLD: qopchol und ytol ergeben eine konkrete Entnahme-Kühl-Folge.

## f86v5.24 · MIXED_RECORD

**ZL3b:** `oar aiin ykain okal kchody chckhy otaiin olkar otaiin`

**Tokenwerte:** Drogenfraktion I im Ansatz | Menge III | erhitze hiervon auf Stufe II | Rohstoffklasse I im Ansatz, heiß am Gradanfang | [kchody:?] | Arzneikompositum: trocken, Gradanfang | kalt im Zubereitungsrahmen, Grad III | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | kalt im Zubereitungsrahmen, Grad III

**Arbeitslesung:** Drogenfraktion I im Ansatz · Menge III · hiervon auf Stufe II erhitzen · Rohstoffklasse I im heißen Anfangsansatz · ⟦kchody:?⟧ · trockenes Arzneikompositum, Anfangsstufe · kalt, Grad III, im Zubereitungsrahmen · erste erhitzte Drogenfraktion im Ansatz · kalt, Grad III, im Zubereitungsrahmen.

**Aktionen:** 3 (ykain)

**Rest:** 1 offen; kchody

**Audit:** HOLD: olkar ist das erhitzte Fraktionsresultat; die einzige klare Handlung ist ykain.

## f86v5.4 · QUANTITY_LABEL

**ZL3b:** `ypchesy oky sheeey qoty qotaiin sail chepy ltedy dar olkar am`

**Tokenwerte:** [ypchesy:?] | heißer Ansatz am Anfang des Grades | [sheeey:?] | kalt am Anfang des Grades | kalt, Grad III | [sail:?] | [chepy:?] | [ltedy:?] | abgemessene Fraktion I | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | Maßeinheit I

**Arbeitslesung:** ⟦ypchesy:?⟧ · heißer Ansatz, Anfangsstufe · ⟦sheeey:?⟧ · kalt, Anfangsstufe · kalt, Grad III · ⟦sail:?⟧ · ⟦chepy:?⟧ · ⟦ltedy:?⟧ · abgemessene Fraktion I · erste erhitzte Drogenfraktion im Ansatz · Maßeinheit I.

**Aktionen:** NONE (NONE)

**Rest:** 5 offen; ypchesy|sheeey|sail|chepy|ltedy

**Audit:** HOLD: dar olkar am bildet am ehesten ein Fraktions-/Mengenetikett, keine Handlung.

## f86v6.25 · ACTION_SEQUENCE

**ZL3b:** `yteedy qokar olkar qodar ykaiin or okeeeey ofchedy qokaiin araram`

**Tokenwerte:** kühle hiervon vollständig ab und schließe | heiße Drogenfraktion I | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | [qodar:?] | erhitze hiervon auf Stufe III | Drogenportion | [okeeeey:?] | [ofchedy:?] | heiß, Grad III | [araram:?]

**Arbeitslesung:** Hiervon vollständig abkühlen und abschließen · heiße Drogenfraktion I · erste erhitzte Drogenfraktion im Ansatz · ⟦qodar:?⟧ · hiervon auf Stufe III erhitzen · Drogenportion · ⟦okeeeey:?⟧ · ⟦ofchedy:?⟧ · heiß, Grad III · ⟦araram:?⟧.

**Aktionen:** 1|5 (yteedy|ykaiin)

**Rest:** 4 offen; qodar|okeeeey|ofchedy|araram

**Audit:** HOLD: olkar ist plausibles Material zwischen Abkühlen und erneutem Erhitzen.

## f86v6.31 · NOMINAL_REGISTER

**ZL3b:** `dair chepy qokaiin olkar olkchdy okar al dar olkchey otytam orom`

**Tokenwerte:** abgemessene Fraktion II | [chepy:?] | heiß, Grad III | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | heiß-trocken aufbereitetes Drogenmaterial | heiße Drogenfraktion I im Ansatz | Rohstoffklasse I | abgemessene Fraktion I | [olkchey:?] | [otytam:?] | [orom:?]

**Arbeitslesung:** Abgemessene Fraktion II · ⟦chepy:?⟧ · heiß, Grad III · erste erhitzte Drogenfraktion im Ansatz · heiß-trocken aufbereitetes Drogenmaterial · heiße Drogenfraktion I im Ansatz · Rohstoffklasse I · abgemessene Fraktion I · ⟦olkchey:?⟧ · ⟦otytam:?⟧ · ⟦orom:?⟧.

**Aktionen:** NONE (NONE)

**Rest:** 4 offen; chepy|olkchey|otytam|orom

**Audit:** HOLD: olkar ist Bestandteil eines Fraktionsregisters ohne Imperativanker.

## f86v6.4 · QUANTITY_LABEL

**ZL3b:** `dshor shdy shor ol aiin olkeedy shdal oteor chdar l karchees olkar dalam`

**Tokenwerte:** abgemessene Blüten-/Fruchtdroge | feucht am Anfang des Grades, abgeschlossen | Blüten-/Fruchtstand; reproduktiver Teil | Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz | Menge III | Holzdrogenansatz vollständig erhitzt und abgeschlossen | feuchte abgemessene Rohstoffmenge I am Gradanfang | [oteor:?] | abgemessene Trockenfraktion I, Anfangsstufe | Holzdroge in der gebundenen Anschlussform | [karchees:?] | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | ein Maß Rohdroge I

**Arbeitslesung:** Abgemessene Blüten-/Fruchtdroge · feucht, Anfangsstufe, abgeschlossen · Blüten-/Fruchtstand · Ansatz/Gut · Menge III · Holzdrogenansatz vollständig erhitzt und abgeschlossen · feuchte abgemessene Rohstoffmenge I, Anfangsstufe · ⟦oteor:?⟧ · abgemessene Trockenfraktion I, Anfangsstufe · Holzdroge, gebundene Anschlussform · ⟦karchees:?⟧ · erste erhitzte Drogenfraktion im Ansatz · ein Maß Rohdroge I.

**Aktionen:** NONE (NONE)

**Rest:** 2 offen; oteor|karchees

**Audit:** HOLD: olkar dalam schließt plausibel als „erhitzte Fraktion; ein Maß Rohdroge I“.

## f86v6.5 · NOMINAL_REGISTER

**ZL3b:** `tar lol chol olkar daiin chear or otshey qokar opchey taiky qotar`

**Tokenwerte:** kalte Drogenfraktion I | Holzstoff | trocken; nominal trockenes Gut/Material | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | Grad-/Maßwert III | trockene Fraktion I | Drogenportion | kalt-feuchter Ansatz in der Mitte des Grades | heiße Drogenfraktion I | Trockenpulver-Ansatz, Form I | [taiky:?] | kalte Drogenfraktion I

**Arbeitslesung:** Kalte Drogenfraktion I · Holzstoff · Trockengut · erste erhitzte Drogenfraktion im Ansatz · Grad/Maß III · trockene Fraktion I · Drogenportion · kalt-feuchter Ansatz, Mittelstufe · heiße Drogenfraktion I · Trockenpulver-Ansatz, Form I · ⟦taiky:?⟧ · kalte Drogenfraktion I.

**Aktionen:** NONE (NONE)

**Rest:** 1 offen; taiky

**Audit:** HOLD: olkar steht in einer besonders starken kalten/heißer/trockenen Fraktionsparadigmatik.

## f88r.19 · MIXED_RECORD

**ZL3b:** `dchey chokol daiin qoekol qoekol qockhol okol cheol`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | [chokol:?] | Qualitätsgrad III | [qoekol:?] | [qoekol:?] | [qockhol:?] | heißer Ansatzstoff | trockener Drogenstoff

**Arbeitslesung:** Eine Dosis bis Mittelstufe trocknen und abschließen · ⟦chokol:?⟧ · Qualitätsgrad III · ⟦qoekol:?⟧ · ⟦qoekol:?⟧ · ⟦qockhol:?⟧ · heißer Ansatzstoff · trockener Drogenstoff.

**Aktionen:** 1 (dchey)

**Rest:** 4 offen; chokol|qoekol|qoekol|qockhol

**Audit:** HOLD: initiales dchey kann Anweisung sein; die doppelte unbekannte Form bleibt sichtbar.

## f8r.15 · MIXED_RECORD

**ZL3b:** `dchey ckhol chol chey kc chy daiin dol daiiiry ckhy`

**Tokenwerte:** eine Dosis bis zur Mittelstufe trocknen und abschließen | [ckhol:?] | trocken; nominal trockenes Gut/Material | trocken in der Mitte des Grades | [kc:?] | trocken am Anfang des Grades | Grad-/Maßwert III | Materialmaß | [daiiiry:?] | Arzneikompositum am Gradanfang

**Arbeitslesung:** Eine Dosis bis Mittelstufe trocknen und abschließen · ⟦ckhol:?⟧ · Trockengut · trocken, Mittelstufe · ⟦kc:?⟧ · trocken, Anfangsstufe · Grad/Maß III · Materialmaß · ⟦daiiiry:?⟧ · Arzneikompositum, Anfangsstufe.

**Aktionen:** 1 (dchey)

**Rest:** 3 offen; ckhol|kc|daiiiry

**Audit:** HOLD: dchey ist Initialhandlung mit nachfolgender Trockenstufen- und Maßspezifikation.

## f95v1.7 · NOMINAL_REGISTER

**ZL3b:** `dshey kain qokar olkar chy tar otar chdy kchdy dolkain otardy`

**Tokenwerte:** eine Dosis bis zur Mittelstufe angefeuchtete Droge | heiß, Grad II | heiße Drogenfraktion I | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | trocken am Anfang des Grades | kalte Drogenfraktion I | kalte Drogenfraktion I im Ansatz | trocken am Anfang des Grades, abgeschlossen | heiß und trocken am Anfang des Grades, abgeschlossen | [dolkain:?] | [otardy:?]

**Arbeitslesung:** Eine Dosis bis Mittelstufe angefeuchtete Droge · heiß, Grad II · heiße Drogenfraktion I · erste erhitzte Drogenfraktion im Ansatz (nur ZL3b; IT2a/RF1b: oltar) · trocken, Anfangsstufe · kalte Drogenfraktion I · kalte Drogenfraktion I im Ansatz · trocken, Anfangsstufe, abgeschlossen · heiß-trocken, Anfangsstufe, abgeschlossen · ⟦dolkain:?⟧ · ⟦otardy:?⟧.

**Aktionen:** NONE (NONE)

**Rest:** 2 offen; dolkain|otardy

**Audit:** QUARANTÄNE: ZL3b-olkar passt nominal in das heiß/kalt/trocken-Register, aber beide Alternativleser haben oltar; die Prosa markiert den Rivalen deshalb direkt.
