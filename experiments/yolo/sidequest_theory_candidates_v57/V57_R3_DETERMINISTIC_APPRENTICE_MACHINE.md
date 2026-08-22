# V57 R3 — deterministische Lehrlingsmaschine und Learnability-Audit

Status: unabhängiger technischer Notationspass; kreative Sidequest-Theorie,
keine Entzifferung.

## Urteil zuerst

`LEARNABLE_EXEMPLAR_NOTATION__NOT_LEARNABLE_BIDIRECTIONAL_SEMANTIC_CODEC`

Ein Lehrling kann die vorhandene Form mit kleinem Regelwerk zuverlässig
abschreiben, prüfen und zurück in eine **formale** Arbeitsanweisung zerlegen.
Er kann aber eine gewöhnliche Herbal-, Bade- oder Kalenderintention nicht
selbständig in die überlieferten Karten kodieren. Für jede opake lokale Karte
muss der Arbeitsauftrag schon die exakte Karten-ID oder ein Exemplar enthalten.
Damit ist die starke Übersetzungstheorie weiterhin überwiegend post-hoc
paraphrasiert. Lehrbar ist die Formular- und Kopierpraxis, nicht die behauptete
Quellsprache.

## Deterministischer Ein- und Ausgang

Die Maschine akzeptiert keine freie Prosa, sondern nur diese vorannotierte
Werkstattrepräsentation:

```text
PROSE_JOB := REGISTER + VISUAL_ID + TEMPLATE + RECORD+
RECORD    := IMAGE_ARG* + FIELD+
FIELD     := CARD (EDGE CARD)* + (CLOSE | END_OPEN_FIELD)
CARD      := CORE(P01..P04) | LOCAL(EXACT_CARD_ID)
EDGE      := JOIN | SPACE
LAYOUT    := LINE_RESET(position, renderer_bits)*

ASTRO_JOB := PAGE_TEMPLATE + (SLOT_ADDRESS + EXACT_GROUP_SURFACE+)+
```

`IMAGE_ARG` bindet einen sichtbaren Besitzer, Teil, Weg oder eine Station,
schreibt aber kein Wort dafür. `CLOSE` ist ein am letzten Kartenereignis
haftender Commit-Bit und kein ausgesprochenes „fertig“. `JOIN`, `SPACE` und
`LINE_RESET` sind Renderer-/Layoutdaten, keine Syntax. Ein Reset löscht nur den
physischen Zeilenanfangszustand; Record, Feld, Bildbesitzer und aktiver
Arbeitsstand bleiben erhalten.

Der Decoder gibt dieselbe Struktur zurück. Für P01–P04 kann er den minimalen
Kontrollprompt nennen; jede andere Karte wird als `LOCAL(EXACT_CARD_ID)`
zurückgegeben. Ein Bildknoten bleibt `IMAGE_ARG(node_id)`, nicht „Pflanze“,
„Becken“ oder „Körper“. Das ist absichtlich weniger flüssig als V53/V54 und
zeigt den wirklichen Informationsgehalt.

## Zustände, Regeln und Inventar

Die ausführbaren Übergänge stehen in
`V57_R3_STATE_MACHINE.tsv`. Die Maschine hat acht Arbeitszustände
(`S0`, `S1`, `S2`, `S3`, `S4`, `S5`, `S7`, `S8`) und 15 Übergangsregeln,
einschließlich der allgemeinen Ablehnung nicht eindeutiger Eingaben.

Der kleine gelernte Kern besteht aus:

| Schicht | Anzahl | Inhalt |
|---|---:|---|
| harte gemeinsame Kernprompts | 4 | `daiin/VORGABEPARAMETER?`, `SET(ARG_AIIN)`, `SET(ARG_AL)`, `FRAME_O(LINK)` |
| Strukturkontrollen | 6 | `IMAGE_ARG`, `LOCAL`, `JOIN`, `SPACE`, `CLOSE`, `LINE_RESET` |
| Register-/Diagrammschablonen | 5 | Herbal offen, Bio-Zelle, f67r2, f68r1, f69v |
| **aktiv zu lehrende Einträge** | **15** | ohne lokale Bedeutungsbehauptung |
| zusätzliche Tier-B-Mnemonics | 8 | nur Fragezeichen-Kommentare, keine deterministischen Opcodes |
| Prosa-Kopierregal | 173 Kartentypen | exakte Ganzkarten, überwiegend ohne Quellenwert |
| Astro-Kopierblätter | 395 Gruppen an 142 Loci | Vorkommen, nicht 395 behauptete Lexeme |

Die vier Kernmappings plus fünf Schablonen ergänzen die 15 Übergänge zu 24
kleinen Regel-/Lookup-Einträgen. Der große Aufwand steckt nicht in der
Grammatik, sondern im Kopierregal. Mechanisch wären 173 Prosa-Typen plus 395
Astro-Vorkommen 568 Nachschlageeinträge; diese heterogenen Größen dürfen nicht
als 568 Wörter ausgegeben werden.

## Kodier- und Dekodieralgorithmus

1. Wähle Register und sichtbare Seite. Herbal/Bio und Astro gelangen in
   getrennte Zustandsräume.
2. Binde Bildargumente als stumme Knotenreferenzen. Erfinde dafür keine Karte.
3. Öffne das passende Feldmuster. Bei einer Karte benutze genau eine der vier
   harten Konstruktionen **nur**, wenn Register, Position und exakte
   Realisierung eindeutig lizenziert sind; sonst kopiere eine lokale Ganzkarte.
4. Kopiere `JOIN`/`SPACE`. Leite die Kante nie aus deutscher Grammatik ab.
5. Setze `CLOSE` nur bei terminalfähiger letzter Karte; beende andere Felder
   offen.
6. Bei physischem Umbruch führe `LINE_RESET` aus und bewahre den logischen
   Zustand. Das doppelte `qokaiin` f82r.3–4 bleibt zweimal sichtbar.
7. Im Astro-Zustand kopiere nur Seitenadresse und lokale Gruppen. Ein direkter
   f68r1↔f69v-Join führt zwingend in `REJECT`.
8. Beim Rücklesen gib Kernprompts, lokale IDs, Bildreferenzen und formale
   Grenzen aus. Ergänze erst danach eine registerlokale Prosa und markiere sie
   als Expansion.

## Round-trip-Maße

Zwei Verluste müssen getrennt gerechnet werden:

```text
L_formal = 1 - korrekt rekonstruierte Karten/Felder/Resets / gelieferte Einheiten
L_sem_min = opake Ereignisse / alle Ereignisse
```

Mit vollständigem Karten- und Layoutblatt ist `L_formal = 0`: Der Lehrling
kopiert Identitäten, Kanten, Feldstatus und Resets. Das beweist nur
Reproduzierbarkeit. Ohne Layoutblatt sind physische Zeilen nicht aus der
Quellintention vorhersagbar.

Für die feste Prosaedition gelten dagegen:

| Maß | Wert | Bedeutung |
|---|---:|---|
| strenger Tier-A-Kern | 45/381 = 11,8 % | nur vier generische/formale Prompts |
| Ereignisse ohne Tier A | 336/381 = 88,2 % | keine harte Prompt-Kodierung |
| ausgewählte schwache Anker | 145/381 = 38,1 % | Fragezeichenwerte, nicht bestätigte Wörter |
| opake Ereignisse | 236/381 = 61,9 % | untere Grenze des semantischen Verlusts |
| Felder mit Tier A | 35/135 = 25,9 % | 100 Felder besitzen keinen harten Prompt |
| vollständig benannte Felder | 17/135 = 12,6 % | 118 Felder sind nur teilweise oder gar nicht benannt |
| Herbal opak | 68/100 = 68,0 % | Bild und Artikelgenre tragen viel Expansion |
| Bio opak | 168/281 = 59,8 % | Prozessprosa bleibt größtenteils lokal ergänzt |

Diese Verlustwerte sind großzügige Untergrenzen: Auch die 145 benannten
Ereignisse sind schwache Mnemonics oder formale Operationen. Pflanzenart,
Substanz, Körperteil, Becken, Rohr, Handlung, Menge, Richtung und
astronomischer Wert werden nicht aus den Karten zurückgewonnen.

## Fünf konkrete Drucktests

`V57_R3_ROUNDTRIP_TESTS.tsv` prüft drei vollständige Prosa-Records, den
publizierten f82r-Zeilenübergang und f69v als getrennten Astro-Fall.

- `f10r_R1`: 14 Karten und zwei Felder sind kopierbar; mindestens 64,3 % der
  Ereigniswerte und sämtliche konkreten Rezeptnomen bleiben unbestimmt.
- `f81v_R1`: 66 Karten und 24 Zellen sind kopierbar; mindestens 59,1 % der
  Werte sowie Becken-/Kreislaufhandlungen kommen nicht aus den Karten.
- `f83r_R4`: Beide Felder müssen offen bleiben; mindestens 66,7 % der Werte
  sind opak. Der Fall fängt den typischen falschen Schluss-Commit ab.
- `f82r.3–4`: `LINE_RESET` erhält den Arbeitszustand, aber beide
  `qokaiin`-Vorkommen werden geschrieben; „carry“ oder „resume“ wird nicht
  dekodiert.
- `f69v`: 140/140 Gruppen an 31/31 Loci sind formal kopierbar, doch 0/140
  historisch identifizierte Regelwerte werden zurückgewonnen.

## Stärkster Widerspruch und Endentscheidung

Der stärkste Widerspruch gegen echte Lehrbarkeit ist die Eingabeanforderung
selbst: Um eine lokale Quellintention zu kodieren, muss der Lehrling bereits
die exakte lokale Karte, ihre Positionslizenz, ihren Separator und meist das
Layout kennen. Damit enthält der Arbeitsauftrag einen großen Teil der
gesuchten Ausgabe. Die kleine Zustandsmaschine validiert und reproduziert sie;
sie übersetzt sie nicht.

Das Ergebnis ist zweigeteilt:

1. **Ja, lehrbar:** als spätmittelalterlich plausible Exemplar-, Formular- und
   Registerpraxis mit stummen Bildargumenten, lokalen Ganzkarten, optionalem
   Commit und physischer Reflow-Regel.
2. **Nein, nicht lehrbar:** als autonomes System, das neue gewöhnliche
   Quellprosa eindeutig in Voynich-Karten verwandelt und diese wieder in
   dieselbe Quellintention zurückübersetzt.

Die kreative V53/V54-Prosa bleibt daher nützlich als lokale Anwendungsschicht,
aber sie ist nicht durch diesen Round-trip bestätigt. Astro bleibt vollständig
separat. Es wurden keine neuen Seiten, keine PAGE_HOST-/Substring-Regeln und
keine f84/f84r-Daten verwendet.
