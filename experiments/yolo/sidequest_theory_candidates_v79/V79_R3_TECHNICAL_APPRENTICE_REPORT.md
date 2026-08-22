# V79 R3 — deterministische technische Lehrlingsmaschine

Status: unabhängiger Werkstatt-Audit über die festgelegten zehn Seiten;
**keine Übersetzung, keine Entzifferung und kein wissenschaftlicher Nachweis
einer Kustodenpraxis**.

## Ergebnis

Ein Lehrling kann die ausgewählten Einheiten mit einer kleinen, sechzehn Regeln
umfassenden Maschine formal vorwärts und rückwärts führen:

- Herbal `H2`: 24 Events;
- Herbal `H4`: 18 Events;
- Biological `B2`: 62 Events einschließlich `E180/E181` und vier sichtbarer
  Besitzerresets;
- Astro `f69v.4..31`: 28 direkt adressierte Plätze mit 33 opaken Gruppen.

Die vollständige Trace enthält 264 Zeilen: 104 Prosaevents vorwärts und 104
rückwärts sowie 28 Astroplätze vorwärts und 28 rückwärts. Jeder formale Input
wird exakt rekonstruiert.

Die zentrale Grenze bleibt scharf:

```text
mit Masterexemplar:
    formale Rekonstruktion 137/137 exakte Atome
    ausgewählte Inhaltsausschreibung als Lookup verfügbar

ohne Masterexemplar:
    formale Rekonstruktion 137/137 exakte Atome
    konkrete Prosa-Sachwerte 0/103
    konkrete Astro-Werte oder Ordnungen 0/28
```

Die 137 Atome sind 104 genaue Prosakarten plus 33 f69-Gruppen. Wegen der einen
Randkopie bilden die 104 sichtbaren Prosakarten nur 103 selbständige
Quellpositionen. „Mit Master“ bedeutet bloß, dass die bereits ausgewählte
V78-/V75-Ausschreibung nachgeschlagen wird; es ist keine semantische
Rückgewinnung aus der sichtbaren Schrift.

## Der kleine Zustandsautomat

```text
START
  ├─ Prosa: RESET_RECORD → OPEN_STATEMENT → SET_OWNER → READ_EXACT_CARD
  │                                      │
  │                         physischer Zeilenrand
  │                                      ↓
  │                              PENDING_EDGE_CARD
  │                         ┌────────────┴────────────┐
  │                  alle 4 Bedingungen       mindestens eine fehlt
  │                         ↓                         ↓
  │                  COLLAPSE_COPY              RELEASE_BOTH
  │
  │             sichtbare Besitzerlücke → RESET substance/target/direction
  │
  └─ Astro: SET_F69_LEFT_NAMESPACE → DIRECT_LOCAL_SLOT → COPY_OPAQUE_GROUPS
                                            └─ kein Start/keine Richtung
```

Der Automatenzustand enthält nur Record, Satz, physische Zeile, örtlichen
Bildbesitzer, genaue ungeteilte Kartenidentität und gegebenenfalls eine am
Zeilenrand gepufferte Karte. Ein Master-Schalter darf eine occurrence-gebundene
Ausschreibung anhängen, ändert aber weder Wörterbuch noch formalen Zustand.

## Vorab eingefrorene Randkopie-Regel

Vor Öffnung der 19 einzelnen Übergangszeilen wurde in
`V79_R3_EDGE_COPY_RULE_FREEZE.json` genau diese Regel festgeschrieben:

```text
gleiche exakte Karte am Ende von Zeile L und Anfang der nächsten Zeile
+ gleicher eingefrorener Satz
+ gleicher sichtbarer Besitzer
+ line-final NONCLOSE, also kein Close dazwischen
→ erste sichtbare occurrence = antizipierende Randkopie
→ zweite occurrence = einmal gelesener Quelltoken
```

Keine Seite, kein Locus, kein bestimmtes Wort und kein Register darf eine
Ausnahme auslösen.

### Vollständiges Ergebnis über alle 19 Übergänge

| Größe | Ergebnis |
|---|---:|
| ausgesuchte Gelegenheiten | 19 |
| gleiche exakte Karte | 1 |
| gleicher sichtbarer Besitzer | 15 |
| line-final `NONCLOSE` | 19 |
| vorhergesagte Randkopien | 1 |
| TP | 1 |
| FP | 0 |
| FN | 0 |
| TN | 18 |

Der einzige Treffer ist:

```text
B2-S005
f82r.3  E180  b5fcea1eaed06b2f2291  PER?
         [physischer Zeilenrand; Satz und Besitzer bleiben offen]
f82r.4  E181  b5fcea1eaed06b2f2291  PER?

Vorwärts:  E180 puffern und nicht sprechen; E181 einmal lesen.
Rückwärts: einen PER?-Quelltoken an E181 setzen und am vorigen Zeilenrand
           dieselbe exakte Karte als sichtbare Vorausnahme kopieren.
```

Das Ergebnis ist mechanisch sauber: Der Lehrling braucht weder die Eventnummern
noch eine memorierte f82-Ausnahme. Es ist aber gegen die **bereits editorisch
gesetzte V78-Reparatur** bewertet. `1/1` beweist daher nicht, dass E180 im
historischen Manuskript tatsächlich eine Kustode ist; es zeigt nur, dass die
Reparatur mit einer allgemeinen sichtbaren Regel reversibel gemacht werden
kann.

Die anderen 18 Übergänge werden vollständig in
`V79_R3_19_TRANSITION_AUDIT.tsv` veröffentlicht. Vier davon wechseln zugleich
den sichtbaren Besitzer und können schon deshalb keine Randkopie sein.

## Vollständige Forward-/Backward-Traces

### H2

Die Maschine führt 24 genaue Karten durch drei Felder und drei Sätze. Die zwei
`ET?`-Vorkommen `E027` und `E029` werden unverändert ausgegeben. Rückwärts
entsteht dieselbe Kartenfolge. Ohne Master bleiben Pressen, Fraktion, Öl,
Salbenposten und Anwendung unbekannt; der Formalapparat kennt nur die Karten,
Grenzen und die zwei fraglichen Linktoken.

### H4

Die Maschine führt 18 Karten durch vier Felder und vier Sätze. `E056` wird als
`PER?` ausgegeben, ohne eine weitere Bedeutung zu erfinden. Auch hier bleiben
Blatt, Wein, Wunde, Honig und Umschlag ohne Master vollständig unbekannt. Die
mechanische Rückschrift benötigt nur Codeblatt und Layout.

### B2

Die Maschine führt 62 Karten, 26 Felder und 22 Sätze. Sie kollabiert nur
`E180/E181`. Vier sichtbare Besitzerwechsel werden in beiden Richtungen als
harte Zustandslöschung geschrieben:

| Event | neuer Besitzer | Wirkung |
|---:|---|---|
| E189 | mittlere linke Geräte-/Inline-Knotenstation | Stoff, Ziel und Richtung löschen |
| E198 | ungelöste mittlere rechte Linie-/Liegepodeststation | Stoff, Ziel und Richtung löschen |
| E203 | unteres grünes Mehrfigurenfeld | Stoff, Ziel und Richtung innerhalb des laufenden Satzes löschen |
| E212 | lokale Randstationen des unteren Feldes | Stoff, Ziel und Richtung löschen |

Damit kann der Lehrling `B2` fortschreiben, ohne aus den Bildteilen einen
unsichtbaren globalen Wasserlauf zu erfinden.

### f69-left-28

Die 28 Plätze werden **direkt**, nicht zyklisch aufgerufen. Ein Trace-Schritt
setzt `F69_LEFT_WHEEL_NS`, adressiert genau den sichtbaren Besitzer
`L01..L28`, kopiert dessen ein oder zwei opake Gruppen und stoppt. Insgesamt
werden 33/33 Gruppen vorwärts und rückwärts rekonstruiert.

Die numerische Reihenfolge in der TSV ist lediglich editorische Auditordnung.
Die Maschine kennt keinen authorialen Start, keine Drehung, keine Laufrichtung,
keine Verbindung zum mittleren/rechten f69-Rad und keinen f68↔f69-Schlüssel.
Mit Master kann sie die vorhandene V75-Lokaletikette nachschlagen; ohne Master
bleiben Himmelsname, Kalenderwert und Reihenfolge 0/28 rückgewonnen.

## `ET?` gegen stillen `LINK/SLOT`

Der gesprochene Arbeitswert `ET?` deckt alle 19 V78-Vorkommen formal ab. Ein
stiller `LINK/SLOT` deckt dieselben 19/19 ab, benötigt keinen Wortlaut und ändert
denselben Automatenzustand nicht. Es existiert in dieser Runde kein unabhängiger
Sachendpunkt, der zwischen beiden entscheidet.

Ergebnis:

`ET?_AND_SILENT_LINK_SLOT_TIED`

`ET?` bleibt der vorgeschriebene kreative V78-Arbeitswert, wird aber nicht
gegen den einfacheren nichtlexikalischen Rivalen gewonnen.

## `PER?` gegen `ENTRY/RESET`

Die Wortlesung wird mechanisch repariert: neun sichtbare Karten ergeben nach
dem einmaligen, regelgeleiteten Kollaps acht Quelltoken. Der Lehrling kann die
Verdopplung vorwärts erkennen und rückwärts aus dem Layout wieder einsetzen.

Der formale Rivale liest dagegen alle neun sichtbaren Karten direkt als
`ENTRY/RESET`-Marken und benötigt überhaupt keinen Kollaps. Die neue Maschine
macht `PER?` somit ausführbar, aber nicht ökonomisch oder semantisch überlegen.

Ergebnis:

`EDGE_COPY_REPAIR_PASSES_MECHANICALLY__ENTRY_RESET_SIMPLER_OR_TIED`

## Fehleraudit

- Formale Forward-/Backward-Fehler mit Master: 0/137.
- Formale Forward-/Backward-Fehler ohne Master: 0/137.
- Falsch-positive Randkopien: 0/19.
- Falsch-negative Randkopien gegen die eingefrorene V78-Annotation: 0/19.
- Verpasste B2-Besitzerresets: 0/4.
- Konkrete Prosa-Sachwerte ohne Master: 103/103 fehlen.
- Konkrete Astro-Werte ohne Master: 28/28 fehlen.

Der wichtigste „Fehler“ ist daher kein Kopierfehler, sondern die vollständige
Abhängigkeit des Inhalts vom Exemplar. Eine genaue formale Rückschrift ist
nicht dasselbe wie Lesen oder Verstehen.

## Urteil

Die V78-Ausgabe ist einem Werkstattlehrling als **formale Kopier- und
Registermaschine** vermittelbar. Die E180/E181-Reparatur benötigt keine
ortsgebundene Ausnahme und besteht ihren engen mechanischen V79-Test. Das
stärkt nur die interne Ausführbarkeit der kreativen Ausgabe.

Ohne Masterexemplar gewinnt die Maschine keinerlei konkrete Pflanzen-, Bade-
oder Himmelsbedeutung zurück. `ET?` bleibt mit einem stillen Link gleichauf;
`PER?` bleibt trotz bestandener Randkopie formal schwächer oder höchstens
gleichauf mit `ENTRY/RESET`. V79 R3 fügt keine Karte, kein Wort und keine
Bedeutung hinzu.

## Artefakte

- `V79_R3_EDGE_COPY_RULE_FREEZE.json`
- `V79_R3_MACHINE_MANUAL.tsv`
- `V79_R3_FORWARD_BACKWARD_TRACES.tsv`
- `V79_R3_19_TRANSITION_AUDIT.tsv`
- `V79_R3_ERROR_AUDIT.tsv`
- `V79_R3_BUILD_SUMMARY.json`
- `build_v79_r3_apprentice_machine.py`
- `validate_v79_r3_apprentice_machine.py`
- `V79_R3_VALIDATION.json`

Es wurden ausschließlich zentrale V78-Prosa und V75-Astro-Artefakte der festen
zehn Seiten verwendet. f84 und f84r blieben versiegelt; kein Commit oder Push
wurde ausgeführt.
