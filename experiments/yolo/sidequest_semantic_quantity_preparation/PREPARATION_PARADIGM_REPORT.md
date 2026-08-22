# Zubereitungs- und Reihenfolgeparadigma

## Ergebnis

Die kurze Werkstattgrammatik hält: **OR = Zubereitung**, **OL+OR = vorige Zubereitung**, **OT+OR = nächste Zubereitung**. Repariert werden **OR+AIN = Zubereitungsportion** statt „warm auflegen“ und **OT+OL = danach weiter** statt „Handvoll“. chochor wird **HO+OR = Pflanzenzubereitung**; ycheor und oykchor bleiben Ganzkarten.

Explorative Sidequest-Lesung der festen Seiten, keine Entzifferungsbehauptung. f84 und f84r blieben versiegelt.

## Exact-Tuple-Regel

- OR-Tuple 7a4bb8136330ee4e6e56 umfasst chor|or|shor|sor; nur dort sind ch/sh/s Renderer.
- cholor|olor ist ein Tuple: OL liefert vorig/fortsetzen, OR bleibt Zubereitung.
- otchor|qotchor ist ein Tuple: OT liefert nächst/danach, OR bleibt Zubereitung.
- ycheor, oykchor, ldalor, chealror und cthoor sind andere Tuples und bleiben trotz Zeichenüberlappung Ganzkarten.
- chochor wird als anderes Tuple nur zerlegt, weil HO=Pflanze und OR=Zubereitung im gesamten H5-Auftakt unverändert passen; damit wird der alte Gloss-Widerspruch Pflanzenteil beseitigt.

## Kompaktes Paradigma

| Formfamilie | Zerlegung | Default | Entscheidung |
|---|---|---|---|
| chor\|or\|shor\|sor | OR_PREPARATION | Zubereitung | CORE_CONFIRMED |
| cholor\|olor | OL_CONTINUE+OR_PREPARATION | vorige Zubereitung | CORE_CONFIRMED |
| otchor\|qotchor | OT_NEXT+OR_PREPARATION | nächste Zubereitung | CORE_CONFIRMED |
| chochor | HO_PLANT+OR_PREPARATION | Pflanzenzubereitung | CORE_REVISED |
| orain | OR_PREPARATION+AIN_PORTION | Zubereitungsportion | CORE_REVISED |
| otol | OT_THEREAFTER+OL_CONTINUE | danach weiter | CORE_REVISED |
| char/dar/sar | AR_SOURCE | aus demselben Vorrat | reine Quellenrelation |

OR benennt die Sache; OL/OT ordnen sie relativ zum Arbeitsgang, AIN portioniert sie, HO bestimmt den Pflanzenstoff.

## OR+AIN gegen „warm auflegen“

1. AIN ist unabhängig Portion (kain/chkain = abgemessener Teil), AIIN ist Maß.
2. H4-S004 enthält mit oltchy bereits die gelinde Erwärmung; „warm“ in orain wäre Kontextkopie.
3. or · y · orain wird sparsam „Zubereitung – davon/laufender Posten – Zubereitungsportion“. Wärme bleibt im Satz, nicht im Kartendefault.

Neue Lesung: „Nimm das Maß, trage es an der Zielstelle auf und erwärme die Zubereitung gelind; verwende davon eine Zubereitungsportion.“

## OL, OT und AR als Anschlüsse

- OL wird durch ol, dchol, okchol, qokol, olkain, oldy, olchedy und okeeol als Fortsetzung/Vorigkeit gestützt.
- OT wird durch otaiin, otchedy, otchdy, otal, otar, oteey, otedy, qoteedy und otchey als Danach/Nächstes gestützt.
- AR wird durch char|dar|sar, qokar, lchedar, cheoar und skar als Quelle/Vorrat gestützt. Es gibt keine eigene OR+AR-Karte; H2-S002 endet lediglich mit „aus demselben Vorrat“.
- Daher ist otol = OT+OL = danach weiter; der alte Wert Handvoll folgt aus keiner Komponente.

## Alle Kernvorkommen

| Event | Record/Aussage | Seite/Locus | Oberfläche | Joint-Tuple | neue Karte | bisheriger Kontext |
|---|---|---|---|---|---|---|
| E017 | H2/H2-S001 | f10r f10r.6 | chor | 7a4bb8136330ee4e6e56 | Zubereitung | Führe sie als frischen Ansatz |
| E024 | H2/H2-S002 | f10r f10r.8 | qotchor | 10488b911aae52b3b334 | nächste Zubereitung | Die nächste Zubereitung |
| E025 | H2/H2-S002 | f10r f10r.8 | chor | 7a4bb8136330ee4e6e56 | Zubereitung | Führe den ersten Ansatz weiter |
| E026 | H2/H2-S002 | f10r f10r.8 | otol | 497cbd9c7401810ff56b | danach weiter | Nimm eine Handvoll |
| E028 | H2/H2-S002 | f10r f10r.8 | cholor | dec401773c1f0347793d | vorige Zubereitung | Nimm den vorherigen Posten hinzu |
| E033 | H2/H2-S003 | f10r f10r.9 | shor | 7a4bb8136330ee4e6e56 | Zubereitung | Führe die Mischung als Salbenansatz |
| E034 | H2/H2-S003 | f10r f10r.9 | chor | 7a4bb8136330ee4e6e56 | Zubereitung | Der wiederholte Ansatzvermerk bestätigt hier denselben Salbenposten |
| E071 | H4/H4-S004 | f55v f55v.11 | or | 7a4bb8136330ee4e6e56 | Zubereitung | Führe sie als zweiten Ansatz |
| E073 | H4/H4-S004 | f55v f55v.11 | orain | 6afeb5c9ab9f6cbdea0d | Zubereitungsportion | Lege den warmen Umschlag frisch auf |
| E074 | H5/H5-S001 | f56r f56r.5 | chochor | b9d7b6d68209a9019e7a | Pflanzenzubereitung | Von der abgebildeten, unbenannten Pflanze |
| E080 | H5/H5-S001 | f56r f56r.7 | otchor | 10488b911aae52b3b334 | nächste Zubereitung | Die nächste Zubereitung |
| E113 | B1/B1-S002 | f81v f81v.7 | olor | dec401773c1f0347793d | vorige Zubereitung | Den vorigen recordlokalen Posten wieder aufnehmen |
| E254 | B3/B3-S012 | f83r f83r.11 | sor | 7a4bb8136330ee4e6e56 | Zubereitung | Den recordlokalen aktiven Posten im Arbeitsgang fortführen |
| E348 | B4/B4-S014 | f83r f83r.38 | or | 7a4bb8136330ee4e6e56 | Zubereitung | Den recordlokalen aktiven Posten im Arbeitsgang fortführen |

## Acht neu gelesene Aussagen

| Aussage | Oberfläche | neue Lesung |
|---|---|---|
| H2-S001 | ycheor · cthy · chor · cthaiin · qoctholy · dy · chy · taiin · shy | Wenn die Pflanzenspitzen bereit sind, bereite sie zu: zerstoße das Kraut, gib es durch ein Tuch und nimm den laufenden Posten nach Maß weiter. |
| H2-S002 | qotchor · chor · otol · chol · cholor · chol · daiin · dar | Für die nächste Zubereitung nimm die Zubereitung; arbeite danach mit dem Vorigen weiter, gib die vorige Zubereitung hinzu und fahre fort. Entnimm das Maß aus demselben Vorrat. |
| H2-S003 | oykchor · shor · chor · chy · kaiiin · dy · chodaiin | Vereinige im glasierten Gefäß zwei Zubereitungen mit dem laufenden Posten zu einer weichen Salbe für das Geschwür. |
| H4-S004 | aiin · okal · oltchy · or · y · orain | Nimm das Maß, trage es an der Zielstelle auf und erwärme die Zubereitung gelind; verwende davon eine Zubereitungsportion. |
| H5-S001 | chochor · cho · chodaly · daiin · sho · kchol · otchor · choky · dal | Pflanzenzubereitung: Nimm die Pflanze zu Blütebeginn nach Maß und lege sie auf. Für die nächste Zubereitung nimm den laufenden Posten und verwende ihn an der Zielstelle. |
| B1-S002 | okaiin · kair · okal · sar · ol · kain · olkain · al · ol · rol · dl · olor · ol · sheckhal · daiin · qokeedal · daiin · chckhy · schedy | Bemesse den Einsatz, führe die laufende Beckenflüssigkeit an die Zielstelle und entnimm einen abgemessenen Teil aus demselben Vorrat. Fahre am unteren Becken mit einer weiteren Portion fort. Vor dem Abkühlen gib den Badezusatz und die vorige Zubereitung in mäßiger Menge hinzu; halte den Teil nach Maß an der Zielstelle, führe ihn durch den verbundenen Lauf und schließe die Bewegung ab. |
| B3-S012 | sor · shedy | Lasse die Zubereitung kurz ruhen; Schluss. |
| B4-S014 | or · chey · qockhey · dairydy | Nimm die Zubereitung, halte den laufenden Posten über der Zielstelle und schließe den Flüssigkeitslauf ab. |

## Ganze betroffene Records

Unveränderte Aussagen bleiben vollständig sichtbar, damit die Revisionen im Recordzusammenhang prüfbar sind.

### H2 (f10r)

| Aussage | Oberfläche | konkrete Rücklesung | Status |
|---|---|---|---|
| H2-S001 | ycheor · cthy · chor · cthaiin · qoctholy · dy · chy · taiin · shy | Wenn die Pflanzenspitzen bereit sind, bereite sie zu: zerstoße das Kraut, gib es durch ein Tuch und nimm den laufenden Posten nach Maß weiter. | NEU GELESEN |
| H2-S002 | qotchor · chor · otol · chol · cholor · chol · daiin · dar | Für die nächste Zubereitung nimm die Zubereitung; arbeite danach mit dem Vorigen weiter, gib die vorige Zubereitung hinzu und fahre fort. Entnimm das Maß aus demselben Vorrat. | NEU GELESEN |
| H2-S003 | oykchor · shor · chor · chy · kaiiin · dy · chodaiin | Vereinige im glasierten Gefäß zwei Zubereitungen mit dem laufenden Posten zu einer weichen Salbe für das Geschwür. | NEU GELESEN |

### H4 (f55v)

| Aussage | Oberfläche | konkrete Rücklesung | Status |
|---|---|---|---|
| H4-S001 | qokaiin · chaiin · ykain · ykan · ody | Nach Maß einsetzen; den Einsatz bemessen; Maß; Blätter zerstoßen; Weißwein zugeben; kühl lagern; Ende | beibehalten |
| H4-S002 | daiin · chedy · talam | Maß; den laufenden Posten umsetzen oder durcharbeiten; klaren Auszug verwahren | beibehalten |
| H4-S003 | ykaiin · cheoar · cheeky · oldy | Wunde waschen; Auszug daraus entnehmen; länger warm halten; weiterführen; Ende | beibehalten |
| H4-S004 | aiin · okal · oltchy · or · y · orain | Nimm das Maß, trage es an der Zielstelle auf und erwärme die Zubereitung gelind; verwende davon eine Zubereitungsportion. | NEU GELESEN |

### H5 (f56r)

| Aussage | Oberfläche | konkrete Rücklesung | Status |
|---|---|---|---|
| H5-S001 | chochor · cho · chodaly · daiin · sho · kchol · otchor · choky · dal | Pflanzenzubereitung: Nimm die Pflanze zu Blütebeginn nach Maß und lege sie auf. Für die nächste Zubereitung nimm den laufenden Posten und verwende ihn an der Zielstelle. | NEU GELESEN |
| H5-S002 | schol · choy · choky · cheeckhody | Vom vorigen Posten nehmen; mit Wasser waschen; den laufenden Posten anwenden oder in Arbeit nehmen; äußerlich anwenden; Ende | beibehalten |
| H5-S003 | sh · cho · kchey · qokokchy | Pflanzenteil; Pflanze; grob zerreiben; den laufenden Posten erneut in Arbeit nehmen | beibehalten |
| H5-S004 | okchy · chokcheo · kchal | Den laufenden Posten anwenden oder in Arbeit nehmen; Auszugsflüssigkeit zugeben; durch Tuch | beibehalten |
| H5-S005 | sho · chokchy · kchoar · sotodan | Pflanze; den laufenden Posten anwenden oder in Arbeit nehmen; Brusttrank; gebrauchen | beibehalten |
| H5-S006 | otchey · keol · daiin | Den nächsten Posten wählen; je Gabe; Maß | beibehalten |

### B1 (f81v)

| Aussage | Oberfläche | konkrete Rücklesung | Status |
|---|---|---|---|
| B1-S001 | qokedy | Kurz spülen oder benetzen und den Schritt abschließen | beibehalten |
| B1-S002 | okaiin · kair · okal · sar · ol · kain · olkain · al · ol · rol · dl · olor · ol · sheckhal · daiin · qokeedal · daiin · chckhy · schedy | Bemesse den Einsatz, führe die laufende Beckenflüssigkeit an die Zielstelle und entnimm einen abgemessenen Teil aus demselben Vorrat. Fahre am unteren Becken mit einer weiteren Portion fort. Vor dem Abkühlen gib den Badezusatz und die vorige Zubereitung in mäßiger Menge hinzu; halte den Teil nach Maß an der Zielstelle, führe ihn durch den verbundenen Lauf und schließe die Bewegung ab. | NEU GELESEN |
| B1-S003 | qol · sshkchdy | Mit Vorigem weiter; unter besonderer Bedingung umsetzen; Schluss | beibehalten |
| B1-S004 | chedy · ol · shedy | Den laufenden Posten umsetzen oder durcharbeiten; mit Vorigem weiter; kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |
| B1-S005 | qolchedy | Weiterführen; Schluss | beibehalten |
| B1-S006 | qokain · shckhy · dl · ral | Eine Portion einsetzen oder zugeben; durch verbundenen Lauf; Badezusatz; abkühlen | beibehalten |
| B1-S007 | qokchdy | Ansatz umsetzen; Schluss | beibehalten |
| B1-S008 | chey · ol · cheky · ol · shedy | Der laufende Posten; dies oder es; mit Vorigem weiter; kurz oder mild erwärmen; mit Vorigem weiter; kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |
| B1-S009 | qokedy | Kurz spülen oder benetzen und den Schritt abschließen | beibehalten |
| B1-S010 | qokedy | Kurz spülen oder benetzen und den Schritt abschließen | beibehalten |
| B1-S011 | chckhy · qoky | Durch verbundenen Lauf; den laufenden Posten anwenden oder in Arbeit nehmen | beibehalten |
| B1-S012 | lsho · qokey · lshedy | Spülung beginnen; den laufenden Posten kurz anlegen oder benetzen; waschen; Ende | beibehalten |
| B1-S013 | lshedy | Waschen; Ende | beibehalten |
| B1-S014 | chedy · qolky · lchedal · qol · otar | Den laufenden Posten umsetzen oder durcharbeiten; betroffene Stelle; Auslassstelle; mit Vorigem weiter; danach auslassen | beibehalten |
| B1-S015 | ytey · okchedy | Gefäß füllen; Ansatz umsetzen; Schluss | beibehalten |
| B1-S016 | qokal · okeey · qol · cheedy | An der Zielstelle einsetzen; den laufenden Posten anhaltend in Kontakt halten; mit Vorigem weiter; kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |
| B1-S017 | sal · teol · dchdy | Zielstelle; erste Öffnung; Umsetzung abschließen | beibehalten |
| B1-S018 | ly · dsheol · oiiin · olkeedy | Gefäß füllen; Stelle bestreichen; vorgeschriebener Grad; an der Sammelstelle stehen oder absetzen lassen; Schluss | beibehalten |
| B1-S019 | tedy | Kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |
| B1-S020 | cheky · shckhedy | Kurz oder mild erwärmen; durch Tuch seihen; Ende | beibehalten |
| B1-S021 | chal | Zielstelle | beibehalten |

### B3 (f83r)

| Aussage | Oberfläche | konkrete Rücklesung | Status |
|---|---|---|---|
| B3-S001 | olkeedy | An der Sammelstelle stehen oder absetzen lassen; Schluss | beibehalten |
| B3-S002 | qotal · chkeedy | Danach zur Zielstelle; vollständig benetzen; Ende | beibehalten |
| B3-S003 | chey · daiin · chey · lchedy | Der laufende Posten; dies oder es; Maß; der laufende Posten; dies oder es; hinausführen; Schluss | beibehalten |
| B3-S004 | qokaiin · qotal · dar | Nach Maß einsetzen; den Einsatz bemessen; danach zur Zielstelle; aus demselben Vorrat | beibehalten |
| B3-S005 | schedy | Arbeitsbewegung abschließen | beibehalten |
| B3-S006 | chedchy · qokal · olchedy | Den laufenden Posten zuführen oder umsetzen; an der Zielstelle einsetzen; weiterführen; Schluss | beibehalten |
| B3-S007 | qokaiin · chedy · qokeedy | Nach Maß einsetzen; den Einsatz bemessen; den laufenden Posten umsetzen oder durcharbeiten; eintauchen oder einweichen und den Schritt abschließen | beibehalten |
| B3-S008 | lchedy | Hinausführen; Schluss | beibehalten |
| B3-S009 | qoky | Den laufenden Posten anwenden oder in Arbeit nehmen | beibehalten |
| B3-S010 | pchedal · otedy | Einfüllstelle; danach kurz oder gewöhnlich einwirken lassen und abschließen | beibehalten |
| B3-S011 | shecthedchy · qoky · chedy · chary | Stelle bestreichen; den laufenden Posten anwenden oder in Arbeit nehmen; den laufenden Posten umsetzen oder durcharbeiten; abkühlen | beibehalten |
| B3-S012 | sor · shedy | Lasse die Zubereitung kurz ruhen; Schluss. | NEU GELESEN |
| B3-S013 | qokaiin · chkain · shcthey · qokedy | Nach Maß einsetzen; den Einsatz bemessen; abgemessener Teil; den laufenden Posten bereit halten; kurz spülen oder benetzen und den Schritt abschließen | beibehalten |
| B3-S014 | okair · sheedy | Flüssigkeit in den Lauf bringen; länger ruhen oder nachwirken lassen; Schluss | beibehalten |
| B3-S015 | lchedy | Hinausführen; Schluss | beibehalten |
| B3-S016 | lo · qokchedy | Unterer Ablauf; Ansatz umsetzen; Schluss | beibehalten |
| B3-S017 | qokeedy | Eintauchen oder einweichen und den Schritt abschließen | beibehalten |
| B3-S018 | shedy | Kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |
| B3-S019 | qokshedy | Ansatz zur Ruhe bringen oder absetzen lassen; abschließen | beibehalten |
| B3-S020 | dal · lchedy | Zielstelle; hinausführen; Schluss | beibehalten |
| B3-S021 | qokaiin · shcthy · dal · sy · saiin · shedal · shecthy · chey · tal · shcthy · dalchdy | Nach Maß einsetzen; den Einsatz bemessen; bereit; Zielstelle; der laufende Posten; dies oder es; Maß; Ruhe- oder Absetzstelle; warmes Wasser; der laufende Posten; dies oder es; Zielstelle; bereit; lokal umsetzen; Schluss | beibehalten |
| B3-S022 | qotchedy | Danach oder erneut umsetzen; Schluss | beibehalten |
| B3-S023 | lchedy | Hinausführen; Schluss | beibehalten |
| B3-S024 | tchedy | Arbeitsbewegung abschließen | beibehalten |
| B3-S025 | qokchdy | Ansatz umsetzen; Schluss | beibehalten |
| B3-S026 | cheedar · chldaiin · chedy · qokain · checthy · chealror · solkeedy | Beckenstation; absetzen lassen; den laufenden Posten umsetzen oder durcharbeiten; eine Portion einsetzen oder zugeben; bereit; bis klar; an der Sammelstelle stehen oder absetzen lassen; Schluss | beibehalten |
| B3-S027 | qoteedy | Danach anhaltend einwirken lassen und abschließen | beibehalten |
| B3-S028 | qokeey · qokedy | Den laufenden Posten anhaltend in Kontakt halten; kurz spülen oder benetzen und den Schritt abschließen | beibehalten |
| B3-S029 | sol · cheeety · qokedy | Mit Vorigem weiter; erste Spülung; kurz spülen oder benetzen und den Schritt abschließen | beibehalten |
| B3-S030 | qoky · saiin · schedair · otchedy | Den laufenden Posten anwenden oder in Arbeit nehmen; Maß; fließende Flüssigkeit durch den Lauf führen; danach oder erneut umsetzen; Schluss | beibehalten |
| B3-S031 | qokeedy | Eintauchen oder einweichen und den Schritt abschließen | beibehalten |
| B3-S032 | chedain · chedy · qotedaiin · otaiin · otedy | Eine Portion in Arbeit nehmen; den laufenden Posten umsetzen oder durcharbeiten; breites Gefäß; voriges Maß wiederholen; danach kurz oder gewöhnlich einwirken lassen und abschließen | beibehalten |
| B3-S033 | ldy | Abziehen; Ende | beibehalten |
| B3-S034 | soiiin · checthy · chety · otaiin · olsaly · shedy | Vorgeschriebener Grad; bereit; zerkleinern; voriges Maß wiederholen; untere Zielstelle; kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |

### B4 (f83r)

| Aussage | Oberfläche | konkrete Rücklesung | Status |
|---|---|---|---|
| B4-S001 | qokeedy | Eintauchen oder einweichen und den Schritt abschließen | beibehalten |
| B4-S002 | qolchey · qokeey · qokedy | Gefäß füllen; den laufenden Posten anhaltend in Kontakt halten; kurz spülen oder benetzen und den Schritt abschließen | beibehalten |
| B4-S003 | chedy · otal · otchey · qokeey · qoky · tol · shedy | Den laufenden Posten umsetzen oder durcharbeiten; danach zur Zielstelle; den nächsten Posten wählen; den laufenden Posten anhaltend in Kontakt halten; den laufenden Posten anwenden oder in Arbeit nehmen; mit Vorigem weiter; kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |
| B4-S004 | qokylddy | Den laufenden Posten als Auflage befestigen; Schluss | beibehalten |
| B4-S005 | dain · chedy · qokeedy | Durch Tuch; den laufenden Posten umsetzen oder durcharbeiten; eintauchen oder einweichen und den Schritt abschließen | beibehalten |
| B4-S006 | shckhedy | Durch Tuch seihen; Ende | beibehalten |
| B4-S007 | shckhedy | Durch Tuch seihen; Ende | beibehalten |
| B4-S008 | saiin · cheeky · sheey · qokedy | Maß; länger warm halten; erste Öffnung; kurz spülen oder benetzen und den Schritt abschließen | beibehalten |
| B4-S009 | shedy | Kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |
| B4-S010 | oldy | Weiterführen; Ende | beibehalten |
| B4-S011 | saiin · cheky · okeeol · okain · chdy · sol · lkedy | Maß; kurz oder mild erwärmen; anhaltende Anwendung mit dem Vorigen fortführen; eine Portion einsetzen oder zugeben; den laufenden Posten umsetzen oder durcharbeiten; mit Vorigem weiter; zweimal waschen; Ende | beibehalten |
| B4-S012 | lchedy | Hinausführen; Schluss | beibehalten |
| B4-S013 | qokol · shedy | Vorigen Arbeitsgang weiterführen; kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |
| B4-S014 | or · chey · qockhey · dairydy | Nimm die Zubereitung, halte den laufenden Posten über der Zielstelle und schließe den Flüssigkeitslauf ab. | NEU GELESEN |
| B4-S015 | qokain · shey · kain · chckhal · solkey · lchedy | Eine Portion einsetzen oder zugeben; klare Flüssigkeit; abgemessener Teil; Dauer; Sammelstelle kurz öffnen oder aktiv halten; hinausführen; Schluss | beibehalten |
| B4-S016 | qolkain · dal · skar · shedy | Mit einer weiteren Portion fortfahren; Zielstelle; erwärmtes Medium ausgießen; kurz oder gewöhnlich ruhen lassen; Schluss | beibehalten |

## Schluss

OR=Zubereitung plus OL/OT/AIN/HO erklärt olor/cholor, otchor/qotchor, orain, otol und chochor vorhersagbar, ohne ycheor oder oykchor wegen bloßer Buchstabenähnlichkeit umzudeuten.

Alle Stütz- und ausgeschlossenen Überlappungstuples stehen in PREPARATION_PARADIGM.tsv.
