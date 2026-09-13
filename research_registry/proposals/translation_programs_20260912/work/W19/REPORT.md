# W19 – die Wiederholungsfolge übersteht alle drei vorhandenen Lesungen

**Der lokale R-Entwurf auf f102v2 bleibt in ZL3b, IT2a und RF1b erhalten.**
Alle drei lesen dieselben früheren `okeey`-Aktionen auf .36:3 und .36:8. Unter
dem festen erneuerten Flüssigkeitsbezug nimmt `sho` auf .38:7 deren Bestand auf;
`ykeey` auf .38:8 hat damit in jeder Lesung die gleiche konkrete Vorgeschichte
für „erwärme erneut“. Die E- und P-Gegenfassungen liefern diese Zeugen nicht.

Das neue Ergebnis betrifft die Abhängigkeit von der Transkription. Es ist
**keine unabhängige Bestätigung einer Übersetzung**: Die drei Texte lesen dasselbe
Manuskript, mit denselben frei hypothetischen Wortkarten und Referenzverträgen.
W18s neuer lokaler Anschluss wird gegen eine weitere Unsicherheit geprüft;
kein neuer Satz und kein weiteres Wort werden als übersetzt ausgegeben.

## Vorher registrierter vollständiger Vergleich

[DECISION.md](DECISION.md), [SPEC.json](SPEC.json), IDEA000217. Alle 13 bereits
exponierten W02-Absatzbereiche und sämtliche zugehörigen gespeicherten IT/RF-Loci.
Alle fünf ykeey/yteey-Stellen, E/P/R und B/J/M. Vorherige Wirkung, Identität und
Ausführungsreihenfolge bleiben fest. W18s primäre ZL-Zeugen müssen exakt
reproduziert werden; das ist erfüllt. W15s frühere Prüfung ohne R-Referenz bleibt
unverändert und ist kein widersprechendes Ergebnis derselben Objektkarte.

Alle 2.763 festen Verarbeitungsargumente wurden übernommen, alle 135 abhängigen
Zielprüfungen und 837 früheren Aktionspaare ausgewertet. Ungültige oder wirkungslose
Vorgänger sowie andere Objekte und andere Wirkungen sind ausdrücklich erhalten:
[ALL_PRIOR_ACTIONS.tsv](ALL_PRIOR_ACTIONS.tsv). Kein passend gewählter einzelner
Vorgänger; beide vorhandenen Erwärmungszeugen werden ausgegeben.

## Konkrete Vorhersage und beobachtete Übertragung

| Lesung | R-Referent von sho .38:7 | Frühere Aktionen am selben Objekt | R: REP für ykeey .38:8 | E / P |
|---|---|---|---|---|
| ZL3b | qokeol f102v2.35:9 | okeey .36:3 und .36:8 | vorhanden | beide ohne exakten Zeugen |
| IT2a | qokeol f102v2.35:9 | okeey .36:3 und .36:8 | vorhanden | beide ohne exakten Zeugen |
| RF1b | qokeol f102v2.35:8 | okeey .36:3 und .36:8 | vorhanden | beide ohne exakten Zeugen |

RF hat eine andere Gruppenposition des qokeol-Ankers; sie wird nicht normalisiert.
B/J/M liefern dieselbe Zielkonsequenz. Die 18 Zeugenzeilen sind **zwei vorherige
Befehle an einer Manuskriptstelle**, jeweils unter drei Grammatikfassungen und
drei Transkriptionen. Sie sind keine 18 unabhängigen Belege.

Die bedingte Mehrschrittlesung bleibt damit:

> Eine als erhitzte Flüssigkeit bezeichnete Portion wird vorsichtig erwärmt;
> ein weiterer gleicher Erwärmungsbefehl folgt. Die später wiederaufgenommene
> Flüssigkeit soll „erneut erwärmt“ werden.

Das ist keine lückenlose Wiedergabe des Absatzes. Alle offenen Gruppen bleiben
in der vollständigen [W17-Arbeitslesung](../W17/READING.md) und der
[W17-Worttabelle](../W17/ALIGNMENT.tsv) erhalten. Die genauen Zielzeilen in allen
Lesungen stehen in [CONTEXTS.tsv](CONTEXTS.tsv).

## Sämtliche übrigen Wiederholungsstellen

| Zielstelle | ZL3b E/P/R | IT2a E/P/R | RF1b E/P/R |
|---|---|---|---|
| ykeey f17v.20:1 | kein exakter Zeuge | gleich | gleich |
| yteey f86v5.21:5 | kein exakter Zeuge | gleich | gleich |
| yteey f86v5.21:9 | kein exakter Zeuge | gleich | gleich |
| ykeey f86v5.22:2 | kein exakter Zeuge | gleich | gleich |
| ykeey f102v2.38:8 | nur R, zwei Zeugen | gleich | gleich |

Kein exakter Zeuge bedeutet keine frühere gültige Aktion mit **demselben Zielwert**
im festen Absatzmodell. Die bekannte frühere heiße Behandlung auf f17v J/M
wird dadurch nicht bestritten. Externe Vorgeschichte ist nicht geprüft.

## Verbleibende Probleme und Entscheidung

**Den f102v2-R-Entwurf als gegen diese Transkriptionsunterschiede stabil behalten.**
Die Auszug-Heizbefehle qokeor .36:9 und .38:4 bleiben unter R typologisch
unvollständig. Die interne Referenzregel hat weiterhin keinen Anker bei sho
auf f22v/f45v. E/P/R werden nicht je nach gewünschter Konsequenz gemischt.
Kein globaler Referenz- oder Wortbedeutungssieger.

W19 prüft ausschließlich Aktionsvorgeschichte. Es übernimmt keine ZL-Qualitäten
in IT/RF und behauptet dort keinen warm-MATCH, keine vollständige physische
Plausibilität, keine Kühlung und keine Wiederherstellung REST. Der Umstand,
dass die zwei früheren Erwärmungsereignisse vorhanden sind, ist von W18s
problemabhängigem aktuellen warm-Zustand getrennt zu halten.

Die bestehenden Wortwerte bleiben vollständig unverändert: 534 hypothetisch
belegte, 366 ungelesene primäre Positionen. Kein Herstellungsübergang vom Pulver
zum Auszug wurde identifiziert. Eine weitere bloße Übereinstimmungszählung an
denselben Zeugen wäre keine neue Forschung; dieser Transfercheck ist abgeschlossen.

## Kontrolle und Nachrechnung

[VALIDATION.json](VALIDATION.json): PASS. Separater Code kontrolliert alle
Rohgruppenpositionen, vollständige Aktionsübernahme, sämtliche früheren Paare
und die genaue Zeugenmenge. 328 Dateien aus W02–W18 bleiben hashgeprüft bytegleich.

```sh
python research_registry/proposals/translation_programs_20260912/work/W19/build.py
python research_registry/proposals/translation_programs_20260912/work/W19/validate.py
```

[SUMMARY.tsv](SUMMARY.tsv) und [TARGETS.tsv](TARGETS.tsv) enthalten alle Kandidaten,
[WITNESSES.tsv](WITNESSES.tsv) alle positiven Paare. Unabhängige Bestätigungskapazität
jedes Kandidaten 0, keine Suchgegenkontrolle, Signifikanz oder bestätigten Bedeutungen.
Keine neue Quelle, Seite, Bildöffnung oder Kontakte; f84/f84r und übrige Reserven
bleiben geschlossen. Globale alte GDT600-/Indexprobleme liegen außerhalb dieses
lokalen Versuchs. Kein weiterer Experimentvertrag wurde ausgewählt.
