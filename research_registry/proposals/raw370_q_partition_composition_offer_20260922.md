# RAW370: q als Bindung an einen Teilungsrahmen

**Ungeprüftes Entwicklungsangebot, 22. September 2026.** Eine gemeinsame
Partitionsrestriktion lässt sich formulieren. Sie ist eine **neue Einschränkung
der alten Lesung, keine bedeutungsgleiche Zerlegung ihrer drei ganzen
Wortwerte**. Alle 65 Primärwerte, 15 Alternativformannahmen, 18 Konstruktionen
und V2-Materialeffekte bleiben als zusätzliche Bedingungen bestehen. Es wird
weder ein Wort bestätigt noch das Lexikon von 65 auf 62 Einträge verkleinert.

## Material, Vollständigkeit und Vorgänger

Grundlage sind ausschließlich die eingefrorenen JSON-Angebote
`raw370_two_paragraph_powder_partition_offer_20260922.json`,
`raw370_powder_partition_v2_material_contract_20260922.json` und die schon
geschlossene unvollständige f4r-Fortsetzung. Die begleitende JSON bindet ihre
Hashes, übernimmt die vollständigen alten Einträge, Produktionen und alle
238 Positionszuordnungen unverändert und verzeichnet sämtliche q-Positionen.
Diese Abschrift ist kein neuer Korpuszugriff oder Test. Die 82 ZL-Positionen
sowie 78 IT- und 78 RF-Positionen sind alternative Lesungen desselben
Manuskripts. 56 der 65 ZL-Formtypen sind Singletons; sämtliche Bedeutungen
wurden hypothetisch angesetzt.

Der vollständige Zensus der **80 bereits festen Formen** ergibt genau diese
drei q+Rest-Paare; keine der 15 zusätzlichen Leserformen beginnt mit q:

| q-Form | unveränderter Ganzwert | exakter Rest | unveränderter Restwert |
|---|---|---|---|
| qotaiin | SEPARATE_BY_GRADE | otaiin | WITH_SIEVE |
| qotchol | COARSE_PART | otchol | COARSE_GRIST |
| qotchy | SORT | otchy | LIFT_OUT |

In ZL stehen qotaiin auf f21r.10/G005 und f32v.8/G006, qotchol auf
f21r.10/G006, qotchy auf f32v.9/G001. IT hat dieselben vier Indizes;
RF hat f21r.10/G004,G005 sowie f32v.8/G005 und f32v.9/G001.
Die unpräfigierten Basen stehen in ZL auf f21r.10/G009 (otaiin),
f32v.8/G001 (otchol) und f32v.8/G007 (otchy).
Das bekannte f4r enthält außerdem **qotey=WATER**; siehe unten. Keine dieser
bekannten Formen ist eine unabhängige Bestätigung des jetzt entworfenen q.

Die primären Berichte GDT561/564 zeigen bereits innere Komposition angesetzter
Mikroformulierungen, keine Übersetzung unbekannter Formen. RAW442
(`raw_cennini_typed_partial_application_writer_20260920.json`) verlangt
ausdrückliche typisierte Argumente; seine Bedeutungen werden nicht importiert.
GDT1016s kontextfreie Unary-Verknüpfung ist nicht dieser ausdrücklich
teilnehmergebundene Entwurf. Die von Root geprüften GDT751/752 liefern keine
q-Bedeutung. Der neue Entwurf ersetzt keine dieser Entscheidungen.

## Genau ein gemeinsamer Relationskern, drei deklarierte Typanhebungen

Ein Teilungsrahmen F besteht aus dem aktiven ganzen Ausgangsstoff x, einem
Teilungsereignis e und der **geschriebenen geordneten Liste zweier
Produktbeschreibungen** D1,D2. Seine Ausgänge y1,y2 sind disjunkt, erschöpfen
x, bewahren dessen Herkunft und erfüllen die geschriebenen Typen und Mengen.
Positive Mengen werden von diesen Angaben verlangt, nicht von allgemeinem
GRIND. Ein geplanter Ausgang ist noch kein freier Vorrat. Die einmalige
Realisierung der Teilung macht die Ausgänge frei und verbraucht das freie
Ganze; sie erzeugt keine zusätzliche Pflanzenmasse oder Flüssigkeit.

`Q_PARTITION_BIND(D,F)` verbindet die **unveränderte Basisbedeutung D** mit
dieser einen Relation. Die folgende endliche Typanhebung ist vollständig
deklariert; weder Oberflächenname noch Folio noch gewünschter Ganzwert wählt
eine Sonderregel aus:

| semantische Eingabesignatur | Ausgabe des neuen Q |
|---|---|
| Materialprädikat D(y) | Referenz auf den eindeutigen Ausgang y von F mit D(y). Fehlender oder mehrfach passender Ausgang scheitert unter der alten Referenzregel. |
| Ereignismodifikator T(e), hier ein Werkzeugadjunkt | Teilungsereignis e von F, das zusätzlich T(e) erfüllt. |
| Handlung A(a,y,F) auf einem schon bestehenden Teil | F auf dem aktuellen ganzen x **neu realisieren**; danach A für jeden geschriebenen Ausgang von F in Listenreihenfolge ausführen. |

Formal stehen damit immer `PARTITION(F,x,{y1,y2})` und die unveränderte
Basisrelation als Konjunkte. Die Ereignisvariante ergänzt
`A(a1,y1,F); A(a2,y2,F)`. Die Materialvariante realisiert **keine zweite
Teilung**. Sie kann den geplanten Ausgang derselben Klausel beschreiben.
Eine unbekannte Eingabesignatur bleibt undefiniert; es gibt keinen
Ganzwort-Lookup als Fallback und keinen neuen unsichtbaren Teilnehmer.

Die Argumente kommen nur aus den alten ganzen Konstruktionen: P1 bindet
die nachfolgenden groben/feinen Ausgänge; P2 bindet die beiden geschriebenen
Inventargruppen davor; P3 bindet den aktiven Eingang und die folgende
vollständige KEEP-Produktliste. Die Bezeichnungen P1/P2/P3 wählen nicht die
q-Bedeutung. Insbesondere wird die alte Wirkung des P3-Kopfes SORT **nicht
als Beweis für eine aus LIFT_OUT abgeleitete Wirkung zurückgelesen**.
Die neue Partitionsrelation wird hier selbst postuliert. Dass P3 sie schon
als ganze Konstruktion verlangt, bedeutet Überlappung, keine unabhängige
Bestätigung.

Das ist ein gemeinsamer, vom Wurzelnamen unabhängiger Relationskern, aber
keine kostenlos durch Typentheorie erzwungene Ableitung: **Die drei
Typanhebungen sind drei neue semantische Festlegungen.** Gegenwärtig hat
jeder Eingabetyp nur eine gepaarte Basis. Die bekannten Fälle können daher
eine allgemeine Regel nicht empirisch von drei passend konstruierten
Typfällen unterscheiden.

## Originalwert, neue Einschränkung und Zusatzkosten

| Form | alter voller Wert | aus Basis und Q gewonnene stärkere Lesung | zusätzliche Verpflichtung / Grenze |
|---|---|---|---|
| qotaiin | nach Feinheit trennen; Verfahren kann fehlen | die gebundene Teilung mit einem Sieb durchführen | Auf f32v.8 ist SIEVE **neu**; f21r.10 nennt otaiin schon ausdrücklich. Die Feinheitsunterscheidung kommt weiterhin aus dem alten Ganzwert und den Ausgangsbeschreibungen, nicht aus WITH_SIEVE allein. |
| qotchol | grober Anteil der relevanten Feinheitsteilung | der eindeutige Ausgang dieses Rahmens, der selbst grobes Mahlgut ist | Bindung an denselben lokalen Rahmen; kein Zugriff auf beliebiges anderes grobes Material. Im alten Paar verträglich; keine Gleichheit aller denkbaren groben Anteile mit grobem Mahlgut behauptet. |
| qotchy | sortiere in die zwei geschriebenen Produkte | neue Teilung des aktiven Ganzen, danach jeden der beiden Ausgänge herausheben | Neue generative und distributive q-Semantik. Beide einzelnen LIFT_OUT behalten ihre Voraussetzung eines bereits existierenden Ausgangs und ihre Bewegungswirkung. SORT verlangte diese beiden Teilbewegungen bisher nicht. |
| qotey | WATER im unvollständigen f4r-Angebot | **undefiniert** | otey fehlt im festen Lexikon; für diese ExistingSupplyKind-Nennung fehlt außerdem ein gebundener Teilungsrahmen. Keine neue Basisglosse, keine Reparatur. |

Die Anwendung auf qotchy verändert keine Pflanzenmasse, bezeichnet aber
zusätzliche innere Teilhandlungen: erst F herausheben, dann G. Danach ist G
am Arbeitsort; das folgende alte KEEP(F),KEEP(G) endet ohnehin mit aktivem
G. Das ist eine stärkere Verfahrensbehauptung, kein bislang beobachtetes
Zwischenergebnis. Die bloße Beschränkung auf einen alten Rahmen wäre hier
unzureichend: Die alte Teilung Π0 hat C und P als Ausgänge. Alle ihre Teile
herauszuheben würde C/P bewegen und **keine** Faserstücke/Körnchen aus C
gewinnen. Q muss ausdrücklich die neue Teilung Π1 auf C erzeugen.

## Beide ganzen Absätze unter der neuen Einschränkung

Die folgende Tabelle führt jede der zehn alten vollständigen Klauselfolgen
auf. Ihre 82 Rohgruppen und festen Einzelwerte sind in der unveränderten
vollständigen Positionsabschrift der JSON erhalten. Nur die markierten
q-Verpflichtungen kommen hinzu; keine neue Satzgrenze wird gesetzt.

| Zeile | gesamte unveränderte Wertfolge / Klauseln | Bestand, Rahmen und neue q-Verpflichtung |
|---|---|---|
| f21r.8 | ACQUIRE ROOT_MATERIAL FRESH; DRY; CRUSH; FOR_OUTPUT [POWDER Q DRY_STATE] | A mit Pflanzenmasse M wird vorbereitet. Ziel Q ist eine Bedingung an späteren Ausgang, kein neuer Vorrat. Kein q. |
| f21r.9 | RINSE WATER UNTIL CLEAN; THEN SPREAD THINLY PLANT_MATERIAL EVENLY | Wasser zum Spülen, gereinigter aktiver Pflanzenstoff; Masse M bleibt. Kein q. |
| f21r.10 | DRY IN_SUN; GRIND COARSELY; SEPARATE_BY_GRADE COARSE_PART FROM FINE_PART WITH_SIEVE | Π21: B→C:c + P:p; M=c+p, c>0, p≥Q. qotaiin bindet das ohnehin genannte Sieb; qotchol bezeichnet C desselben geplanten/realisierten Rahmens. Kein zweiter Ausgang und kein zweites Ereignis durch die Referenz. |
| f21r.11 | KEEP FINE; KEEP COARSE; WITH_CLOTH COVER; THEN STORE_SEPARATELY RESIDUE | P und C erhalten; nach Auswahl von C wird C abgedeckt und getrennt gelagert. Kein q. |
| f21r.12 | RETRIEVE POWDER; SIEVE UNTIL [POWDER FINE Q CLEAN] | P wird wieder aufgenommen; Ergebnis U:Q und, falls positiv, Rest V:p−Q. C:c bleibt. Diese Verfeinerung kann zwei weiterhin feine Ausgänge haben. Kein q. |
| f32v.7 | INTRODUCE ROOT_MATERIAL; CRUSH; DRY OVERNIGHT IN_SHADE; THEN THOROUGHLY MIX EVENLY PREPARED_BULK | A→B mit Pflanzenmasse N. Kein q. |
| f32v.8 | INVENTORY [COARSE_GRIST Q Q] [POWDER Q]; SEPARATE_BY_GRADE; LIFT_OUT DEFINITE COARSE_FRACTION | CARRY/ADD: Π0 B→C:2Q + P:Q, N=3Q. qotaiin verlangt **neu ein Sieb**, ohne eine zusätzliche otaiin-Gruppe zu behaupten. Unpräfigiertes otchy hebt allein C aus dieser bestehenden Teilung heraus; P bleibt unangetastet. |
| f32v.9 | SORT WITH_SIEVE; KEEP [FIBRES Q] [GRANULES Q] | Neue Π1 auf aktivem C:2Q→F:Q+G:Q. qotchy verlangt Teilung und danach LIFT_OUT(F),LIFT_OUT(G), bevor das alte KEEP beide lagert. P:Q bleibt. Die Materialnamen stammen aus der geschriebenen Liste. |
| f32v.10 | INGREDIENTS WATER OIL [POWDER FINE Q]; KNEAD TO_RESULT [PASTE ONE PORTION] | CARRY verwendet das freie P:Q und die geschriebenen ersten Wasser-/Ölvorräte. Paste T enthält Pflanzenmasse Q, Wasser w und Öl o; Komponenten sind nicht zusätzlich frei. Kein q. |
| f32v.11 | WITH_MEDIUM WATER GRIND | T.W ist bereits enthaltenes Medium. GRIND erhält Paste, Wasser und Öl; es erzeugt aus feinem Feststoff keine grobe Fraktion und kein trockenes Pulver. F/G bleiben. Kein q. |

Damit ist die q-Verfahrensverschärfung abstrakt mit dem alten Materialfluss
verträglich. **Physische Ausführbarkeit ist weiterhin unbewiesen.** Insbesondere
müssen die beiden f32-Teilungen nicht denselben perfekten binären Siebschnitt
verwenden: Ein bereits vollständig zurückgehaltener grober Rest ließe sich
damit ohne Änderung nicht erneut in zwei positive Ausgänge zerlegen. Die
alte Lesung legte Schnitt/Sortiermerkmal nicht fest; der neue Entwurf darf
aus der gemeinsamen Werkzeugart keine Identität dieser Parameter ableiten.

## Alle Material- und Bedeutungsrivalen bleiben sichtbar

* **CARRY/ADD:** f21 endet mit C:c, U:Q und gegebenenfalls V:p−Q, insgesamt
  M. f32 endet mit F:Q, G:Q und Paste mit Pflanzenmasse Q, insgesamt 3Q.
  Wasser/Öl zählen nicht als zusätzliche Pflanzenmasse.
* **FRESH:** f21 bleibt gleich. f32s ursprüngliches B:N bleibt ungenutzt;
  .8 führt E:3Q ein, .9 erhält F/G und altes P:Q. .10 führt neues P′:Q
  für die Paste ein. Endbestand Pflanzenmasse N+4Q. Q schließt diese
  explizite alte Referenzalternative nicht aus.
* **DISJOINT_TWO_Q:** C besteht aus C1:Q und C2:Q. Nach Π1 kann F jeweils
  a und Q−a, G die Gegenanteile enthalten, 0≤a≤Q. Q erzwingt keine
  individuelle Herkunftszuordnung. Gesamtmassen entsprechen ADD.
* **REITERATED/ID:** .8 hätte nur C:Q plus P:Q. Zwei disjunkte Q-Produkte
  aus C bleiben unmöglich, selbst mit nichtnegativem Verlust. Diese alte
  bedingte Unverträglichkeit wird weder neu entdeckt noch repariert.
* **Unabhängige Ganzwörter / bloße Kategorienmarkierung:** Die drei
  Ganzwerte können ohne gemeinsame q-Relation bestehen. Dann bleibt das
  Verfahren auf f32v.8 offen und SORT muss keine zwei LIFT_OUT-Teilakte
  enthalten. Das ist ein echter Unterschied zu diesem Angebot.

## qotey, konkrete Grenzen und Entscheidung

Das schon bekannte f4r enthält qotaiin und qotchol sowie das neue
qotey=WATER. Sämtliche dortigen q-Positionen beider Leser sind in der JSON
verzeichnet. Das vollständige f4r bleibt unter seinem Entwicklungsbudget
**MISSING_BINDING**. Ohne seine fehlenden vollständigen Klausel-/Patienten-
bindungen wird hier auch keine vollständige q-Auswertung behauptet.
Für qotey ist otey weder unter den 80 alten Formen noch unter den 13 neuen
f4r-Einträgen vorhanden. Der Q-Operator kann daraus WATER nicht berechnen.
Ein universeller Anfangs-q-Vertrag hätte daher weiterhin eine konkrete
offene Eingabe- und Typbindung. Die auf die drei vorhandenen Paare
beschränkte Hypothese ist ausdrücklich keine vollständige q-Morphologie.

Eine weitere genaue Grenze liegt schon **im alten ganzen f21-Absatz**:
Π21_REFINE auf .12 ist eine Siebteilung, bei der beide Ausgänge fein bleiben
können. `Q(WITH_SIEVE,Π21_REFINE)` ist damit möglich, ohne
SEPARATE_BY_GRADE zu bedeuten. Der Operator allein erklärt also nicht den
vollen Unterschied zwischen dem festen qotaiin und dem festen sheey=SIEVE.
Der alte Ganzwert bzw. die geschriebenen kontrastierenden Ausgangstypen
leisten weiterhin unverzichtbare Arbeit. Das ist kein versteckter neuer
Textfall, sondern ein vorhandener anderer Rahmen desselben Angebots.

**Entscheidung:** Ein gemeinsamer kompositioneller **Restriktionsanteil**
existiert als ausdrücklicher Entwurf: dieselbe Teilungsrelation bindet die
Basis an Ausgang, Ereignis oder verteilte Teilhandlung. Sie erzeugt vor allem
die neue Siebpflicht auf f32v.8 und die Abhängigkeit der qotchy-Teilhandlungen
von einer neuen Teilung auf C. Es sind keine bloßen opaken Kategoriennamen.
Eine genaue Herleitung der vollständigen alten Denotationen ist dagegen
nicht gelungen; die drei Typanhebungen, der Feinheitskontrast und der
qotey-Fall lassen sich nicht als bereits erklärt verbuchen. Das Angebot ist
höchstens eine einfrierbare explorative Verschärfung. Es rechtfertigt noch
keinen Decoder, keinen neuen Zielzugriff und keinen Semantic-PASS.

Neue Kosten sind die q-Segmentierung, der gemeinsame Relationsbeitrag,
die drei ausdrücklich genannten Typanhebungen und ihre stärkeren Werkzeug-/
Teilhandlungsbehauptungen. Es gibt keine neue Glosse oder Zielauswahl.
DRY_STATEs boolesche Aktualisierung bleibt offen; die neue Relation schließt
diese alte Lücke nicht. Keine Implementierung, Simulation, statistische
Bewertung oder unabhängige Manuskriptbestätigung wurde durchgeführt.
