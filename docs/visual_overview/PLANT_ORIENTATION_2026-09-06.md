# Sechs Pflanzenblätter persönlich am Original betrachtet

6.September2026. NATIVE_ORIENTATION_WITH_KNOWN_ANNOTATION_POINTER.
Root hat alle sechs ausgewählten Originalaufnahmen selbst nativ betrachtet:
f4r, f10r, f13r, f17r, f18r, f20v. Ganze fotografierte Ansichten, keine
OCR, Ausschnitte, Bildverbesserung oder automatische Klassifikation. Die
Auswahl und Grenzen standen vor dem Bildabruf im zugehörigen PLAN; alle sechs
Schlüssel waren bereits in GDT791 zugelassen. Quellen, Maße und Hashes stehen
in PLANT_ORIENTATION_2026-09-06_SOURCES.json.

## Unmittelbare Beobachtungen

| Aufnahme | Was ich im Original sehe |
|---|---|
| f4r /1006082 | Eine hohe, fein verzweigte Pflanze mit vielen schmalen roten und grünen Flächen sowie unbemalten kapselähnlichen Endformen. Schrift steht überwiegend oben und links; einige Zeilen lassen die oberen Verzweigungen frei. Nahe der Wurzel stehen kleine getrennte dunkle, zeichenartige Marken entlang der Pflanzenachse. Größere blasse Farbspuren liegen im Hintergrund; deren Entstehung wird nicht bestimmt. |
| f10r /1006094 | Eine große seitliche blaue Blütenform an einer gekrümmten oberen Achse, darunter verschieden breite Blattgestalten. Manche schmaleren Blattformen wirken umgeschlagen: braune und grüne Partien sind durch helle Bänder getrennt. Unten erstreckt sich eine braune Wurzelachse zu roten ovalen Endkörpern. Der Text verteilt sich links und teilweise innerhalb des oberen Bogens. |
| f13r /1006098 | Eine zentrale Ansammlung schmaler, teils blauer oder blasser Formen mit kleinen hellen punktierten Köpfen. Breite grüne Blätter besitzen teils braune umgeschlagen wirkende Randpartien. Oberhalb der großen roten Wurzel liegen röhrenähnliche Ansätze mit gezeichneten ovalen Endflächen. Der obere Schriftblock lässt Raum um die Spitze der Pflanze. |
| f17r /1006106 | Eine schlanke Pflanze mit langen schmalen grünen Blättern und großen dunklen blauen Blütenformen oben und seitlich. Die Schrift liegt in mehreren abgesetzten Bereichen um die Blüten; am oberen Rand steht eine viel kleinere, blasse Notiz. Innerhalb der feinen Wurzellinien fallen rote langgezogene Umrisse auf. Der bekannte otchol/chol-Befund wird nicht erneut gelesen oder getestet. |
| f18r /1006108 | Eine hohe grüne Pflanze mit breiten ovalen unteren Blättern und stärker gegliederten oberen Formen. Der große blaue Blütenkopf besitzt eine rote, kleinteilig gemusterte Mitte; kleinere Endformen tragen rote Spitzen. Schrift steht überwiegend links, einige kurze Zeilen rechts des Blütenkopfs. Links oben beginnt der Text mit einer auffällig verlängerten hohen Form. |
| f20v /1006113 | Eine verzweigte Pflanze mit langen schmalen grünen Blattformen und vielen spitz umzeichneten, blau gefüllten Endformen. Die Endformen sind unterschiedlich orientiert; eine hängt nach unten. Der obere Textblock wird rechts durch Zeichnungsteile begrenzt. Die Wurzeldarstellung liegt am unteren Bildrand; die vollständige Fotografie zeigt nicht automatisch jedes botanische Detail vollständig. |

„Blüte“, „Wurzel“, „Kapsel“, „Röhre“ und „umgeschlagen“ beschreiben sichtbare
Ähnlichkeit beziehungsweise meinen Eindruck. Keine Artbestimmung, historischen
Objektnamen oder verifizierten biologischen Eigenschaften. Insbesondere wurden
keine neuen LM-Blattkantenwerte, Zählvariablen oder Text-Bild-Zuordnungen vergeben.

## Konkreter Quellenanschluss: die kleinen f4r-Marken

Ich notierte die kleinen axialen Marken zunächst ohne Wortlesung. Anschließend
suchte der Ideenagent ausschließlich in internen Berichten nach diesem Ort.
Der Primärbericht
`experiments/semantic_assumptions/results/col001_plain_colour_annotation_capacity_report.md`
führt bereits f4r mit der menschlichen Lesung **rot**, senkrecht im
Pflanzenstängel, als Notiz in gewöhnlichem Alphabet auf. Root hat diesen
Primärbericht danach gelesen. Das passt räumlich zur Beobachtung; ein neuer
unabhängiger paläographischer Beweis der exakten Zeichenlesung wird nicht behauptet.

Das ist somit ein wiedergefundener bekannter Quellenanker. Die deutsche
Farbnotiz ist keine neu entschlüsselte Voynich-Zeichenfolge. Sie bestimmt
weder die Sprache des Haupttexts noch die Hand des Schreibers oder die
zeitliche Reihenfolge der Farbarbeit. COL001 hält diese Grenzen bereits fest.
Sein einziger Voynichschrift-Kandidat im Farbkontext reicht nicht für eine
replizierte Farbzuordnung; diese Kapazitätsgrenze wird nicht wieder geöffnet.
Keine Suche nach gemeinsamen Teilstrings in f4r/f7r-Prosa.

## Was dieser Durchgang ändert

Mein visuelles Verständnis umfasst jetzt weitere konkrete Pflanzenaufbauten,
verschiedenfarbige beziehungsweise umgeschlagen wirkende Blattformen und die
räumliche Trennung von Haupttext, Randnotiz und kleinen Marken an einer Achse.
Gerade die f4r-Marken zeigen, warum eine überraschende eigene Beobachtung zuerst
mit der vorhandenen Geschichte abgeglichen werden muss. Sie waren hier kein
neuer Schlüssel. Die übrigen Beschreibungen erhalten keinen Neuigkeitsanspruch.

Die drei persönlichen Orientierungsdurchgänge des Dossiers umfassen zusammen
24Darstellungen aus23Aufnahmen zu24bereits zugelassenen Seitenschlüsseln.
Spezielle andere Bildexperimente sind nicht Teil dieser Dossierzählung.
Der Zulassungsumfang bleibt39Schlüssel/44Selektoren und11weitere Freigaben.
Kein neuer Entzifferungstest wurde aus diesem Durchgang ausgewählt.

Alle sechs nativen Ansichten waren bis06:11UTC betrachtet. Quellenvorbereitung
begann06:06:24UTC; die Dokumentation erfolgt im15-Minuten-Budget bis06:21:24UTC.
Die Quellenprüfung kontrolliert Bytes, Hashes und Maße, nicht Bildinterpretation:

```sh
python3 docs/visual_overview/validate_orientation_sources.py PLANT_ORIENTATION_2026-09-06_SOURCES.json
```
