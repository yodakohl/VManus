# GDT779 — residuale exakte V99R7-Ganzwörter nach `ol`

Status: `PASS__50_EXACT_FALLBACK_WHOLES__44_FORMS__49_LOCI__245_CONTEXTUAL__131_FALLBACKS__205_CONSUMED__6_SANITIZATIONS__NO_COMPONENT_EXPORT`.

## Ergebnis

Die occurrence-ID-freie Regel beginnt ausschließlich bei den **181** noch
generischen GDT778-Fallbacks. Unter ihnen besitzen **99** Zeilen in **76**
vollständigen rechten Formen eine V99R7-Ganzwortkarte. Reader-Exaktheit lässt
**50** Spannen in **44** Formen auf **49** loci übrig; **49** nicht-exakte
Kandidaten bleiben sichtbar ausgeschlossen.

Alle 50 Treffer ersetzen direkt den generischen Ansatz-/Zubereitungswert. Die
kontextuelle Abdeckung steigt **195→245**, die Fallbackzahl fällt **181→131**
und der eindeutige Rechte-Token-Verbrauch steigt kollisionsfrei **155→205**.
Die Doppelstelle `f75r.26` wird als eine Passage mit zwei Zielspannen gerendert.

## Precedence-Kontrolle

Der vollständige 76er-Shadow enthält **179** Elternzeilen: 99 Fallbacks und 80
bereits kontextuelle Zeilen. Seine 127 exakten Zeilen teilen sich in 50 neue
Fallbacktreffer und **77 unverändert geschützte kontextuelle** Zeilen. Im finalen
44er-Deck stehen 68 rohe und 63 exakte Elternmatches; 13 der exakten Matches
waren bereits kontextuell und bleiben vollständig geerbt.

## Praktische Beispiele

- `f104r.14`: `ol oeeal` — `Ansatz-/Zubereitungsposten` → **Trockenmaterial I, Endstufe**.
- `f104v.3`: `ol dl` — `Ansatz-/Zubereitungsposten` → **Rohstoffmaß**.
- `f104v.9`: `ol chedaiin` — `Ansatz-/Zubereitungsposten` → **abgemessene Trockenmenge III**.
- `f106v.46`: `ol oky` — `Ansatz-/Zubereitungsposten` → **erste Wärmestufe**.
- `f107r.46`: `ol cheor` — `Ansatz-/Zubereitungsposten` → **trockener Teil**.
- `f108r.6`: `ol cheol` — `Ansatz-/Zubereitungsposten` → **Trockenmaterial**.

## Verbleibende Restschuld

Die 131 Fallbacks zerfallen jetzt ohne erneuten Korpuszugriff in 37 Stellen
ohne rechtes Token, 49 nicht-exakte Stellen mit V99R7-Karte, 20 nicht-exakte
Stellen ohne Karte und 25 reader-exakte Stellen ohne Karte. Nur die letzte
25er-Klasse ist sofort für neue vollständige Ganzwortkandidaten zugänglich;
nicht-exakte oder leere Rechtsfelder werden nicht still repariert.

## Kartenhygiene und Grenze

Die 44 Karten teilen sich disjunkt in 32 direkt geerbte Ganzwortkarten, sechs
patientenfrei sanierte Karten, drei ausschließlich für die neue exakte
`ol + Ganzwort`-Spanne lizenzierte Karten, zwei als Ganzwort geerbte
Kompositionskarten ohne Teilformexport und eine spätere vollständige
GDT755-Ganzwortkarte (`qockhey` → **mische**). Alte Quellenformulierungen sind
nur im Provenienzaudit sichtbar und steuern weder Auswahl noch Renderer.

Die Werte bleiben ersetzbare praktische Ganzwortdefaults. GDT779 bestätigt
kein EVA-Zeichen, keinen Wortteil, kein Lexem, keine Sprache und keinen
Klartextsatz. Es wurden keine neuen Seiten, Bilder, OCR oder Transkriptionen
geöffnet; `f84` und `f84r` blieben gesperrt. Das GDT388-Paket bleibt
`VALID_ACQUISITION_NOT_SCORE_READY`.
