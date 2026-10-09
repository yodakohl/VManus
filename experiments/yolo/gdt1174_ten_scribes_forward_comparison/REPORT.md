# GDT1174 — zehn ausführbare Schreiber, kein statistisch passender Prototyp

**Alle zehn Entwürfe schreiben sinntragende Beispielnachrichten ausschließlich
mit Formen aus dem festgelegten Vorrat und lesen sie verlustfrei zurück.
Keiner erfüllt die vorab festgelegte gemeinsame Statistikprüfung. Damit ist
die Nutzerforderung nach zehn statistisch passenden Systemen noch nicht erfüllt.**

Die vollständigen menschlich lesbaren Regeln stehen in [METHOD.md](METHOD.md).
Die [Beispieltexte](artifacts/EXAMPLES.json), alle zehn vollständigen Ausgaben,
[Quellnachrichten](artifacts/SOURCE_MESSAGES.json), Programme und
[Einzelwerte](artifacts/RESULT.json) sind erhalten. Das sind erfundene Codes;
kein tatsächlich beobachtetes Voynichwort erhält einen Bedeutungswert.

## Gemessene Nähe, ohne Sieger durch Teilpunkte

Je8000 vollständige Gruppen unter der ausdrücklich festgelegten22-Formen-
Zerlegung. Die Vergleichswerte sind kein Vollmanuskriptprofil.

|Lesung|mittlere Länge|verschiedene Formen|Anteil Top10|direkte Doppelungen|
|---|---:|---:|---:|---:|
|IT2a|4.60|2451|13.31%|0.88%|
|RF1b|4.59|2530|12.60%|0.74%|
|ZL3b|4.73|2500|12.88%|0.95%|

|System|mittlere Länge|verschiedene Formen|Anteil Top10|Grenzen eingehalten IT/RF/ZL|
|---|---:|---:|---:|---:|
|1. Silbenwörter|6.97|1150|60.46%|2/2/2 von10|
|2. Stamm und Rollenendung|6.66|1150|60.46%|2/2/2 von10|
|3. Innere Rollenbeugung|6.06|1150|60.46%|1/1/1 von10|
|4. Begriffshierarchie|5.87|98|48.84%|4/4/4 von10|
|5. Fachkürzel und Buchstabierung|4.61|1150|60.46%|2/2/2 von10|
|6. Feste Satzstellen|3.66|1128|80.29%|0/0/0 von10|
|7. Ausdrückliche Rückverweise|5.59|1155|52.01%|2/2/4 von10|
|8. Änderungsprotokoll|5.79|1195|57.99%|3/3/3 von10|
|9. Stellenschrift mit Operatoren|3.00|47|90.89%|0/0/0 von10|
|10. Definition und Aufruf|3.00|626|82.60%|0/0/0 von10|

Teilpunkte sind keine Wahrscheinlichkeiten und begründen keinen Favoriten.
System5 trifft zwar die mittlere Wortlänge, schreibt aber60% seiner Wörter
mit nur zehn Formen. System7 erreicht eine ähnliche bedingte Zeichenentropie,
bleibt bei der Wortverteilung ebenfalls weit entfernt. Die weitergehenden
bekannten Kontext-, Absatz-, Ganzform- und Übertragungsbefunde sind hier noch
nicht reproduziert; bereits der kleinere notwendige Filter scheitert.

## Das gemeinsame Problem liegt vor dem Alphabet

Die Quelle enthält zwar unterschiedliche Nachrichten, zwingt aber fast alle
Schreiber in dasselbe enge Fünffelderformular. Die Felder Tätigkeit, Zusatz,
Menge und Dauer haben zusammen nur24 mögliche Werte. Material ist das einzige
breitere Feld. Das war eine zu starke Vereinfachung meiner Konstruktion.
Ein neuer Zeichenschlüssel würde diesen Fehler nicht beheben.

Die folgende **nachträgliche rechnerische Erklärung** wurde erst nach dem
registrierten Lauf formuliert; sie verändert weder Programme noch Ergebnis.
Für Systeme1/2/3/5 entfallen vier von fünf Wörtern auf höchstens24 Formen.
Selbst wenn diese vollkommen gleich häufig wären, müssten die zehn häufigsten
Formen mindestens (4/5)*(10/24)=ein Drittel des Textes ausmachen. Die gemessenen
49–91% sind deshalb nicht allein eine zufällige Schwäche des Generators.

Entsprechende Untergrenzen für vollständige Datensätze:

|Systeme|Grund|mindestens Top10-Anteil|
|---|---|---:|
|1/2/3/5|80% der Wörter in höchstens24 Formen|33,33%|
|4|sechs von sieben Wörtern in höchstens40 Formen|21,43%|
|6|vier von fünf Wörtern teilen sich acht unmarkierte Werte|80,00%|
|7|vier kleine Felder samt je einer Rückverweisform: höchstens28 Formen|28,57%|
|8|pro Auftrag höchstens ein Materialwort; Abschluss plus andere Felder tragen mindestens die Hälfte in höchstens25 Formen|20,00%|
|9|zwei feste Operatoren pro neun Wörter|22,22%|
|10|Definitions-/Aufruf-/Abschlusswörter: 2(N+D)/(7N+4D), mit N Aufrufen und D Definitionen|28,57%|

Eine eventuelle unvollständige letzte Gruppe der8000-Wörter-Probe verändert
diese Schranken nur geringfügig. Alle liegen oberhalb der großzügigen
registrierten Obergrenze von maximal18,31% für Top10. Für diese festen
Wortaufteilungen hilft daher auch kein anderes Mischungsverhältnis der
zulässigen Inhalte. Die kleinen Wörterbücher oder die Gruppierung des Inhalts
müssten sich tatsächlich ändern. Das widerlegt weder Abkürzungen allgemein
noch eine Fachsprache, Rückverweise oder sinntragende Notation im Manuskript.

## Vier vollständige Nachrichten pro System

Die Nachrichten sind: eine Portion getrocknete Minzblätter über Nacht in Wasser
einweichen; danach zwei Portionen; danach Salbei statt Minze; danach derselbe
Auftrag nochmals für eine weitere Portion. Die Wörter unten sind ausschließlich
unsere erfundenen Ausgaben. Sie sind keine behaupteten Manuskriptlesungen.

### 1. Silbenwörter

```text
deey key toteekey teedaday teedachoy
deey key toteekey teedadey teedachoy
deey deekey toteekey teedadey teedachoy
deey deekey toteekey teedadey teedachoy
```

### 2. Stamm und Rollenendung

```text
qodary ddaindy sdainin rdayol ldalor
qodary ddaindy sdainin rdainol ldalor
qodary dshaindy sdainin rdainol ldalor
qodary dshaindy sdainin rdainol ldalor
```

### 3. Innere Rollenbeugung

```text
dearn daainn doainn deeayn diialn
dearn daainn doainn deeainn diialn
dearn shaainn doainn deeainn diialn
dearn shaainn doainn deeainn diialn
```

### 4. Begriffshierarchie

```text
qodary qoday chdayy shdainy sdainin rdayol ldalor
qodary qoday chdayy shdainy sdainin rdainol ldalor
qodary qodain chdayy shdainy sdainin rdainol ldalor
qodary qodain chdayy shdainy sdainin rdainol ldalor
```

### 5. Fachkürzel und Buchstabierung

```text
qoty dchy schy rdy lky
qoty dchy schy rchy lky
qoty qodeekey schy rchy lky
qoty qodeekey schy rchy lky
```

### 6. Feste Satzstellen

```text
dar dain dain day dal
dar dain dain dain dal
dar shain dain dain dal
dar shain dain dain dal
```

### 7. Ausdrückliche Rückverweise

```text
qodary ddaindy sdainin rdayol ldalor
yqo yd ys rdainol yl
yqo dshaindy ys yr yl
yqo yd ys yr yl
```

### 8. Änderungsprotokoll

```text
qodary ddaindy sdainin rdayol ldalor dy
rdainol dy
dshaindy dy
dy
```

### 9. Stellenschrift mit Operatoren

```text
day day dain ckhy dain day dal dar cthy
day day dain ckhy dain dain dal dar cthy
dain day dain ckhy dain dain dal dar cthy
dain day dain ckhy dain dain dal dar cthy
```

### 10. Definition und Aufruf

```text
ol day dain dy
or day dar dain day dal dy
or day dar dain dain dal dy
ol dain shain dy
or dain dar dain dain dal dy
or dain dar dain dain dal dy
```


## Quellenumfang und Prüfung

Ausschließlich der bereits guarded, quellhashgebundene GDT1170-Cache wurde
verwendet. Keine neue Aufnahme, Quelle, rohe gemischte TSV oder Reserve.
f84/f84r bleiben versiegelt, f116v ausgeschlossen. Nur P-Gruppen mit sicheren
Außengrenzen und vollständiger Zerlegung gingen in die verfügbaren Streams ein.
Die erste8000-Wörter-Probe je Leser folgt der vorab permutierten Seitenfolge.

|Leser|alle P-Gruppen|verfügbare Gruppen|unsichere/Bildgrenze|Zeichen außerhalb der festen Zerlegung oder unaufgelöst|
|---|---:|---:|---:|---:|
|IT2a|31433|29821|1268|344|
|RF1b|31504|25622|2236|3646|
|ZL3b|31918|25564|5403|951|

Diese Auslassungen begrenzen besonders die RF-Abdeckung. Die drei Lesungen
sind keine unabhängigen Manuskripte. Die kleine Probe und die synthetische
Quelle rechtfertigen keine Behauptung über die ursprüngliche Sprache.

Der getrennt geschriebene Validator rekonstruiert Auswahl und Kennzahlen,
vergleicht alle gespeicherten Nachrichten mit ihrer vollständigen Rücklesung,
prüft alle einzelnen endlichen Feldwerte und verändert die physische
Zeilenbreite. Derselbe Autor, teilweise gemeinsame Encoder-/Decoderfunktionen;
keine unabhängige historische oder semantische Bestätigung. Die vorhandenen
Primärbefunde GDT288/289,608,915/916,1170 und die begrenzten früheren Misch- und
Rückverweishypothesen bleiben in ihrem eigenen Geltungsbereich erhalten.

## Entscheidung

Zehn konkrete Konstruktionen sind vorhanden; zehn passende Voynich-Systeme
sind damit **nicht** geliefert. Die statistisch notwendige Breite fehlt in der
gewählten Aufteilung der Aussagen auf Wörter. Keine dieser zehn Fassungen
wird als Übersetzungshypothese bevorzugt oder mit neuen Zeichenwerten repariert.

Ein sinnvoller weiterer Entwurf muss zuerst eine reichere, dennoch verständliche
Satz-/Wortbildung festlegen, deren häufigste festen Formen nicht schon durch
den Bauplan überrepräsentiert sind. Erst danach lohnt ein anderer Zeichenschlüssel.
Das ist die nächste Konstruktionsfrage, kein bereits gewählter neuer Lauf.
Lokaler Konstruktionscheckpoint; keine Veröffentlichung oder Außenkontakte.
