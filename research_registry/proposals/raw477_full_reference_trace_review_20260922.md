# RAW477: vollständiger Referenzvertrag und gemeinsame Vergleichsfolge

2026-09-22. Unabhängige Entscheidungsvorbereitung, keine Auswahl, kein Lauf und
keine neue Lesung. Die Originaldateien bleiben unverändert. Gegenstand ist der
vollständige bereits exponierte GDT1015-Arbeitsabsatz f82r.11–19 mit 80 Positionen,
60 geratenen Werten und zwölf gesetzten Konstruktionen. Dies ist die normalisierte
Arbeitskopie: diplomatisch stehen an f82r.15:4 `qok[ee:ch]dy` und an f82r.16:11
`ra{cty}` statt `qokeedy` und `ra`. Keine Normalisierung wird neu zugelassen.

## Entscheidung

Ein kleiner gemeinsamer Vergleich ist vertretbar: Veröffentlichung des lokalen
Ergebnisses vor/nach SAME und verbrauchender/nichtverbrauchender Abruf haben eine
echte **Interaktion im gesamten geschriebenen Argument**. Jede Einzeländerung
belässt einen A/B-Vergleich; gemeinsam machen sie beide Vergleiche reflexiv.
Das verändert, welche Gleichheit der ganze Entwurf behauptet. Es ist weder eine
Bestätigung der Stunden-/Planetenwerte noch ein neuer mathematischer Befund.

Nach Abstimmung vor Auswahl: sechs feste Regeln. Die vier lokalen typisierten
Fassungen bilden das 2×2 aus Publikationszeit und Verbrauch. Hinzu kommen UNTYPED
(verzögert, lokal verbrauchend, ohne Typfilter bei Auswahl) und GLOBAL (verzögert,
typisiert verbrauchend, ohne lokalen Reset). Der abschließende Präregistrierungs-
Zusatz unten legt Registry, Recency und wahrheitsunabhängige Publikation fest.

## Unveränderliche Objekte und Funktionsargumente

- `D`: die in C01 definierte allgemeine DAY-Einheit. Eine spätere DAY-Nennung
  aktualisiert ihre Erwähnung, erzeugt aber kein neues Individuum.
- `U`: die allgemeine HOUR_UNIT. HOUR in C03/C06/C10 kann dieselbe Einheit nennen;
  die quantifizierten Stundenvariablen in C08 und der ordinale Endpunkt in C10
  sind keine frischen HOUR_UNIT-Antworten für den Iterator.
- `H`: der durch C02 einmal gebundene Siebenerkreis. `s=CYCLE` in C09/C11 und
  NEXT_MEMBER in C03/C08 benutzen diesen globalen Modellparameter.
- `N`: die in C07 festgelegte DAY_COUNT, Wert 24. DAY_COUNT in C09 ruft N ab,
  statt bei seinem eigenen Abruf eine neue Tageszählung zu erzeugen.
- `i`: freie Anfangsphase des gesamten Arguments. C04s Name aus dem Anfang,
  C05s Auswahl, C10s Beginn und C11s gemeinsamer Beginn benutzen dieses gleiche
  schon vorher gesetzte Argument. C04 ruft keinen erst in C05 erzeugten historischen
  RULER-Diskursreferenten ab. Diese Parameterbindung ist eine alte Annahme.
- `A`, `B`: zwei Methodenobjekte; `RA`, `RB`: deren getrennte Ergebnisrecords.
  Ergebnisidentität ist Herkunft aus einer Rechnung, nicht Gleichheit des Werts:
  RA und RB bleiben verschiedene Records, auch wenn beide denselben Herrscher
  als Wert haben. Die Vergleiche prüfen die Werte, nicht Recordidentität.

Diese Liste ist **kein universelles neues Verfahren für alle Nominalausdrücke**.
Die Konstruktionen behalten ihre alten lokalen Variablen, Funktionsargumente und
globalen Parameter. Ein solcher Vollvertrag darf deren verbleibende Setzung nicht
als Ergebnis der sieben FETCH-Aufrufe ausgeben.

## Vollständige Spur über alle zwölf Konstruktionen

Die Tabelle beschreibt die vorher festzulegende Hauptspur (typisiert, lokal
verbrauchend, verzögert publizierend). Sie ist eine schriftliche Ableitung aus
den bereits verfassten Konstruktionen, keine neue Ausführung.

| Konstruktion / Positionen | Registrierung und unveränderte Bindung | Abruf / Folge |
|---|---|---|
| C01 / 1–8 | D wird als DAY definiert; DAYLIGHT ist sein Teil. Die Grenze bleibt unbestimmt. | Kein rückwärtiger Auswahlaufruf. |
| C02 / 9–16 | H wird als globaler Kreis definiert; Kardinalität 7 bleibt geraten. | Kein rückwärtiger Auswahlaufruf. |
| C03 / 17–24 | U als allgemeine HOUR_UNIT ist verfügbar; NEXT_MEMBER verwendet H. Fortgang ohne RESET bleibt alter Inhalt. | Kein behaupteter Abruf einer bestimmten schon vergangenen Stunde. |
| C04 / 25–29 | Name wird funktional aus der gemeinsamen Anfangsphase i abgeleitet. | F1: FETCH(DAY) → D; lokal U_used={D}. |
| C05 / 30–33 | Anfangsherrscher ist H(i); START ist der Anfang der schon definierten DAY-Einheit. Keine neue Tagesidentität. | Kein weiterer freier Antezedent gewählt; globale Parameterbindung bleibt als Annahme. |
| C06 / 34–39 | DAY36 erwähnt wieder D; HOUR37 wieder U; RULER39 ist die Zuordnung durch H. NIGHT bleibt Teil von D. | Keine neue DAY/HOUR_UNIT-Identität aus Wiedererwähnung. |
| C07 / 40–43 | Neues lokales U_used. Nach Abschluss wird N=24 registriert. | F2 an40: FETCH(DAY) → D; F3 an43: FETCH(HOUR_UNIT) → U. Beide THIS benutzen dieselbe Funktion, verschiedene verlangte Typen. |
| C08 / 44–47 | Zwei gebundene Stundenvariablen: Nachtstunde h und ihr Nachfolger. NEXT_MEMBER benutzt H. | Nicht zwei auswählende Rückverweise auf ein bestehendes Stundenindividuum; keine neue Regel für diese alten lokalen Variablen. |
| C09 / 48–55 | CYCLE51 benutzt global H. Der Rest wird aus N und drei H-Umläufen berechnet. | F4 an54: FETCH(DAY_COUNT) → N. Der CYCLE-Bezug ist als globale Parameterverwendung ausdrücklich deklariert, nicht als Iteratorerfolg. |
| C10 / 56–63 | DAY60 erwähnt D, HOUR62 die Einheit bzw. den ausdrücklich konstruierten Endpunkt. Methode A und RA werden bei Abschluss registriert. | A berechnet seinen Ergebniswert aus i und dem alten Endpunktvertrag. Keine nach Ergebnisgleichheit gewählte Referenz. |
| C11 / 64–75 | B ist lokal geöffnet; zwei ONE_MEMBER-Operanden bleiben getrennt. H und i unverändert. RB ist spätestens nach REACH74 lokal berechenbar. | F5 an75: FETCH(RULER_RESULT) → RA; prüfe value(RB)=value(RA). Erst anschließend werden B und RB für spätere Abrufe publiziert. |
| C12 / 76–80 | Neues lokales U_used. HOUR79/RULERSHIP80 projizieren die zu vergleichenden Ergebniswerte; keine Gleichsetzung absoluter Stunden. | F6 an76: FETCH(METHOD) → B; F7 an78: FETCH(METHOD) → A, da B schon lokal benutzt. Prüfe value(B)=value(A). |

FETCH aktualisiert eine Erwähnung desselben Records, vervielfältigt ihn nicht.
Bei Verbrauch wird genau diese Recordidentität in U_used eingetragen. Lokaler
Reset geschieht vor jeder der zwölf vorhandenen Konstruktionen; globaler Reset
initialisiert die Menge nur einmal am Absatzanfang. Ein leerer typkompatibler
Abruf stoppt die betreffende vollständige Regelspur als ungebunden. Spätere
Vergleiche sind dann nicht ausgeführt, nicht widerlegt.

## Vollständigkeit der sieben Stellen: enge zulässige Aussage

Die sieben Stellen sind die expliziten Auswahlfelder der Rohkarte. Sie umfassen
**nicht alle textübergreifenden Identitätsbindungen** der alten Lesung. Gerade
C09 `cycle:C02`, C11s CYCLE/H und die START-/Anfangsbindungen müssen sichtbar als
globale Argumente bleiben. Die Wahl, H als einmal benannten Parameter und N als
abrufbaren Diskursrecord zu behandeln, ist ein Bestandteil dieses begrenzten
neuen Vertrags; sie folgt nicht aus dem Erfolg des Iterators.

Wer stattdessen jeden nominalen Kreisverweis als FETCH zählen möchte, muss vor
Auswahl ausdrücklich zwei weitere Aufrufe an C09:51 und C11:73 registrieren und
den Scope ändern. Diese Erweiterung darf nicht erst bei Problemen erfolgen.
Sie ist für die hier diskutierte Publikations-/Verbrauchsinteraktion nicht
erforderlich. Die Rohkarte ist also als enger Siebenstellenvertrag vollständig
deklarierbar, aber nicht als bereits begründete universelle Referenzgrammatik.

## Gemeinsame Vorhersage der vier lokalen Fassungen

EAGER bedeutet: B und RB werden unmittelbar nach dem lokal bestimmten Ergebnis
(vor SAME75) publiziert. DEFERRED bedeutet: erst nach der Vergleichsprüfung am
Ende von C11. Das ist die einzige zeitliche Änderung. Keine Veröffentlichung
entscheidet anhand des gewünschten Wahrheitswerts.

| Veröffentlichung | Abruf | C11 SAME75 | C12 METHOD76/78 | Verpflichtung des ganzen Absatzes |
|---|---|---|---|---|
| DEFERRED | CONSUMING | RB = RA | B = A | Zwei geschriebene A/B-Vergleiche, logisch dieselbe Wertgleichheit. |
| DEFERRED | NONCONSUMING | RB = RA | B = B | A/B bleibt durch C11 verpflichtend. |
| EAGER | CONSUMING | RB = RB | B = A | A/B bleibt durch C12 verpflichtend. |
| EAGER | NONCONSUMING | RB = RB | B = B | Kein A/B-Vergleich mehr aus diesen beiden Konstruktionen. |

Die Gegenprobe muss den **ganzen Absatz** behandeln: Das Verschwinden nur einer
Kante beweist keinen Verlust der Gesamtverpflichtung. Alle Hauptrechnungen können
in allen vier Fassungen zufällig/stipuliert dieselben Werte liefern; die
unterschiedlichen Abhängigkeiten sind dann dennoch nicht identisch.

Beim GLOBAL-Verbrauch sind beide CONSUMING-Fassungen bereits an F2/C07:40 leer:
F1/C04 hat D verbraucht, und C06 erwähnt nur dasselbe D erneut. NONCONSUMING
macht den Resetbereich wirkungslos; die entsprechenden Duplikate bleiben im
gedachten achtteiligen Faktorwürfel; ausgewählt vorgeschlagen sind nur die oben
genannten sechs Regeln. Kein frisches DAY aus C06 darf diesen Stopp reparieren.

## Aussagegrenze und kleinster sinnvoller Auswertungsumfang

Eine spätere kleine Auswertung darf die alten vollständigen rivalischen
Rechnungsfassungen als klar bezeichnete Sensitivitätsfälle mitführen: Sie sind
bereits vorhandene Gegenmodelle, keine neuen Zahlen-/Glossenanpassungen. Falls
eine solche Fassung A≠B ergibt, erlauben drei lokale Referenzfassungen den
abschließenden Gleichheitsanspruch nicht; nur EAGER+NONCONSUMING kann beide
Vergleiche tautologisch machen. Die alte gesetzte C09-Restbedingung, C03/C08-
Inhalte und sonstigen Pflichten bleiben zusätzlich bestehen. Das Beseitigen
zweier Vergleiche beweist keine Gesamtverträglichkeit jedes alten Rivalen.

Stärkster Gegenfall: Selbstvergleiche und wiederholte Verweise sind sprachlich
möglich. Ohne unabhängig gebundenes Nichtreflexivitäts- oder Abschlusszeichen
wählt das Manuskript allein den Iterator nicht aus. Der Gewinn wäre ein kleinerer
vollständiger bedingter Bindungsvertrag mit einer expliziten gemeinsamen Folge,
nicht ein Bedeutungsbeweis und kein Anlass für eine weitere Solverkette.

Primärgrundlagen: RAW477 JSON; GDT1015 MODEL_v01.json, READING_v01.md, REPORT.md und
SCOPE_CORRECTION.md. GDT933/GDT947 werden in RAW477 als Grenzen beibehalten; die
alten Gegensatz-/Backward/Forward-Verträge werden hier weder ausgeführt noch
geändert. Kein Zielcensus, kein Test, keine Quelle oder Metadatenmutation.

## Verbindliche Präregistrierungspräzisierung vor Auswahl

Abstimmung 16:34 UTC, noch kein Lauf und keine Registrierung. Diese Präzisierung
ist Teil des abgeschlossenen Angebots und geht ungenauem Kurztext oben vor.

**Falsche Gleichheiten stoppen die strukturelle Publikation nicht.** Beide
Vergleichswahrheiten werden protokolliert. DEFERRED publiziert B und RB am
strukturellen Ende von C11 auch dann, wenn SAME falsch ist. Danach ist C12
weiterhin auswertbar. Nur eine fehlende/typwidrige Referenz macht die nachfolgende
Spur ungebunden. Der Resolver bekommt keine Ergebniswahrheiten und keine
gewünschten Antezedent-IDs.

EAGER publiziert B und RB unmittelbar nach REACH74 vor SAME75 ausdrücklich
query-sichtbar. Ein bloßer Schattenrecord mit completed=false wäre keine EAGER-
Variante. METHOD A und Ergebnis RA sind verschiedene Records; ebenso B/RB.
RA und RB bleiben wegen ihrer Herkunft aus verschiedenen Rechnungen verschieden, auch
wenn ihr Herrscherwert gleich ist. Vergleiche prüfen Werte, nicht Recordidentität.

Nur DAY, HOUR_UNIT, RULER, DAY_COUNT, METHOD und RULER_RESULT sind in dieser engen
Registry zulässige Typen. CYCLE, NIGHT, DAYLIGHT, NAME, i und die lokalen
Stundenvariablen bleiben deklarierte globale/funktionale/lokale Argumente. Das
ist eine neue explizite Domänenannahme, keine allgemeine Diskurstheorie.

| Stelle / Ereignis | Vollständige Registrywirkung im gewählten Bereich |
|---|---|
| DAY2, Abschluss C01 | D entsteht und wird sichtbar. |
| HOUR19, Abschluss C03 | U entsteht als Einheitsdescriptor und wird sichtbar. Vor F1/C04 ist U der jüngste zugelassene Record. |
| F1/C04 | Erfolgreicher Abruf erwähnt D erneut, ohne neue Identität. |
| RULER32, Abschluss C05 | R_init wird als RULER-Descriptor der gemeinsamen Anfangsphase sichtbar; kein RULER_RESULT einer Methode. |
| DAY36 / HOUR37 / RULER39, C06 | D und U werden in dieser Reihenfolge erneut erwähnt. Anschließend wird R_hour sichtbar, der RULER-Descriptor der allgemeinen Stunden-Zuordnung in C06. Er ist als lokal anders gebundener Descriptor von R_init unterschieden; kein gewünschter Ausgabewert wird ausgewählt. |
| THIS40 / THIS43 | F2/F3 erwähnen bei Erfolg D/U erneut. |
| Abschluss C07 | N entsteht nach den Abrufen mit dem bereits gesetzten Wert24; Typ DAY_COUNT. |
| HOUR44 / HOUR46 | Beide erwähnen Einheitsdescriptor U; die zwei verschiedenen lokalen Stundenvariablen erzeugen keine neuen U-Identitäten. Diese Trennung von Einheit und Instanz ist eine offengelegte Modellannahme. |
| DAY_COUNT54 | F4 erwähnt N erneut. |
| DAY60 / HOUR62 | Erwähnen D beziehungsweise U erneut. Der ordinale Endpunkt ist ein lokales Argument. |
| Abschluss C10 | Zuerst A, dann RA publizieren. |
| OTHER_METHOD64 | B lokal öffnen, noch nicht query-sichtbar. |
| Nach REACH74, vor SAME75 | RB lokal verfügbar. Nur EAGER publiziert jetzt B, dann RB. |
| SAME75 | F5 erwähnt den ausgewählten Ergebnisrecord erneut. |
| Abschluss C11 | DEFERRED publiziert B, dann RB unabhängig von der Vergleichswahrheit. EAGER erzeugt keine Duplikate oder zweite Veröffentlichung. |
| METHOD76 / METHOD78 | F6/F7 erwähnen ihre Methoden erneut; verbrauchte Identitäten bleiben lokal gesperrt. |
| HOUR79 | Erwähnt U erneut; danach kein weiterer Abruf. |

Recency folgt genau dieser Ereignisreihenfolge, bei Publikationslisten deren
angegebener Reihenfolge. Aktualisierte Erwähnungen löschen keine verbrauchte
Identität aus U_used. UNTYPED wählt ohne Typfilter aus derselben endlichen
Registry; danach prüft die Konstruktion unverändert den geforderten Typ. Es
scheitert bereits F1/C04: U ist jünger als D und ist kein DAY. RULER39 an C07
ist ein zusätzlicher erklärender Gegenkontext, kein erster Fehler dieses Laufs.

Die alten 357 arithmetischen Zeilen können als eingefrorene Ergebnispaare dienen.
Ihre Varianten behalten alle ursprünglichen Wort-/Grammatikänderungskosten und
übrigen Pflichten; sie werden nicht zu 357 neuen Manuskriptbeobachtungen. Für
A≠B bleibt unter DEFERRED+CONSUMING, DEFERRED+NONCONSUMING und EAGER+CONSUMING
jeweils mindestens eine falsche Vergleichsbehauptung sichtbar. Nur die kombinierte
EAGER+NONCONSUMING-Regel nimmt beiden Vergleichen die A/B-Verpflichtung. Dies
behauptet keine automatische Gesamtverträglichkeit aller alten Rechenrivalen.
