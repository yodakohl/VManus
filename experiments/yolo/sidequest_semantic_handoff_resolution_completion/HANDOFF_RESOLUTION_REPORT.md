# Aufgelöste Übergaben zwischen Arbeitszellen

Die vorige Runde zeigte 19 offene Zellen. Diese Runde beantwortet für jede
davon die praktische Frage eines Lehrlings: **Was genau nehme ich in die
nächste Zelle mit?**

## Das Ergebnis

Die Übergaben brauchen drei Registerarten:

| Übergabe | Anzahl | Bedeutung |
|---|---:|---|
| direktes Material | 16 | Auszug, Ansatz, Portion, Wasser-/Badposten oder behandeltes Material |
| benannte Reserve | 2 | ein zurückgelegter Posten bleibt neben dem aktuellen Produkt abrufbar |
| Gerätezustand | 1 | eine geschlossene Öffnung bleibt für den folgenden Spülgang geschlossen |

Damit wird `POSTEN` nicht mehr mechanisch als das letzte sichtbare Wort der
vorigen Zelle gelesen. Die Werkstatt führt vielmehr einen aktiven
Materialgriff, einen kleinen Reservegriff und bei Bedarf die aktuelle
Gerätestellung.

## Drei besonders hilfreiche Reparaturen

### H1: Auszug statt Wurzelrest

H1-S001 sammelt einen Wurzelauszug, stellt ihn nach Sollmaß ein und notiert
zuletzt noch den Wurzelrest als Reserve. Die nächste Zelle wärmt sinnvollerweise
nicht automatisch das letzte genannte Objekt, sondern den aktiven
**bemessenen Wurzelauszug**:

> Setze den bemessenen Wurzelauszug an, wärme ihn an, führe ihn weiter und
> halte ihn bereit.

### H3: Reservegriff neben dem Produkt

H3 legt eine Blütenreserve zurück, bereitet daraus einen Trank und ruft danach
die **restliche Blütenreserve** als Folgeposten wieder auf. Ein einzelnes
„zuletzt erzeugtes Produkt“-Register würde hier versagen; der zusätzliche
Reservegriff erklärt die Folge besser.

### B2: Zustand statt Stoff

B2-S014 schließt den Bodenablauf, aber bestätigt noch keine Arbeitszelle. Der
folgende Schritt übernimmt keinen unsichtbaren Stoff, sondern die
Gerätestellung:

> Halte den Bodenablauf geschlossen, gib Spülwasser zu, setze länger an und
> schließe.

Das ist die einzige der 19 Übergaben, die rein apparativ ist.

## Die vollständigen Ketten

Die übrigen Übergaben ergeben kurze, praktische Folgen:

- gewonnener Pflanzenansatz → Folgeansatz → Topf und Weichstufe;
- verwahrter Ansatz → daraus entnommener Auszug;
- vorbereiteter Zutatenansatz → lokale Anwendung;
- zerriebene Stängel → geseihter Ansatz → Anwendungsauszug → nächste Gabe;
- abgekühlte Badmischung → Umsetzen;
- durchgeleiteter Waschposten → Waschgang;
- abgeleitete Arbeitsflüssigkeit → Auffanggefäß;
- Überlaufposten → Frischwasserzugabe;
- Klarflüssigkeit → weitere Portionen;
- entnommene Sollmaßportion → Umsetzen;
- angesetzter Posten → Einlass;
- aufgestrichener und abgekühlter Ansatz → Absetzen.

Diese Lesungen verwenden ausschließlich bereits ausgewählte Kartenwerte. Die
173 Wörterbuchkarten und 381 Einzelereignisse bleiben unverändert; nur die 19
Zielsätze benennen den geerbten Inhalt jetzt ausdrücklich.

## Schreiberregel

Nach einer offenen Zelle:

1. Behalte den aktiven Materialposten, nicht einfach das letzte Substantiv.
2. Behalte ausdrücklich zurückgelegte Reserven unter eigenem Griff.
3. Behalte eine gesetzte Öffnungs-/Gerätestellung, bis sie geändert oder die
   nächste Zelle bestätigt wird.
4. Ein Record-Ende entlässt alle drei Register.

Das ist für mehrere Schreiber leicht lernbar: Das Bild setzt den Besitzer, die
Karten verändern Material und Zustand, offene Zellgrenzen reichen die Register
weiter, terminale Karten bestätigen einen Schritt.

## Dateien

- `HANDOFF_REGISTER.tsv`: alle 19 Übergaben mit Quell- und Zielanweisung;
- `RECORD_RELEASE_REGISTER.tsv`: die acht layoutbedingten Freigaben;
- `SELECTED_173_HANDOFF_DICTIONARY.tsv`;
- `SELECTED_381_HANDOFF_INTERLINEAR.tsv`;
- `SELECTED_116_HANDOFF_SENTENCES.tsv`;
- `SELECTED_11_HANDOFF_RECORDS.md`: vollständige fortlaufende Lesefassung.

Die Kreis-/Astroseiten bleiben getrennte Diagrammregister. Keine zusätzliche
Seite wurde verwendet.
