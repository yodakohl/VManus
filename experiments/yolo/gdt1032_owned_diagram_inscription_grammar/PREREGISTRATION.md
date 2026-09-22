# GDT1032: registrierte native Lesung vorhandener Diagrammbeschriftungen

## Entscheidung vor Bildöffnung

Unbekannt ist nach GDT213/214 nicht die Bildarchitektur, sondern die tatsächliche
sprachliche Gestalt der kurzen Inschriften. Beide Primäraudits sagen ausdrücklich,
dass sie diese weder transkribiert noch übersetzt haben. IDEA57 betrifft gerade
unterschiedliche Argumentstruktur in Beschriftung und Prosa. Bevor eine geratene
Voynich-Bedeutung AND/HOURS anhand ihrer Etikettentauglichkeit gewichtet wird,
sollen dieselben bereits ausgewählten historischen Bilder erstmals auf ihre
sichtbaren Inschriften gelesen werden. Kein Voynichbild und kein Zielcensus.

Auswahlbeginn10:32:06UTC, Gesamtbudget25Minuten einschließlich Vorbereitung,
Transport, eigener visueller Lesung, unabhängiger Sichtung, Prüfung und
Veröffentlichung; Ende10:57:06UTC. Keine neue Kontrollsammlung, kein OCR oder
Decoder, keine zusätzlichen Quellen/Bilder bei Leseschwierigkeiten. Die vier
festen historischen Bilder stehen mit den alten Hashes in src/SOURCE.json.
Ein Transportversuch pro URL,35Sekunden und25MB Grenze, bei Hashabweichung keine
Bildöffnung; kein Ersatz mit ähnlichem Bild oder neuer Auflösung. Originaldateien
werden nur im lokalen temporären Cache gespeichert, nicht veröffentlicht.

## Vollständige Sichtungsregel

Jedes verfügbare feste Bild wird vollständig in nativer Ansicht betrachtet.
Alle räumlich vom längeren Fließtext abgesetzten Inschriften innerhalb oder
unmittelbar an der gezeichneten Anlage werden in Leserichtung über die ganze
Bildfläche erfasst, einschließlich nur eines Zeichens, Wiederholungen und
unlesbarer Einheiten. Textblöcke werden nicht nach erkannter Bedeutung ausgewählt.
Lange durchlaufende Prosaflächen werden ebenfalls als Regionen ausgewiesen,
aber nicht als einzelne Etiketten zerlegt oder vollständig übersetzt. Grenzfälle
bleiben AMBIGUOUS_REGION; Nähe begründet keinen bestimmten Bauteilbesitz.

Pro Region: Bild-ID, ungefähre relative Lage/Box, sichtbare Zeichenfolge soweit
lesbar, Unsicherheiten, Segmentierungsstatus und explizite sprachliche Analyse.
Abkürzung und ihre Expansion getrennt. Codes:
NOMINAL_EXPRESSION, SENTENCE_OR_RELATIONAL_EXPRESSION, SINGLE_SIGN_OR_INDEX,
UNREADABLE, AMBIGUOUS_REGION, CONTINUOUS_PROSE. Ein isolierter arabischer oder
lateinischer Buchstabe erhält keine Wortübersetzung allein aus seiner Form;
zum Beispiel kann eine sprachliche Konjunktionsform zugleich als Index dienen.
Eine beschriftete Figur liefert nicht automatisch die Grammatik ihrer Inschrift.

Root erstellt die regionale Lesung. Ein zweiter Modellagent kann dieselben
vollständigen Bilder unabhängig sichten, ohne Root-Beobachtungen zu sehen.
Beide sind maschinelle native Vision, keine fachkundige Außenprüfung. Widersprüche
bleiben als unsichere Lesung erhalten; keine Mehrheitsabstimmung erzwingt ein Wort.
Der ausführbare Validator prüft Bindungen, Inventar/Status und Abdeckung der vier
festen Bild-IDs, nicht die historische Richtigkeit der Handschriftenlesung.

## Vorher festgelegte Folgen und Grenzen

- Sicher gelesene nominale Beschriftungen erlauben eine ausdrücklich weiche,
  genrespezifische Vergleichserwartung; einzelne funktionale Wörter werden deshalb
  nicht automatisch ausgeschlossen. Bei sehr wenigen/unsicheren Einheiten gibt
  es keine kalibrierte Wahrscheinlichkeits- oder Häufigkeitsaussage.
- Buchstaben-/Indexfälle oder relationale/Satzfälle widerlegen die zusätzliche
  universelle Annahme, jede isolierte Beschriftung müsse eine normale Nominalphrase
  sein. Sie widerlegen weder eine konkrete Voynich-Glosse noch alle Bildlabels.
- Bei fehlender Lesbarkeit oder fehlenden ganzen Inschriften folgt NO_READABLE_
  GRAMMAR_CAPACITY, keine nachträgliche weitere Kontrollquelle.
- Der neue Befund entscheidet, ob der vorbereitete AND/HOURS-Vergleich überhaupt
  einen begründeten weichen Beschriftungshinweis liefern kann oder nur als
  zusätzliche unkalibrierte Genreannahme angeboten werden darf. Erst danach
  separate Registrierung eines möglichen vollständigen Voynich-Inschriftenchecks.

Diese bewusst ausgewählten zwei historischen Objekte sind keine Zufallsstichprobe
und kein Gegenmodell der gesamten Projektsuche. Keine Signifikanzbehauptung,
keine bestätigte Voynich-Bedeutung, kein neuer Bildzugriff auf Manuskriptreserven.
Die alten213/214Quellenbytes, Interpretationen und Grenzen bleiben unverändert.
