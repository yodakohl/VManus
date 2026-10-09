# GDT1174 — lokaler Konstruktionsvergleich vor der Auswertung

Explorativer Auftrag des Nutzers vom 5. Oktober 2026: zehn verschiedene,
sinntragende und mit der Feder ausführbare Systeme innerhalb des vorhandenen
Zeichenrepertoires entwerfen. Keine konkrete Voynich-Wortbedeutung wird benutzt.
Die zehn Systeme und ihre Programme werden vor der neuen Statistikberechnung
lokal gehasht. Das ist keine öffentliche oder verblindete Präregistrierung.
Die alten Texte, ihre Struktur und zahlreiche Einzelbefunde sind bekannt.

Jedes System erhält dieselben 256 künstlichen Einträge mit je 20 vollständigen
Arbeitsaufzeichnungen. Der Inhalt ist ein explizites Tupel aus Tätigkeit,
Pflanze, Teil, Zustand, Zusatz, Menge und Dauer. Es sind erfundene Notizen über
Proben und Tätigkeiten, keine historische Quelle und keine behauptete Lesung.
Jeder Auftrag betrifft eine eigene Portion. Eine wiederholte Benennung legt
keine Identität der Portion fest. Die aufgeschriebene Nachricht muss exakt
zurückgewonnen werden, einschließlich aller fünf gepackten Felder. Definitionen,
Kontrollwörter und Referenzen zählen zur Textmenge.

Das gemeinsame Inventar hat 22 als EVA-Referenznamen bezeichnete Formen:
`a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh`.
Mehrzeichen-Namen wie ch bezeichnen hier eine Form. Dies ist eine feste
Vergleichssegmentierung, keine neue Identifizierung des wirklichen Alphabets.
Alle erzeugten Zeichen müssen daraus stammen. Ein Entwurf muss nicht jedes
Zeichen in dieser endlichen Demonstration verwenden; fehlende Häufigkeiten
gehen jedoch in den Verteilungsvergleich ein. Unklare Originalformen werden
vollständig als Auslassungen gezählt, nicht nachträglich normalisiert.

Die zehn vollständigen Verfahren sind in src/scribes.py vorgegeben: Silbenlexik,
Rollenaffixe, innere Rollenmarkierung, Begriffshierarchie, feste Fachkürzel plus
offene numerische Silbenschreibung, feste Satzstellen, explizite Rückverweise,
Änderungsprotokoll, Postfix-Operatoren, Materialdefinition mit späteren Aufrufen.
Die 4096 Materialmöglichkeiten werden aus 64 Pflanzen, acht Teilen und acht
Zuständen gebildet. Die Werte sind unsere Beispielnotation, keine aus Voynich
gelernten Glossen. Ein neuer Begriff außerhalb dieses Bereichs ist in diesen
endlichen Prototypen noch nicht spezifiziert. Deshalb kein Anspruch einer
vollständigen Sprache für jedes mögliche Manuskriptthema.

Physische Zeilen werden nach höchstens 48 Inventarzeichen, ohne Worttrennung,
umbrochen. Leerzeilen begrenzen Einträge und setzen deklarierte Speicher zurück.
Der Decoder bekommt nur die sichtbare Ausgabe samt Absätzen; logische
Datensatzgrenzen müssen aus fester Stelligkeit oder ausgeschriebenem Abschluss
wiederhergestellt werden. Zeilenumbrüche liefern keine geheimen Satzgrenzen.

Ziel ist ausschließlich der bereits selektorbewachte GDT1170-Cache mit
179 zugelassenen Selektoren, SHA-256
ccff1909c3dbca720b28f11711278853e3befa99e6f444a0335249d6d6db01be.
Keine rohe gemischte TSV, neue Abbildung, neue Quelle oder Reserve. f84 und
f84r bleiben versiegelt, f116v ausgeschlossen. Nur P-Gruppen mit beidseitig
sicherem Abstand bzw. Zeilenrand und vollständiger Inventarzerlegung werden
verwendet. Jede Auslassung und der vollständige Nenner werden ausgewiesen.
Alternative Leser werden getrennt berechnet, nie als unabhängige Replikate.

Vergleich je 8000 Wörter: synthetische Ausgabe in fester Reihenfolge; Original
in vorab mit Seed1174 permutierter Seitenreihenfolge, innerhalb jeder Seite
stabile Locus-Reihenfolge. Ganze Zeilen/Nachbargrenzen bleiben erhalten. Eine
Abschneidung am Ende wird angegeben. Nachbarschaft zählt nicht über Zeilen
oder ausgeschlossene Gruppen hinweg. Die Auswahl ist keine neue Bestätigung.

Zehn vorab festgelegte grobe Ähnlichkeitsgrenzen: mittlere Wortlänge ±20%,
Längenstreuung ±25%, Top10-Anteil ±5 Prozentpunkte, Typanteil ±5 Punkte,
bedingte Zeichenentropie ±0,30 Bit, exakte direkte Doppelung ±1 Punkt,
direkte Ein-Zeichen-Ähnlichkeit ±3 Punkte, Anfang/Ende-JS ±0,12 Bit,
Längenverteilung-TV höchstens0,20 und Zeichenverteilung-JS höchstens0,10 Bit.
Dies sind transparente Konstruktionsgrenzen, keine inferentiellen Tests oder
historisch begründeten Naturkonstanten. Gezählt werden alle zehn Grenzen;
ein Gesamtbestehen verlangt alle zehn bei allen drei Lesern. Kein neuer
Schlüssel, keine geänderte Verteilung, keine Reparatur nach Betrachtung der
Ergebnisse. Eine bloße Zahl bestandener Grenzen wählt keine Übersetzung.

Auch ein Gesamtbestehen wäre nur ein erster Filter. Die stärkeren Befunde aus
GDT608,289,915/916,1073/1077 zu Resten, Positionen und Übertragung sind damit
noch nicht reproduziert. Kein Modell erhält deshalb die Bezeichnung
"erklärt Voynich". Ein Scheitern betrifft die konkrete Konstruktion mit dieser
Inhaltsquelle, nicht die gesamte Familie. Alte Fehlschläge bleiben unverändert.

Gesamtbudget90Minuten inklusive Vorbereitung und Dokumentation; keine
automatische Modellreparatur. Ergebnis ist zunächst ein lokaler, vollständig
nachvollziehbarer Konstruktionscheckpoint, kein neuer Inhaltsbefund.
