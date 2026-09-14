# W71: Wärmezufuhr und Stofftemperatur auseinanderhalten

**Der gemeinsame W70-Ablauf ist noch keine physikalisch tragfähige Lesung.** Die alten Zustandswerte erzeugen auf f75v.45 die Folge **warm → heiß → heiß → warm**. Der letzte Wechsel stammt allein aus der programmierten Zuweisung qoky→warm. Es gibt hier keinen gelesenen Kühlvorgang, der diesen Temperaturabfall erklärt.

Das erklärt eine konkrete Schwäche der bisherigen Interpretation: „mäßig erwärmen“ beschreibt sprachlich eine Tätigkeit, während der Zustandsrechner daraus unabhängig vom Eingangszustand eine warme Endtemperatur macht. Diese beiden Behauptungen sind nicht gleichbedeutend. W09s Zuweisungsmechanismus ist bereits vorhanden und wird nicht als neue Manuskriptentdeckung ausgegeben. W70 hat ausdrücklich keine physikalische Prüfung behauptet; sein Gemeinsamkeitsbefund bleibt unverändert.

## Tatsächlich projizierte Folge

| Stelle f75v.45 | Geerbte Annahme | Zustand vor → nach | Was offen bleibt |
|---|---|---|---|
| .2 qokar | erwärmter Anteil | Anfangswert warm | kein gemessener Zustand |
| .8 qokeey | anhaltend erhitzen; W09 setzt heiß | warm → heiß | keine gelesene Dauer oder Temperatur |
| .9 qokeey | nochmals derselbe Wortwert | heiß → heiß | identischer Endwert erklärt nicht die Wortwiederholung |
| .10 otey | offen | kein Effekt angesetzt | weder Kühlung noch Zeitspanne ergänzen |
| .11 qoky | mäßig erwärmen; W09 setzt warm | heiß → warm | Abfall nicht durch gelesenen Prozess begründet |
| .12 dy | fertig | kein thermischer Effekt | W03 hat dafür keine ausführbare Abschlussanforderung |

Die Tabelle trifft in beiden Transkriptionen und beiden W69-Fassungen dieselbe Stelle. Das sind vier abhängige Projektionen, keine vier Bestätigungen.

Der vollständige Absatz f75v.43–49 wurde einbezogen: **32 Prädikatszeilen**, 16 thermische Zuweisungen, zwei thermische Aktionen ohne Material und 14 hier nicht thermisch ausgeführte Prädikate. Alle vier heiß→warm-Zuweisungen betreffen genau .45:11. [TRACE.tsv](TRACE.tsv) enthält alle Ereignisse, [READING.md](READING.md) alle Absatzwörter. Nichtthermische Prädikate wurden dokumentiert, nicht zu erfolgreichen Zustandsprüfungen erklärt.

## Zwei verschiedene inhaltliche Konzepte

| Konzept | Was die Folge behaupten würde | Stand |
|---|---|---|
| Feste Endtemperaturen | zweimal heiß machen, anschließend warm machen | dem alten Zuweisungsmodell entsprechend; angenommene Erwärmung erklärt den letzten Abfall nicht |
| Arbeitsanweisungen über Wärmezufuhr | anhaltend Wärme zuführen, wiederholen, anschließend mäßig Wärme zuführen | als bedingtes Prozesskonzept formulierbar; die Stofftemperatur danach bleibt unbekannt |

Das zweite Konzept benötigt **keine Behauptung, dass der Stoff durch qoky kälter wird**. Es bestätigt aber weder Wärme als Thema noch qoky als Wärmezufuhranweisung. Eine verringerte Wärmezufuhr, ein zeitliches „anschließend“ und die Deutung der Wiederholung sind noch nicht unabhängig gelesen. Ein verbales Schema „behandeln, behandeln, mäßig behandeln“ könnte ebenso andere Prozesse beschreiben. Es wurde kein neuer Decoder und kein alternativer Dynamikrechner gebaut.

Die sinnvolle Arbeitsformulierung lautet deshalb höchstens:

> „[Erwärmten Anteil] anhaltend erhitzen, anhaltend erhitzen, [otey offen], mäßig erwärmen; [fertig?].“

Alle vorangestellten offenen Gruppen bleiben im vollständigen Absatz erhalten. Keine gemessene Temperatur, Dauer, Intensitätsstufe oder Prozessabschlussbedingung wird ergänzt. Insbesondere wird otey nicht zur Kühl- oder Warteanweisung erklärt, um den Ablauf zu retten.

## Entscheidung

**Die thermische Endzustandsfolge wird nicht als Stütze der Übersetzung verwendet.** Die Handlungsglossen bleiben als Prozesshypothesen erhalten; eine danach als warm gesetzte Stofftemperatur ist hier unzulässige Zusatzgewissheit. Das betrifft die Interpretation dieses Entwurfs; historische W09/W28-Dateien und deren Rechenergebnisse bleiben unverändert.

Der nächste sinnvolle Inhaltstest muss die beiden Konzepte unterscheiden: Benennt ein schon angesetztes nachfolgendes Qualitätswort wirklich eine unabhängig gebundene Endtemperatur desselben Materials, oder stammt der vermeintliche Endzustand wieder nur aus der Aktionszuweisung? Vor weiterer Rechnung ist dieser konkrete Bindungsfall in den vorhandenen Qualitätsprüfungen zu suchen. Nur eine neue Verbindung von Handlung, Material und tatsächlich eigenständiger Qualitätsaussage könnte den Endzustandsansatz hier weiterbringen. dy allein liefert sie nicht. Kein automatischer neuer Wärmeparameter und keine Reparatur von otey.

## Quellen und Prüfgrenzen

W09/SPEC.json setzt qokeey=hot und qoky=warm; W09/build.py überschreibt den PHYSICAL-Wert bei ausführbaren Aktionen. W28 erbt diese Effekte. W03 liefert qokar als PROCESSED_NOMINAL/warm, aber keinen dy-Featureeintrag. W69 liefert die vollständigen Prädikatspositionen und explizit hypothetischen Materialbezüge. Die Projektion verwendet diese W69-Bezüge, **nicht** W09s andere vollständige Argument-/Eligibility-Regeln; sie ist keine erneute Gesamtzustandsprüfung. Offene Wörter könnten weitere Effekte enthalten, deren Existenz hier unbekannt bleibt.

GDT822s ältere Ganzwort-Gegenhypothese qokeey≈physisches Feuer ist nicht dasselbe wie anhaltend erhitzen. Deren Materialwechselprobleme und ungelöste Anschlüsse werden nicht als Wärmeverbbeweis übernommen.

DECISION.md vor der Projektion; `build.py` erzeugt alle Zeilen, `validate.py` prüft Eingänge, Effekte und vollständige Ereignisabdeckung. Keine neuen Seiten, Bilder oder Kontakte. Alles bereits exponiert, f84/f84r und Reserven geschlossen. Keine bestätigte Wort-/Pflanzenbedeutung, Signifikanz oder unabhängige Bestätigungskapazität. Lokale Ausführungsprüfung ist keine Physik- oder Bedeutungsprüfung.

Registryprüfung PASS; globale Prüfung weiterhin sieben bekannte ungebundene GDT600-Dateien. Lokale Ausführungsprüfung: VALIDATION.json.
