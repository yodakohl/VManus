# GDT1283 — f77r erlaubt hier keinen belastbaren Vergleich der Restbreite

**NO_BOUND_GEOMETRY_FOR_GREEDY_TEST.** Bei einer informierten Betrachtung des
bereits zugelassenen Bildes konnte ich weder die beabsichtigte rechte Schreibgrenze
noch die nötigen Anfügebreiten unabhängig bestimmen. Deshalb wurde kein
numerischer Breitentest ausgeführt. Keine der beiden Erklärungen wurde ausgewählt:
Anfangsschreibung mit zusätzlichem `d` oder unveränderte Formen bei anderer
Zeilenaufteilung.

## Konkrete Stelle und Beobachtung

Die gespeicherten Transkriptionen beginnen f77r.32 übereinstimmend mit
`qor ain cheol`. ZL und IT ordnen diese Zeile dem bei .25 beginnenden Absatz zu.
Die passende RF-Wortfolge liefert keine unabhängige Absatzgrenze.

Verwendet wurde ausschließlich das vorhandene [Bild aus GDT930](../gdt930_label_text_joint_reading/artifacts/f77r.jpg),
2000 × 2687 Pixel, SHA-256
`6bcedcaccc8107da32d6d1ca950b96708b529538d7902a2108398a3c0b9327df`.
Das ist die vorhandene Bildversion, keine neue Aufnahme in höherer Auflösung.

Der mittlere Textblock neben der mittleren Figur lässt sich regional zuordnen.
Es wurden jedoch keine unabhängig geprüften Pixelgrenzen der einzelnen Zielwörter
festgelegt. Die Zeilenanfänge sind neben der Zeichnung versetzt. Rechts enden die
Zeilen unterschiedlich weit; dahinter bleibt Pergament frei. Sichtbare Blatt- und
Falzkanten legen für diesen Test nicht automatisch die beabsichtigte Schreibgrenze
von Zeile .31 fest. Eine eindeutige Linierung, Feldgrenze oder ein Hindernis als
solche Grenze habe ich nicht identifiziert.

Auch die hypothetische Anfügebreite von `qor` beziehungsweise `qor ain` auf der
vorigen Zeile bleibt ungebunden: Zwischenräume und mögliche Veränderungen der
Schreibbreite dürfen nicht einfach aus der nächsten Zeile übernommen werden.
Daraus folgt nicht, dass der Schreiber keine Ränder oder Abstandsregeln hatte.

| Vorher festgelegte Voraussetzung | Ergebnis |
|---|---|
| Regionale Zuordnung der Stelle | vorhanden; keine Wort-Pixelgrenzen |
| Unabhängig bestimmte rechte Schreibgrenze | ungeklärt |
| Festgelegte Anfügebreiten, Abstände und Skalierung | ungeklärt |
| Numerischer Vergleich | nicht ausgeführt |

## Was der Vergleich leisten müsste

Sei H die unveränderte Gruppe vor einer kurzen Minimform B. Zwei **festgelegte,
möglichst raumausnutzende** Umbruchregeln unterscheiden sich an einem Umbruch vor H
nur dann eindeutig, wenn H noch in den freien Rest R passt, H zusammen mit B aber
nicht: `F(H) ≤ R < F(HB)`.

Ist R kleiner als F(H), brechen beide Regeln um. Ist R mindestens F(HB), widerspricht
der beobachtete Umbruch dieser strikten Raumausnutzungsregel. Die bloße Vorschrift
„kein Umbruch vor B“ fordert dagegen noch keine maximale Raumausnutzung.
Zeichen- oder Gruppenzahlen ersetzen die nötigen Breiten nicht.

GDT1149s Anfangsvermeidung bleibt bestehen. GDT1150s fehlende exakte Gegenstellen
wurden nicht neu gezählt oder durch kürzere Kontexte ersetzt. IDEA882 enthält den
Umbruchrivalen bereits; IDEA200 und GDT1056 hatten die fehlende physische Restbreite
ausdrücklich als Grenze benannt. Hier wurde diese Voraussetzung erstmals für die
festgelegte Stelle im Bild geprüft.

## Umfang, Kontrolle und Entscheidung

Die Wahl der Stelle war explorativ und nicht Teil eines vollständigen Seitenzensus.
Protokoll, Bild und Zieltranskriptionen wurden vor dieser Betrachtung gebunden.
Ein Beobachter kannte die Formen und Hypothesen. Es gab keinen neuen Bildabruf,
keine Suche nach günstigen Ausschnitten, keine OCR und keine Kontrastbearbeitung.
Die übrige Seite diente der Lokalisierung, nicht neuen Lesungen.

Die Softwareprüfung bestätigt Quelle, Maße, Zielzeilen, Beobachtungsfelder und die
Anwendung der festgelegten Entscheidungsregel. **PASS_ACCOUNTING_ONLY bestätigt
nicht die Richtigkeit des visuellen Urteils.**

Dieser lokale Breitentest bleibt geparkt. Ein nachträglich aus den Zielzeilenenden
geschätzter Rand würde die fehlende unabhängige Voraussetzung nicht ersetzen.
Die Beobachtung widerlegt weder Platzdruck noch Anfangsvarianten oder sprachliche
Abhängigkeiten. Keine Wortbedeutung, neue Seite oder Reserve wurde erschlossen.
Lokaler Abschluss; kein Commit oder Push.
