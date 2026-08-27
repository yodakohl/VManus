# GDT548 — die 145 Prosaformen haben jetzt einen gemeinsamen Reader

Status: `PASS_ONE_EXACT_KEY_READER_FOR_145_PROSE_SURFACES__23_NAMED_DEFAULTS`

## Ergebnis

Die bisher auf vier Experimente verteilte Arbeitsübersetzung ist jetzt eine
einzige ausführbare Ausgabe. Für jede der 145 bekannten Prosaoberflächen gibt
der Reader gemeinsam aus:

- die unveränderte Komponentenfolge;
- eine vollständige neutrale Defaultbedeutung;
- die vollständige Lesung im bekannten Satzkontext;
- sichtbare Handlung und sichtbares Argument;
- die Regel für ein aus demselben Satz übernommenes Handlung-/Argumentpaar;
- die konkrete Stützroute und ihren verbleibenden Vorbehalt.

Keine Sequenz fällt dabei auf ein bedeutungsloses Etikett zurück. Zugleich
bleiben die vier wirklich verschiedenen Stützarten erkennbar: elf vollständige
alte Rezeptträger, 29 Kompositionen aus vollständigen alten Kacheln, 81
Fragment-Ausbaukarten und 24 Atom/Faktor-Karten.

## Der praktische Leser

`src/read_prose.py` akzeptiert nur einen exakten bekannten Schlüssel. Optional
kann man die laufende Handlung und das laufende Argument desselben Satzes
angeben:

```bash
python3 experiments/yolo/gdt548_unified_145_prose_reader/src/read_prose.py \
  --surface dalol --active-action CH --active-argument Y
```

Für `dalol=AL+OL` wird dann aus dem neutralen „Am Zielort; fortsetzen“ die
bekannte kontextuelle Arbeitslesung „Im laufenden Satz ordne den laufenden
Eintrag [wie zuvor] zu; zur Zielspalte; führe fort.“ Ohne laufende Handlung
bleibt die neutrale Bedeutung trotzdem sichtbar; der Reader behauptet nur
keine bereits aufgelöste verbale Satzlesung.

Ein unbekannter Schlüssel stoppt mit `STOP_UNKNOWN_145_PROSE_SURFACE` und
erbt keine ähnlich geschriebene Karte.

## Die kleine echte Restmenge

Der gemeinsame Vertrag macht die schwächsten Stellen erstmals in einer
einzigen Liste sichtbar. Es sind genau 23 Karten:

- zehn vollständige Kachelkompositionen, deren Kacheln und Nähte alt sind,
  aber ohne vollständiges altes Gerüst oder geordneten Satzpfad;
- zwölf Fragmentkarten mit dem bereits benannten Kontext- oder Kantenrest;
- `shso`, dessen `SH>S` der einzige rohe neue direkte Aktionsübergang ist.

Die übrigen 122 Karten bleiben keineswegs „bewiesen“; sie brauchen aber nicht
bei jeder Runde erneut aufgerissen zu werden. Die nächste Verbesserung kann
gezielt die 23er-Liste nach gemeinsamen fehlenden Bausteinen bündeln.

Alle 34 Prüfungen bestehen, einschließlich Quell-Replay jeder Stufe,
vollständiger Bedeutungsfelder, vier CLI-Stufenproben, Kontextumschalter,
Unknown-Stop und byteidentischem Neulauf. Keine Seite, Oberfläche, Rezeptkarte
oder Wurzelbedeutung wurde verändert. Die deutschen Sätze bleiben die beste
aktuelle Arbeitsübersetzung, kein behaupteter Klartext.
