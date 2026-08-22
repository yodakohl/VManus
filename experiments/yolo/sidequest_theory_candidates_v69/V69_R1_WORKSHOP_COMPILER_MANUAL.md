# V69 R1 — ausgewähltes Werkstatt-Compilerhandbuch

Status: letzte kreative Zehnseitenedition. Dieses Handbuch beschreibt eine lehrbare Produktion, keine Sprache, Lautung oder Entzifferung.

## Die fünf getrennten Ebenen

1. **Exakte Identität:** Prosa-joint_tuple_id oder lokale Astro-Adresse; niemals aus sichtbaren Teilen zusammensetzen.
2. **Formale Kontrolle:** nur `VORGABEPARAMETER?`, `STANDARDSLOT_SETZEN`, `LOKALEN_RELATIONSSLOT_SETZEN`, `AKTIVEN_ARBEITSSTAND_VERKNÜPFEN` an ihren ausgewählten Ereignissen.
3. **Ganzkarten-Mnemonic:** nur `MASS?`, `ANWENDEN?`, `BEREIT?`, `ANSATZ?`, `ZIEL?`, `KLAR?`, `VORIGES?`, `ANTEIL?`, `TEMPERIEREN?`, `SPÜLEN?`, `ABLASSEN?` an elf exakten IDs.
4. **Lokale Quellenexpansion:** zwei gleichrangige Exemplare — `SIMPLE/BATH/ELECTION` und `MATERIAL/PROCESS/SCHEDULE`.
5. **Volltext:** der vollständige Record oder das vollständige Diagramm; niemals Wörterbuchquelle.

Alle übrigen 159 Prosa-Karten sind `UNKNOWN_EXEMPLAR`. Ein formaler Feldschluss ist kein gesprochenes Wort und ergänzt kein Objekt.

## Werkstattausstattung

- **Common Ledger:** 173 exakte Prosa-IDs; 14 davon tragen mindestens einen Control-Kanal.
- **Mnemonic-Blatt:** elf fragezeichenmarkierte Lehrgriffe.
- **Formblatt:** vier formale Controls, V61-Aussagen, V62-Register und V63-Status.
- **Doppeltes Masterexemplar:** medizinisch und praktisch; beide gleichrangig.
- **Drei Astro-Seitenbücher:** f67r2, f68r1 und f69v bleiben getrennte Namespaces.
- **Kopierblatt:** Oberfläche, Feld, Close, Zeilenfit und Korrekturzeichen.

Fünf Funktionen — Lehrmeister, Bild-/Rissmeister, Exemplarhüter, Renderer und Korrektor — dürfen in einer kleinen Werkstatt auf drei Personen verteilt werden. Die Funktionstrennung bleibt trotzdem sichtbar.

## Encoder

1. Bestimme Seite, Register und Record/Diagramm. Öffne niemals ein anderes Seitennamespace.
2. Setze den Bildbesitzer nur als stillen OWNER beziehungsweise den Diagrammmittelpunkt als lokale Adresse.
3. Wähle **eine** der beiden Quelleneditionen für den aktuellen Kopierauftrag. Vermische sie nicht innerhalb eines Records.
4. Ordne Herbal als Besitzer → Teil → Bearbeitung → Parameter/Zustand → Gebrauch → Fortsetzung; Bio als Station → ACTIVE → Parameter/Link/TARGET → Zustand → Transfer → Schluss; Astro als Namespace → Adresse → lokaler Wert.
5. Gliedere Prosa nach den 116 ausgewählten Aussagen. Physische Zeilen sind erst späterer Reflow.
6. Führe OWNER, ACTIVE, TARGET und PREVIOUS als anonyme recordlokale IDs. Setze alle vier am Recordwechsel zurück.
7. Nutze einen Formalcontrol oder ein Mnemonic nur, wenn Ereignis und exakte ID im Release-Ledger lizenziert sind. Sonst kopiere `UNKNOWN_EXEMPLAR` aus dem lokalen Masterexemplar.
8. Bewahre die exakte Kartenfolge jedes Feldes. UNIQUE darf ausgeführt, AMBIGUOUS mit offener Alternative vermerkt, UNPARSED/EXEMPLAR_ONLY nicht nachträglich geparst werden.
9. Übergib die Folge dem Renderer. Er darf ausgewählte Hülle, JOIN/SPACE, Feldschluss und Bildraum-Umbruch ausführen, aber keine Identität und keinen Quelleninhalt ändern.
10. Der Korrektor vergleicht ID, Oberfläche, Feld, Statement, Registerübergang und Exemplarspalte; erst danach wird der Record freigegeben.

## Rückleser

1. Lies Namespace, Unit, locus und Feld/Adresse vor der sichtbaren Form.
2. Schlage die exakte Ganzkarte nach; ignoriere PAGE_HOST, Teilstrings und ähnliche Oberflächen.
3. Gib Formalcontrol und Mnemonic getrennt aus. Das Fragezeichen bleibt Bestandteil jedes Mnemonics.
4. Aktualisiere die vier Register aus dem vollständigen Übergangslog, nicht nur aus dem Endzustand.
5. Reflowe nach statement_id. Ein Zeilenende beendet keine Aussage; ein Close commitet nur das Feld.
6. Wähle für die konkrete Lesung entweder die medizinische oder die praktische lokale Spalte. Beide benötigen das Masterexemplar.
7. Bei fehlendem Exemplar lautet die Ausgabe `UNKNOWN_EXEMPLAR`, niemals eine Vermutung aus der Oberfläche.
8. Bei Astro lies ausschließlich die lokale Seitenadresse. Importiere weder GDT327-Prosa noch Kartenmnemonics.
9. Verbinde f68r1 und f69v nicht; Start und Richtung bleiben exemplarisch/editorisch.

## Korrekturregeln

- Zerlegte Ganzkarte → genaue ID neu kopieren.
- Mnemonic als Übersetzung → auf Lehrprompt mit Fragezeichen zurücksetzen.
- Lokales Nomen im Wörterbuch → entfernen und ins Recordexemplar verschieben.
- Zeile als Satz → V61-Statementfolge wiederherstellen.
- Close als Handlung/Objekt → nur Feldcommit behalten.
- Registerwert über Recordgrenze → alle vier Register resetten.
- Praktische und medizinische Prosa vermischt → Record aus einer einzigen gewählten Spalte neu setzen.
- Astro-Prosaimport oder A2↔A3-Join → lokalen Seitenschlag wiederherstellen.
- UNKNOWN erraten → genaue Karte behalten und `UNKNOWN_EXEMPLAR` schreiben.

## Meisterregel

> Erst Namespace und Quelle, dann Aussage und Register, dann Formalcontrol oder exakte Ganzkarte, zuletzt Renderer und Close; rückwärts in genau umgekehrter Ordnung. Der Inhalt kommt aus dem Exemplar, nie aus sichtbaren Kartenteilen.
