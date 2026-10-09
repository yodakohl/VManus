# GDT1202 — zwei Schreibweisen pro ganzem Quellwort reichen hier nicht

**WHOLE_WORD_TWO_ALIAS_CAPACITY_EXCLUDED.** In allen vier vorhandenen
Vergleichstexten scheitert sogar die günstigste denkbare Verteilung jedes ganzen
Quellwortes auf höchstens zwei Schreibweisen. Es entstehen zu wenige verschiedene
Formen, während die häufigsten zehn Formen zu viel Text beanspruchen. Das schließt
diese Konstruktionsklasse auf den festgelegten Quellen vor jeder Zeichentafel aus.
Es ist ein Quellkontrollbefund, keine allgemeine Aussage über die Sprache des
Voynich-Manuskripts. Die unabhängig implementierte Zähl-/Schrankenprüfung besteht.

## Ergebnis unter großzügigen Bedingungen

Jede Buchprobe enthält die ersten 8.000 unveränderten gespeicherten Quellwörter.
Die Schreibung dürfte für jedes einzelne Wort beliebig günstig auf zwei Formen
verteilt werden; ein menschlich ausführbarer Auswahlmechanismus wird dafür noch
nicht verlangt. Unterschiedliche Quellwörter dürfen für die obere Vielfaltgrenze
sogar sämtliche Formen getrennt halten. Wir prüfen also mehr Freiheit, als der
vorgeschlagene kleine Schreiber mit zwei Anfangsvarianten wahrscheinlich hätte.

| Quelle | verschiedene Quellwörter | davon nur einmal | höchstens verschiedene Ausgaben | mindestens Top10-Anteil |
|---|---:|---:|---:|---:|
| b4 | 1.131 | 577 | 1.685 | 21,1875 % |
| w1 | 1.275 | 704 | 1.846 | 20,1500 % |
| bs1 | 1.105 | 561 | 1.649 | 20,3125 % |
| gr1 | 1.199 | 690 | 1.708 | 23,3375 % |

Schon der unveränderte tolerante gemeinsame Prüfbereich verlangt mindestens
**2.130 Formen** und höchstens **17,6 %** in den häufigsten zehn. Die tatsächlichen
Voynich-Zusammenfassungen liegen enger; die Toleranzen werden nicht als exakte
Manuskriptwerte ausgegeben. Alle Einzelbedingungen der drei Leser scheitern,
nicht nur der strengste gemeinsame Rand:

| bisherige Leserzusammenfassung | beobachtete Formen | zulässige Mindestzahl | beobachteter Top10-Anteil | zulässiger Höchstanteil |
|---|---:|---:|---:|---:|
| IT2a | 2.451 | 2.051 | 13,3125 % | 18,3125 % |
| RF1b | 2.530 | 2.130 | 12,6000 % | 17,6000 % |
| ZL3b | 2.500 | 2.100 | 12,8750 % | 17,8750 % |

ZL/IT/RF sind alternative Transkriptionen, keine unabhängigen Bestätigungen.
Diese Zahlen sind die schon vorhandenen GDT1174-Acht-Tausender-Zusammenfassungen,
keine neue Zählung des ganzen Manuskripts. Es wurde kein neuer Zieltext geöffnet.

## Warum eine andere Zeichentafel daran nichts ändert

Ein Quellwort, das nur einmal vorkommt, kann auch mit zwei erlaubten Schreibweisen
in dieser Probe nur eine davon liefern. Ein häufigeres Wort kann höchstens zwei
verschiedene Formen liefern. Deshalb gilt genau:

```
maximale Formen = 2 × Zahl der Quellworttypen − Zahl der Einmalvorkommen
```

Für die günstigste Konzentration wird jede Worthäufigkeit möglichst gleichmäßig
geteilt. Bei 733 Vorkommen wären das beispielsweise 367 und 366. Ein ungleicherer
Split kann die Summe der zehn größten Häufigkeiten nicht senken. Das Beispiel
733 betrifft ausschließlich das Quellwort vnd in b4; es ist keine Zuordnung zu
einem Voynichwort. Das vollständig ausgegebene Frequenzkonto enthält alle Wörter,
nicht nur diese häufige Form.

Auch wenn sich verschiedene Quellwörter später dieselbe schriftliche Form teilen,
kann dies nur die Vielfalt verringern und die Spitzenkonzentration erhalten oder
erhöhen. Länge, Zeichenwahl und ein komplizierterer Verteiler innerhalb der Grenze
von zwei Ganzwortschreibungen beheben den Widerspruch deshalb nicht.

Die Formel ist eine obere/untere notwendige Grenze. Ein Bestehen hätte keinen
fertigen Schreiber oder ein gleichzeitiges Treffen aller statistischen Intervalle
bewiesen. Hier scheitern jedoch beide notwendigen Richtungen in jedem Buch für
jeden Leser. Keine Optimierung, Verschlüsselung oder zusätzliche Variante lief.

## Reichweite und wichtige Quellannahme

Wort bedeutet hier exakt ein gespeicherter Token der festgelegten CoReMA-
Editionsprojektion. Großschreibung, seltene Zeichen und Interpunktion bleiben
unverändert. Auch ein allein gespeicherter Punkt bleibt eine eigene Quellgruppe;
in bs1 gehört er zu den häufigen Gruppen. Das ist nicht automatisch die Wort-
oder Zeichensetzung eines mittelalterlichen Schreibers. Die Bedingung lautet:
**ein gespeicherter Quelltoken wird genau eine sichtbare Ausgabegruppe**.
Satzzeichen an Nachbargruppen zu hängen würde diese Bedingung ändern und wird
hier nicht nach dem Ergebnis als Reparatur ausgeführt.

Die Aussage gilt für die vier exponierten Vergleichsprojekte und diese
Gruppierungsregel. Sie widerlegt weder jede andere Ausgangssprache noch eine
konstruierte Fachsprache, bedeutungstragende Endungen, mehrere Quellwörter pro
Schriftgruppe oder sinnvolles Voynich. Sie identifiziert auch keine Quellsprache.
Die auf zwei begrenzten Alternativen sind ganze Wortschreibungen. Zwei Varianten
PRO BUCHSTABE können wesentlich mehr als zwei Formen desselben Wortes ergeben;
1197/IDEA938 werden durch diesen Versuch nicht als getestet oder widerlegt erklärt.

## Vorgänger und Konsequenz

1180V2-flat/V2-edge sind konkrete ausgeführte Unterfälle mit höchstens zwei
Schreibungen pro Quellwort. Ihr alter negativer Gesamttest allein war noch kein
Ausschluss aller anderen Tafeln.1202liefert jetzt einen notwendigen Ausschluss
unabhängig von der Zeichentafel für die festgelegten ganzen Quellwörter.
Die bereits gescheiterten Tafeln wurden nicht neu ausgeführt oder repariert.
1196s ähnliche Mathematik betraf dagegen Vokalfragmente mit E/C-Markierung und
andere erste8.000Gruppen; die damaligen Zahlen werden nicht als Ganzwortzahlen
umgedeutet.1002war ein anderes natives Alias-Bedeutungsproblem.1200s Formenreihen
und1201s transparente Gruppierung bleiben als begrenzte positive Ergebnisse.

**Entscheidung:** Für diese Quellen keinen Zweivarianten-Ganzwortschreiber mehr
bauen oder sein Alphabet optimieren. Keine automatische dritte/vierte Variante
anhängen. Vor einem neuen Entwurf muss sich die Verteilung von Inhalt auf
Schriftgruppen begründet ändern oder eine andere feste Annahme mit eigenem
Falsifikationskriterium gewählt werden. Das ist eine Auswahlaufgabe, noch kein
neuer fertiger Kandidat. Die naheliegenden alten Listen-/Kurzwortbindungen wurden
bereits in1175–1178 bearbeitet; sie dürfen nicht als unversuchte Fortsetzung
wiederkehren. Neuer Umfang und Lernaufwand müssten zuerst ausdrücklich das alte
Scheitern sowie dal/daly/daldy/daldaldy und die bekannten Ganzformreste berücksichtigen.

## Reproduzierbarkeit und Prüfung

Vertrag und Eingaben wurden am5.Oktober2026 um12:56:29UTC lokal vor dem Zähllauf
gebunden. Vorbereitung begann12:52:35UTC. SOURCE_RECEIPT nennt Quell-/Zielhashes,
alle beteiligten Rezept-/Wortpositionen und Stichprobenhashes. FREQUENCIES enthält
jede wörtliche Quelleinheit, ihre Häufigkeit und beide optimalen Häufigkeitszellen.
Die vier Gesamtquellen haben1.054Rezepte/80.931gespeicherte Wörter; diese wurden
hier nur inventarisiert, nicht als1.054neue Encoder-Rücklesungen gewertet.

Der separat geschriebene Validator importiert den Runner nicht. Er zählt über
Rezept-/Wortpositionen, verteilt einzelne Vorkommen abwechselnd auf zwei Zellen
und rekonstruiert alle Buch-/Lesergrenzen.8.100kleine erschöpfende Teilungsfälle
und1.536Zusammenführungsfälle prüfen die verwendete Schranke. PASS betrifft
Quelle, Zählung und Mathematik; gleicher Autor, kein unabhängiger Manuskripttest.
Alle24Buch/Leser/Richtungsbedingungen sind negativ. Prüfzahlen sind kein
Entzifferungsfortschritt.

Keine neue Quelle, Reserve, f84/f84r/f116v, Bildprüfung oder semantische Relation;
kein Wort übersetzt. Lokaler Konstruktionscheckpoint gemäß Live-Route, kein
Commit/Push und kein laufender Folgeversuch. Abschlusszeit im vorhandenen Dossier.
