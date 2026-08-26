# GDT446 — Die Karte kennen heißt noch nicht, sie ausführen dürfen

## Die Korrektur

GDT445 hatte die richtige Reihenfolge für die Kartensuche, aber eine zu grobe
Ausgabe: `EXACT_CATALOG` wurde unmittelbar zu `READ`. Das vermischt zwei
verschiedene Fragen:

```text
IDENTITÄT: Welche gelernte oder vorhergesagte Karte ist sichtbar?
AUSFÜHRUNG: Sind ihre Faktoren in genau diesem linken Kontext lizenziert?
```

GDT446 trennt beide Kanäle. Ein exakter Schlüssel bleibt ein exakter Schlüssel,
aber er darf keinen fehlenden Kopf und kein rotes Innenpaar überstimmen.

## Was sich konkret ändert

Im 1.563er Katalog sind bei neutralem Kontext:

- 1.482 Schlüssel grün ausführbar;
- 45 nur gelb ausführbar;
- 36 identifizierbar, aber nicht ausführbar.

Die 36 Stopps sind sehr aufschlussreich:

- 31 beobachtete Karten brauchen einen geerbten Handlungskopf;
- vier schmale Zukunftskarten brauchen ebenfalls einen Kopf;
- eine schmale Zukunftskarte, `S+P+AL`, enthält das rote Direktpaar `S>P`.

An den wirklichen 4.576 Ereignisstellen ist der Kontext vorhanden:

- 4.566 grün;
- 10 gelb;
- 0 Stopps;
- 4.576/4.576 Zustandsübergänge unverändert.

Die Korrektur entfernt also keine reale Lesung. Sie verhindert nur, dass ein
isolierter Katalogtreffer einen fehlenden Ausführungskontext vortäuscht.

## Der stärkste Einzeltest

```text
AIR+DY
Identität: schmaler exakter Anhangsschlüssel
ohne Kopf: STOP CLOSE:NO_ACTIVE_ACTION
mit eingehendem CH: lesbar als geerbter Schlusskontext
```

Ebenso:

```text
S+P+AL
Identität: schmaler exakter Anhangsschlüssel
Ausführung: STOP PAIR:S>P
```

Die Zukunftsprognose darf das rote Paar nicht in eine produktive Regel
verwandeln.

## Zwei vollständige Angriffstests

### Sichtbaren Slot löschen

Alle 471 bisher lesbaren getrennten Ketten wurden von `A+F+B` auf `A+B`
verkürzt. Ergebnis: 471/471 stoppen genau auf dem erwarteten roten Direktpaar.

### Geerbten Kopf entfernen

Aus allen 934 geretteten Schlusskontexten wurde der eingehende Handlungskopf
entfernt. Ergebnis: 934/934 stoppen auf `CLOSE:NO_ACTIVE_ACTION`, auch bei
exakter Kartenidentität.

Alle 1.405 Stopps erhalten Handlung und Argument. Damit sind sichtbarer Slot
und geerbter Kopf echte notwendige Eingaben und keine nachträglichen
Erklärungen.

## Korrekturledger zu GDT445

Über die drei dort publizierten Prüfbestände ändern 73 Zeilen ihre
Entscheidungsstärke:

- 62 von `READ` zu `READ_AMBER`;
- 11 von `READ` zu `STOP`.

Das sind Prüfkontexte, nicht 73 verschiedene Manuskriptfehler. Die elf echten
falschen Ausführungen liegen im neutralen Kandidatenbestand. Der reale Strom
bleibt stopfrei.

## Neue Bedienregel

```text
1. Identifiziere den exakten Schlüssel, falls vorhanden.
2. Zeige seinen Rang, aber führe noch nichts aus.
3. Prüfe immer Selector, Fokus, Paar, Schluss und eingehenden Zustand.
4. Nur der Faktor-/Kontextkanal entscheidet READ, AMBER oder STOP.
5. Identität darf einen STOP niemals überstimmen.
```

Das macht die Aufnahme neuer Seiten strenger und zugleich schneller: Wir
können eine Form sofort wiedererkennen, ohne aus Wiedererkennung eine falsche
grammatische Lizenz abzuleiten.
