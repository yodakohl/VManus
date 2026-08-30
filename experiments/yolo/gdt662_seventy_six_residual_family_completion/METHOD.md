# GDT662 — Methode

## Frage

Lassen sich die 76 verschiedenen Restformen in den 78 von GDT661 neu
freigelegten Ein-Loch-Zeilen so konkret lesen, dass alle 861 geerbten
Vorkommen geschlossen werden und dabei eine vorhersagbare Mischung aus
Fachkomposita, kurzen Rezeptzeichen und gelernten Ganzwörtern entsteht?

## Eingaben

- GDT661 V38-Wörterbuch, Glossar, vollständige Zeilen, Ein-Loch-Zeilen,
  Vorkommensaudit und die 78 neu exponierten Frontierzeilen;
- dieselbe exakte 179-Seiten-Allowlist wie GDT661;
- die bereits zugelassene, gecachte Tokenquelle und der Drei-Leser-Vergleich,
  beide ausschließlich über den bewachten Abfrageweg;
- die geerbten GDT660/GDT661-Renderer, damit bereits gelöste Token an exakt
  derselben Position unverändert bleiben.

`f1r`, `f84` und `f84r` sind ausgeschlossen. Es werden keine neue Seite, kein
Bild und keine OCR-Ausgabe geöffnet.

## Vorgehen

1. Die 78 Frontierzeilen liefern in ihrer ersten Auftretensreihenfolge genau
   76 Zieloberflächen. Ihre 861 Vorkommen werden in allen 4.128 zugelassenen
   physischen Zeilen gezählt.
2. Drei unabhängige Leser bearbeiten dieselbe Front aus verschiedenen
   Blickwinkeln: praktische Rezeptkohärenz, spätmittelalterliche
   Schreiber-/Apothekerpraxis und Kurzform-/Kompositionsfamilien. Die
   Alternativen müssen konkrete Stoffe, Maße, Zustände oder Handlungen nennen;
   generische Arbeitswörter sind ausgeschlossen.
3. Das gemeinsame Modell trennt vier Kartentypen:
   `PRODUCTIVE_COMPOUND`, `LEARNED_FUNCTION_WORD`, `LEARNED_WHOLE` und
   `HYBRID_EXACT`. Auch eine kompositionell erklärte Form wird nur als exaktes
   whitespace-getrenntes Ganzwort eingesetzt. Eine Zerlegung allein darf kein
   anderes Token übersetzen.
4. Wörterbuchbedeutung und praktische deutsche Wiedergabe bleiben getrennt.
   So kann `oly` als Arbeitskarte „abseihen“ am Zeilenende „seihe ab“ ergeben,
   während die sichtbare Konkurrenz „Drogenmaterial in Grundform“ in der Karte
   erhalten bleibt. Positionsmarker verhindern globale String-Ersetzungen bei
   Wiederholungen desselben Wortes.
5. Alle 861 Zielpositionen ersetzen exakt den vorherigen `[surface:?]`-Slot.
   Glosse, Quelle und Scope jeder Nichtzielposition müssen bytegleich bleiben.
6. Danach werden V39-Abdeckung, vollständige Mehrwortzeilen, Ein-Loch-Zeilen,
   praktische Übersetzungen, Leserstatus, Familienatlas und die nächste Front
   neu erzeugt.
7. Ein unabhängiger Validator rekonstruiert Zielmenge, Kartentypen,
   Positionsrenderer und V38→V39-Arithmetik ohne Import des Builders und
   vergleicht einen vollständigen Tempdir-Replay byteweise.

## Auswahlregel und Aussagegrenze

Eine konkrete Defaultkarte darf explorativ bestehen bleiben, bis eine
Schwesterform oder Passage sie unmöglich macht oder eine praktisch bessere
Lesung mehr Kontexte zugleich erklärt. Für konkurrierende Lesungen wird der
stärkste Rivale ausdrücklich gespeichert. Kurze Handlungslesungen werden nur
als exakte Ganzwörter verwendet: freies `qo = nimm` macht gebundenes `qo-`
nicht automatisch zu einem Verb; `qokol = erhitze` ändert daher auch nicht die
geerbte Karte `qotol = kaltes Material`.

Das Ergebnis ist eine konkrete Arbeitsübersetzung, keine bestätigte
Entzifferung. Es behauptet keine Sprache, Phonetik, freie Glyphenwerte, exakte
Pflanze, Krankheit oder historische Vorlage. Historische Rezeptbücher
motivieren nur die Architektur aus Kürzeln, Maßen, Stoffnamen und
Herstellungsangaben; sie identifizieren kein Voynich-Zeichen.
