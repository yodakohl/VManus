# Entwicklungsangebot: vier gewichtete Ganzfassungen für Galen IV/V

2026-09-22, begonnen 09:48 UTC; Grenze 10:10 UTC. **Ein angebotener endlicher
Schreiber, kein ausgeführter Versuch.** Er erlaubt Makro und Komposition vorab,
ohne bei jeder späteren Abweichung eine neue Ausnahme einzuführen. Er erzeugt
prüfbare Rohtextfolgen; derzeit rechtfertigt er dennoch keinen neuen Manuskriptlauf.

## Unveränderliche Eingabe und genau eine neue Entscheidung

Eingabe sind die vollständigen Graphen, 59 Wortwerte und 88 Rohgruppen von
[RAW499](../proposals/raw_galen_2444_comparison_epistemic_target_20260921.json)
und [RAW501](../proposals/raw_galen_2445_frozen38_extension_20260921.json).
Die Quelleneinheiten bleiben Galen II.44.4/5. Keine alte Denotation, Zusatzannahme,
IT-Abweichung oder negative Quellenqualifikation wird geändert. Insbesondere
bleiben B06s zusätzliche Berichtsfähigkeit und die angenommenen Modalgrenzen
als Annahmen bestehen. Der Schreiber löst keine neue Satzgliederung.

RAW501 enthält zwei ausdrücklich wiederholte Benennungsbefürwortungen und eine
Behauptung üblichen Namensgebrauchs. B12 setzt INSIST_CALL(P,C,t) mit
INSIST(P,USE_NAME(P,t,C)) gleich. Jede der **beiden Befürwortungen** bekommt
unabhängig genau eine Wahl:

- **M**, Gewicht 1/2: INSIST_CALL wird durch das bestehende `dkshey` realisiert.
- **K**, Gewicht 1/2: INSIST und USE_NAME werden durch die bestehenden `otam`
  und `qokal` realisiert.

Die Gewichte sind eine offengelegte symmetrische Modellvorgabe nach Kenntnis des
alten Textes, keine historische Häufigkeitsschätzung. Sie gelten für beide
Stellen gleich; keine Anpassung an Absatz, Blatt, Schreiber, Erfolg oder Inhalt.
Keine dritte Realisierung, kein zusätzlicher Alias und kein Raten unbekannter
Wortwerte ist zulässig. Der übliche Namensgebrauch in C02 besitzt kein INSIST
und behält sein einzelnes `qokal` mit Gewicht 1.

## Vollständig begrenzte Schreibregeln

Ausgangspunkt ist RAW501 `selected_target.full_record`, die ganze vierzeilige
33-Gruppen-Fassung. RAW499s ganze 55 Gruppen werden unverändert vorgeschaltet.
Die folgenden disjunkten Ersetzungen definieren **sämtliche** Varianten;
alle übrigen Gruppen, Unsicherheitszeichen und ihre Reihenfolge bleiben literal.
Die Originalpositionen adressieren nur die bereits gebundenen Eingabespannen.
Ausgabe ist die geordnete Folge ganzer Gruppen; ein neuer physischer Zeilenumbruch
wird nicht modelliert. Die historischen ZL-/IT-Daten selbst werden nicht verändert.

| Graphrahmen | M | K |
|---|---|---|
| C01, ursprüngliche Positionen 1–4; erste Benennung mit Namenseinführung | `psheoldy dkshey qokopy ror` | `psheoldy otam qokopy ror qokal` |
| C03, ursprüngliche Positionen 25–27; wiederaufgenommene Befürwortung | `dchedy dkshey` | `otam dchedy qokal` |

C01-K stellt den Namen `ror` vor den neuen Gebrauchskopf `qokal`; es wird keine
ungebundene Vorwärtsreferenz erfunden. Die geschriebenen P- und C-Argumente
bleiben `psheoldy` und `qokopy`. C03 behält seine geschriebenen Argumente
`dchedy`, das vorherige `okal` und die folgenden C-Referenzen `dal`/`shedy`.
Die vorhandene Graphstruktur bestimmt die Reichweite von INSIST in beiden
Realisierungen. Die rhetorische C01-Fortsetzung, ihr Einschub, der C02-Satz und
der C03-Sach-Recap bleiben vollständig erhalten.

**Explizit gezahlte neue Konstruktionen:** Die beiden Tabellenrahmen erlauben
genau diese variable Operatorstellung. C03-M macht außerdem den in INSIST_CALL
enthaltenen USE_NAME-Inhalt über B12 für die schon vorhandenen TO/OF-Projektionen
zugänglich. Sonst würden diese Wörter ihre Argumente verlieren. Das ist eine
vorab lizenzierte Makroentfaltung, keine neu bestätigte Syntax. Eine Alternative,
die diese Entfaltung nicht erlaubt, kann C03-M nicht lesen; sie wird nicht nach
einem Ergebnis heimlich repariert.

Als einzige innere Wortbauregel wird `q+okal` zugelassen: q hebt die vorhandene
Name-Referenzfunktion SAME_NAME zu USE_NAME an, mit zusätzlich geschriebenem
Sprecher- und Pflanzenargument. Der aktuell gebundene Name bleibt identisch.
Diese Regel gilt **nur für diesen Name-Referenztyp und diesen bekannten Stamm**.
Andere q-Wörter behalten ihre ganzen Werte; insbesondere bleibt
`okaiin=ATHENIANS` gegenüber `qokaiin=AND` unverändert. Damit wird keine allgemeine
q-Morphologie behauptet. Die Makroentfaltung und die q-Regel sind unterschiedliche,
beide ausdrücklich bezahlte Konstruktionen.

## Eine echte, vollständig bestimmte Oberflächenkonsequenz

Sei c die Zahl der K-Wahlen. Es gibt genau vier vollständige Ausgaben mit je
Gewicht 1/4. Für den ganzen RAW501-Absatz gilt zwingend:

`#dkshey = 2−c;  #otam = c;  #qokal = 1+c;  Gruppen = 32+c`.

| C01/C03 | c | dkshey / otam / qokal | Gruppen RAW501 | Gruppen zusammen | Gewicht |
|---|---:|---:|---:|---:|---:|
| M/M | 0 | 2 / 0 / 1 | 32 | 87 | 1/4 |
| M/K, die alte Fassung | 1 | 1 / 1 / 2 | 33 | 88 | 1/4 |
| K/M | 1 | 1 / 1 / 2 | 33 | 88 | 1/4 |
| K/K | 2 | 0 / 2 / 3 | 34 | 89 | 1/4 |

Folglich sind `#dkshey+#otam=2` und `#qokal−#otam=1` obligatorisch, obwohl kein
einzelner Befürwortungsinhalt auf genau eine Wortform festgelegt wird. Eine ganze
Realisierung desselben Eingabegraphen mit zusätzlichem/fehlendem Kopf oder einer
fünften Realisierung hat Wahrscheinlichkeit null. Innerhalb der vier erlaubten
Ausgaben ist hingegen kein einzelnes Ergebnis ein Gegenbeweis. Zwei gleich lange
33-Gruppen-Ausgaben bleiben verschieden; bloße Gruppenzählung ersetzt den
Vollvergleich nicht. Die angegebene Verteilung wird nicht an Beobachtungen angepasst.

Das ist mehr als eine freie Liste von Glossen: Diese Liste allein erzwingt weder
Kopf-Kopplung noch Längenänderung. Die Folgerung betrifft wirkliche Schreibungen,
nicht eine weitere erfundene Namenswelt. Sie ist hier schriftlich hergeleitet,
nicht als neues Manuskriptergebnis getestet.

## Warum daraus derzeit noch kein sinnvoller Zieltest folgt

Der Schreiber ist konditional auf **genau den vollständigen bekannten Graphen**.
Er behauptet nicht, jeder andere Absatz müsse dieselben zwei Befürwortungen,
denselben Gebrauchssatz und dieselben Ergänzungen enthalten. Eine neue Zielstelle
erst nach Sichtung passend so zu deuten, würde die Vorhersage wieder aufheben.
Die 1/2-Wahl löst die bisher freie Lexikalisierung, aber weder Quellenzuordnung
noch Modalgrenzen oder die Auswahl einer weiteren gleichartigen ganzen Aussage.

Die stärkste unmittelbar verfügbare Erweiterung wäre ein vollständiges weiteres
Exemplar genau dieser vier Fassungen. Sie wäre äußerst eng: Alle Fassungen
behalten etwa `cheey daiin shey` aus der ankerfähigen f80v.20 und `chey dal or`
aus der ankerfähigen f80v.22. Bei ebenfalls getrennten ankerfähigen Zeilen eines
anderen Blatts wären das zwei disjunkte exakte Anker. Genau solche Absatzpaare
sind im vorhandenen [GDT928-Census](../../experiments/yolo/gdt928_multi_anchor_complete_paragraphs/REPORT.md)
nicht vorhanden. Andere Umbrüche/unsichere Zeilen werden dadurch nicht
widerlegt, liefern aber auch keinen benannten neuen prüfbaren Kandidaten. Kein
erneuter Census und keine nachträgliche Lockerung der Anker folgt daraus.

Außerdem erzeugt ein Schreiber, der `qokal` als opakes ganzes Wort behandelt und
dieselben vier Satzregeln samt Gewichten verwendet, **exakt dieselbe Verteilung**.
Auch perfekte neue Vorhersage träfe daher die begrenzte Schreibgrammatik, ohne
q als Bedeutungsbaustein auszuwählen. Das ist die konkrete verbleibende Rivalität,
nicht ein pauschales Verbot hypothetischer Bedeutungen.

## Entscheidung und Kosten

**Als endliches Entwicklungsangebot erhalten; keinen neuen Lauf auswählen.**
Der Makro-/Kompositionswechsel ist jetzt begrenzt und erzeugt überprüfbare
Oberflächenfolgen. Für einen Manuskriptversuch fehlen aber eine vor ihrer
Deutung nominierte weitere vollständige Graphinstanz und eine vom opaken
Ganzwortschreiber unterschiedliche Folgerung. Zusätzliche unbewertete Aliase,
variable Gewichte oder neue Bereichsgrenzen würden diese Lücken nicht schließen.

Das berücksichtigt [IDEA72s konkrete Grenze](ld_idea72_method_review.json):
Eine vorab lizenzierte Ganzform muss nicht jede Schriftvariation blockieren.
[GDT995](../../experiments/yolo/gdt995_conditional_suffix_inverse/METHOD.md)
motiviert eine vollständige Schreibverpflichtung, verleiht diesem neuen
Voynich-Schreiber aber keine historische Evidenz. GDT979/994/997/998/999/1016
und 915/916 bleiben mit ihren registrierten Grenzen unverändert; weder ihr
Corpuslauf noch ihr gescheiterter Code wird neu aufgesetzt.

Budget: höchstens 22 Minuten Primärlektüre, Entwicklung und Dokumentprüfung;
Abschluss 09:59 UTC nach ungefähr elf Minuten. Implementierung, neue Corpussuche
und wissenschaftliche Ausführung null.
Keine neue Quelle, Abbildung, Reserve, Kontakt- oder Registeränderung.
