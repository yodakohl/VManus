# V15 R4 — Kanzlei-Korrektor: Visual-Role-Audit des Bio-Wertdecks

Datum: 2026-08-21

Rolle: skeptischer Kanzleischreiber und Korrektor um 1420. Scope sind allein
`f81v`, `f82r` und `f83r`. Dies ist eine explorative Werkstatttheorie, keine
Übersetzung und kein kanonischer Grounding-Befund. `f84` und `f84r` blieben
versiegelt.

## Entscheidung

Die 38 Zielwerte sind **keine sichtbaren Objektrollen**. Vor dem Reveal ließ
sich kein Zielereignis sauber einer Figur, einem Becken, einer Leitung, einer
Zwischenstation oder einem Ausgang zuweisen. Alle 38 wurden deshalb als
`GENERAL_CONFIGURATION_OR_PAGE_OWNER` eingefroren, 20 mit `MEDIUM` und 18 mit
`LOW`. Die Bilder können den stillen Gegenstand einer Textzone liefern; die
einzelnen Felder besitzen aber keine Leader, siebenfachen Stationsmarken oder
stabilen räumlichen Entsprechungen.

Die nützlichste weiterlebende Theorie ist daher:

```text
gezeichnete Gesamtanordnung als stiller Besitzer
  + wiederverwendete Schreibschablone
  + lokale Angaben
  + einer von mehreren latenten Zustands-/Anwendungswerten
  + COMMIT
```

Das ist weder ein visueller Rollen-Decoder noch bloße Interpunktion. Die vier
Familien bleiben am besten **auswählbare Antworten eines Konfigurationsdecks**.
Ob diese Antworten medizinische Zustände oder gewöhnliche, häufige
Vorlagenwörter sind, entscheiden die drei Seiten nicht. Meine Rangordnung ist:

| Deutung | Konfidenz | Urteil |
|---|---:|---|
| latente Anwendungs-/Konfigurationswerte | .55 | führende Arbeitstheorie |
| generische Exemplar-, Stencil- und Kadenzwerte | .50 | stärkster Rivale |
| gewöhnliche abgekürzte Prosa mit häufigen Schlusswörtern | .39 | weiterhin möglich |
| direkte sichtbare Rollenwerte | .10 | durch den Blind-Audit stark geschwächt |

Die knappe Führung der Inhaltsdeutung bleibt explorativ stehen: Ein reines
Kadenzmodell erklärt die Seiten- und Schablonenbindung gut, muss aber außerdem
erklären, warum 16 der 38 Werte ganze Ein-Karten-Felder bilden und warum
`f82r.27` einen nichtbenachbarten identischen Wert auswählt. Umgekehrt darf die
medizinische Deutung nicht so tun, als habe die Blindkarte einen Behälter-,
Körper- oder Ausgangswert gefunden.

## Blindphase, Freeze und begrenzte Vorab-Leckage

Ein eigener Builder las die 281 erlaubten Bio-Ereignisse ausschließlich über
`./vmanus-exp query-tsv`, selektierte intern `DY=1/B3=0`, bestimmte die vier
führenden exakten Typen mit `12/10/8/8` und schrieb vor dem Freeze nur 38
neutrale IDs mit Seite, Locus, Record, Feldordinal, Feldlänge und
Feldposition. Keine Familie, Surface, Hülle oder Tuple-ID stand im maskierten
Paket.

- Masked packet:
  `V15_R4_PRE_REVEAL_MASKED_OCCURRENCES.tsv`
- Masked SHA-256:
  `c84b081a64b93d631d399736a0a075d47093fd00d3a79f7ca3183436a4642ba4`
- Rollen-Freeze:
  `V15_R4_PRE_REVEAL_VISUAL_ROLE_FREEZE.tsv`
- Freeze-Zeit:
  `2026-08-21T17:17:42.224308+00:00`
- Freeze-SHA-256:
  `99e613f2a252dd676b8729ee72cbc10670009130c7319031c6c254a778b96d08`
- Post-Reveal-Join:
  `V15_R4_POST_REVEAL_VALUE_ROLE_JOIN.tsv`

Transparenzhinweis: Ein zu breiter Discovery-`rg` zeigte vor der formalen
Maskierung kurz zwei alte Familienhashes und einzelne historische
Surface-Beispiele. Er zeigte weder die neue neutrale ID-Zuordnung noch eine
Bildrolle. Der Rollen-Freeze ist deshalb nicht vollkommen informationsleer,
aber die Leckage konnte hier keine Familie attraktiv auf eine Rolle ziehen:
alle 38 Rollen wurden aus demselben konservativen Bildkriterium als
Gesamtkonfiguration eingefroren. Die maschinenlesbare Freeze-Metadatei
dokumentiert die Leckage ausdrücklich.

## Warum keine feinere Bildrolle eingefroren wurde

Auf `f81v` stehen zwei Prosablöcke über einem großen Gemeinschaftsbecken mit
Zuleitung. Der untere Block gehört plausibel zum Beckenkomplex, doch kein Feld
zeigt auf eine der vielen Figuren oder auf Ein-/Ausgang. Auf `f82r` ist Text um
mehrere Figuren, gestapelte Gefäße, eine liegende Figur und den unteren grünen
Komplex geflossen. Nähe trennt Figur, Gefäß und Leitung nicht. Auf `f83r`
stehen Textblöcke neben drei linken Vignetten, einem Bogen und einer
serpentinenartigen unteren Leitung; auch dort fehlen Feld-Leader.

Ein Korrektor darf deshalb sagen „dieser Absatz gehört zu dieser gezeichneten
Anordnung“, aber nicht „Feld 3 ist die Leitung“ und „Feld 6 ist der Ausgang“.
Gerade `f82r.27` besitzt sieben Textzellen, ohne sieben sichtbare Stationen.
Eine feinere Zuordnung wäre nachträgliches Ausmalen der Schriftstruktur.

## Vollständiger 38er-Nachweis nach Reveal

| Familie | Frequenz | vollständige Loci/Felder |
|---|---:|---|
| `VAL-A` | 12 | `f81v.17 F2`; `f81v.18 F2`; `f81v.24 F2`; `f81v.27 F2`; `f82r.7 F2`; `f83r.11 F1`; `f83r.14 F3`; `f83r.24 F1`; `f83r.26 R2F1`; `f83r.28 R2F2`; `f83r.37 R2F3`; `f83r.44 R2F1` |
| `VAL-B` | 10 | `f82r.2 F3`; `f82r.19 F1`; `f82r.26 F1`; `f82r.27 F3`; `f82r.27 F6`; `f83r.6 F3`; `f83r.14 F2`; `f83r.22 F2`; `f83r.25 R2F1`; `f83r.27 R2F1` |
| `VAL-C` | 8 | `f81v.2 F1`; `f81v.18 F3`; `f81v.18 F4`; `f83r.11 F2`; `f83r.20 F3`; `f83r.20 F4`; `f83r.25 R2F2`; `f83r.28 R2F1` |
| `VAL-D` | 8 | `f82r.23 F2`; `f83r.3 F3`; `f83r.6 F4`; `f83r.11 F4`; `f83r.14 F5`; `f83r.15 F3`; `f83r.37 R2F2`; `f83r.41 R2F1` |

`R2` bezeichnet Record 2, nicht Agent R2. Der Join enthält zusätzlich neutrale
Occurrence-ID, Feldlänge, Position, Surface, Hülle, eingefrorene Rolle,
Konfidenz und Begründung für jede einzelne Zeile.

## Value × Role

| Wert | FIGURE | VESSEL | CONDUIT | JUNCTION | ENDPOINT | GENERAL | UNOWNED | gesamt |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `VAL-A` | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 12 |
| `VAL-B` | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 10 |
| `VAL-C` | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 8 |
| `VAL-D` | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 8 |

Das ist kein „alle Werte bedeuten Gesamtkonfiguration“-Treffer. Es ist ein
Nullergebnis für die feinere sichtbare Rolle: Die Eigentumsauflösung reicht
nicht aus, um eine Assoziation zu messen. `VISUALLY_UNOWNED` wurde nicht
nachträglich in attraktivere Klassen verteilt; `GENERAL` wurde nur dort
verwendet, wo wenigstens ein Seiten- oder Vignettenbesitz plausibel war.

## Page-, Stencil- und Feldkontrollen

### Seite

| Wert | f81v | f82r | f83r |
|---|---:|---:|---:|
| `VAL-A` | 4 | 1 | 7 |
| `VAL-B` | 0 | 5 | 5 |
| `VAL-C` | 3 | 0 | 5 |
| `VAL-D` | 0 | 1 | 7 |

Die Seite ist informativer als die eingefrorene Bildrolle. Besonders die
Nullen von B/D auf `f81v` und C auf `f82r` passen zu Seiten- oder
Vorlagenwortschätzen. Sie könnten ebenso unterschiedliche Anwendungen oder
Zustandsinventare verschiedener Bildtypen anzeigen; ein sichtbares Objekt
identifizieren sie nicht.

### Stencil

`f81v.17` und `f82r.7` besitzen beide das Feldschema `1|3|1|4`; in beiden
steht `VAL-A` am Ende des dreigliedrigen zweiten Feldes. Das ist der stärkste
generische Stencil-Fall: Ein Kopist kann denselben graphischen Takt und dieselbe
Schlusskarte aus einem Muster übernehmen, ohne eine Bildrolle zu kodieren.

Weitere Doppelungen sind zweischneidig:

- `f81v.18 F3–F4` wählt zweimal benachbart `VAL-C`;
- `f83r.20 F3–F4` wählt ebenfalls zweimal benachbart `VAL-C`;
- `f82r.27 F3/F6` wählt `VAL-B` nichtbenachbart;
- `f83r.27 F2–F3` wiederholt außerhalb des Zieldecks zweimal exakt
  `shckhedy`.

Die ersten beiden können eine lizenzierte Doppelbelegung oder eine übernommene
Kadenz sein; der letzte ist ein guter Dittographie-Kandidat. Die nichtbenachbarte
Wiederkehr in `f82r.27` ist schwerer als bloßes zweimaliges Ansetzen der Feder
zu erklären.

### Feldform

| Wert | ONLY | LAST | beobachtete Feldlängen | beobachtete Feldordinale |
|---|---:|---:|---|---|
| `VAL-A` | 3 | 9 | 1–6 | 1–3 |
| `VAL-B` | 5 | 5 | 1–4 | 1, 2, 3, 6 |
| `VAL-C` | 3 | 5 | 1–4 | 1–4 |
| `VAL-D` | 5 | 3 | 1, 2, 4 | 1–5 |

Alle vier Werte wandern über Feldlänge und Ordinal. Keine Familie ist einfach
„erste Zelle“, „lange Zelle“ oder „Ein-Karten-Zelle“. Zugleich wurde das Sample
gerade unter `DY=1/B3=0` gewählt; seine Schlussstellung ist deshalb kein
unabhängiger Semantikbeweis. Die fast deterministischen sichtbaren Hüllen
(`VAL-A` meist `sh`, B/C `q`, D ohne Hülle) gehören zur exakten
Kartenrealisierung und dürfen nicht als neuer Bildbefund gezählt werden.

## f82r.27: sieben Zellen

Die vollständige Linie lautet formal:

```text
F1 pchedy | F2 rsheal daldy | F3 qokeedy | F4 rshedy |
F5 qoteedy | F6 qokeedy | F7 lochedy
```

Also:

```text
[lokaler Wert 1] COMMIT |
[Zusatz + lokaler Wert 2] COMMIT |
VAL-B COMMIT |
[lokaler Wert 4] COMMIT |
[lokaler Wert 5] COMMIT |
VAL-B COMMIT |
[lokaler Wert 7] COMMIT
```

F3 und F6 besitzen denselben exakten Wert und dieselbe eingefrorene
Gesamtkonfigurationsrolle. Das zeigt keine gleiche sichtbare Station: Es gibt
keine unabhängige siebenfache Bildzuordnung. Als Schreiberbefund ist es dennoch
stärker als eine Nachbar-Dittographie. Am besten ist „derselbe zulässige
Konfigurationszustand wurde an zwei getrennten Slots erneut gewählt“; knapp
dahinter liegt „dieselbe Kadenzkarte steht an zwei exemplarisch vorgegebenen
Abschlussstellen“.

## Drei durchgehende Rücklesungen

Die eckigen Ausdrücke sind Quellenklassen, keine entzifferten Wörter.

### f81v.18

```text
[lokaler Wert] COMMIT |
[Angabe] – unter demselben Bezug – [Angabe] – unter demselben Bezug – VAL-A COMMIT |
VAL-C COMMIT | VAL-C COMMIT | [offene lokale Fortsetzung]
```

Flüssige Arbeitslesung:

> Für die laufende Beckenanordnung bestätige zuerst eine lokale Angabe; führe
> zwei Unterangaben unter demselben Bezug bis zum Standardwert A; trage für
> zwei aufeinanderfolgende Zellen denselben Zustand C ein und fahre mit der
> lokalen Notiz fort.

Die zwei Zellen sind Schriftzellen, nicht nachgewiesene Badestationen.

### f82r.27

> Für die dargestellte Anwendung: bestätige lokalen Wert 1; bestätige Wert 2
> mit Zusatz; setze Zustand B; danach zwei andere lokale Zustände; setze
> Zustand B erneut; schließe mit einem siebten lokalen Zustand.

Diese Lesung bewahrt C=C des älteren Schemas nun korrekt als `VAL-B=VAL-B`,
ohne daraus gleiche Menge, Körperstelle oder Leitung zu machen.

### f83r.14

```text
[lokaler Wert] COMMIT | VAL-B COMMIT | VAL-A COMMIT |
[lokaler Wert] COMMIT | [Zusatz] VAL-D COMMIT |
[aktivierter/fortgesetzter lokaler Eintrag]
```

Flüssig:

> Für diese gezeichnete Einheit wähle einen lokalen Anfangswert, dann B und A,
> danach einen weiteren lokalen Wert und D mit Zusatz; eröffne anschließend
> die nächste lokale Angabe.

Die Abfolge mehrerer verschiedener Werte in einer Linie passt besser zu einer
Konfigurationsliste als zu einem einzigen Satzschlusszeichen.

## Konkrete Bedeutungsprobe

Die Daten tragen derzeit eher eine gemeinsame Taxonomie als vier sichere
Einzelwörter:

```text
VAL-A..D := kanonische Zustands-/Ergebnisantworten für die ganze Anwendung
```

Damit die Theorie wirklich generativ bleibt, friere ich folgende konkrete,
aber bewusst schwache Expansion als nächsten Prüfgegenstand ein:

| Familie | konkrete Arbeitsglosse | Konfidenz |
|---|---|---:|
| `VAL-A` | `STANDARD / BEREIT / ORDNUNGSGEMÄSS ABGESCHLOSSEN` | .30 |
| `VAL-B` | `AKTIV / ERWÄRMT / IN ARBEIT` | .27 |
| `VAL-C` | `EINGETAUCHT / FORTGEFÜHRT` | .24 |
| `VAL-D` | `ABGELEITET / ENDZUSTAND` | .22 |

Das sind keine lexikalischen Übersetzungen. Sie bilden eine mögliche
medizinisch-technische Prozessachse, auf der derselbe Zustand an zwei Slots
wiederkehren kann. `Badmedium`, `Körperteil`, `Leitungstyp` und `Ausgang` sind
schlechtere Defaultglossen, weil die Blindkarte keine entsprechende
Value×Role-Trennung fand.

## Stärkste generische Erklärung

Ein Schreiber erhält pro Seitentyp ein Exemplar mit kurzen, optisch
abgeschlossenen Feldern. Häufige Schlusskarten werden als Ganzheiten gelernt.
Eine Hülle sorgt für die gewohnte Ansetzung; `DY` liefert den lokalen
Abschluss. Der Kopist reproduziert Stencils wie `1|3|1|4`, übernimmt
Seitenwortschatz und wiederholt eine Schlusskarte, wenn das Exemplar dieselbe
Kadenz zweimal verlangt. Bild und Text teilen den Seitenplatz, ohne dass jede
Karte ein Bildobjekt benennt.

Dieses Modell erklärt:

- den starken Seiteneffekt;
- den Stencil-Zwilling `f81v.17/f82r.7`;
- die Hüllenkonstanz;
- die Mischung aus langen und Ein-Karten-Feldern;
- benachbarte Doppelungen und echte Kopierfehler.

Seine Schwäche ist, dass „Kadenzwert“ leicht nur eine Umbenennung bleibt. Es
muss vorhersagen, welche Karte an welcher Stelle kommt, statt jede Wiederholung
nachträglich als Rhythmus zu erklären.

## Stärkste medizinische Erklärung

Die Bildanlage liefert nicht sieben Objektspalten, sondern das stille Thema
eines ganzen Eintrags: Bad, Bewässerung, Leitung oder Anwendung. Die Felder
tragen mehrere Parameter dieser Anordnung. Die vier häufigen Karten sind
kanonische Zustände, Prozessstufen oder Resultate, die an verschiedenen
Parametern wiederverwendet werden können. Deshalb darf `VAL-B` sowohl F3 als
auch F6 von `f82r.27` füllen, und `VAL-C` darf zwei benachbarte Zellen erhalten,
ohne zweimal dasselbe sichtbare Objekt zu bezeichnen.

Dieses Modell passt zu den Bildern und den geschlossenen Kurzfeldern. Seine
Schwäche ist die fehlende unabhängige Zuordnung eines einzigen Werts zu heiß,
kalt, Bad, Körper, Fluss oder Ausgang. Es führt knapp, weil es mehr als den
Schreibduktus erklärt, bleibt aber vollständig von der generischen
Exemplarerklärung begleitet.

## Korrektorenaudit: Fehler und Segmentierung

1. **f81v.18, C–C:** echte gleiche Belegung oder Dittographie. Dass dasselbe
   Muster auf `f83r.20` wiederkehrt, macht eine lizenzierte Doppelbelegung
   plausibler, beweist sie aber nicht.
2. **f83r.27, `shckhedy–shckhedy`:** stärkster unmittelbarer
   Dittographie-Kandidat außerhalb des Zieldecks. Ein Korrektor würde zuerst
   das Exemplar prüfen, bevor er zwei Bedeutungen annimmt.
3. **f82r.27, B ... B:** kein normaler Nachbarfehler. Möglich sind bewusste
   Wiederwahl, exemplarisch wiederholter Slot oder Rücksprung zum falschen
   Abschlussmuster.
4. **f82r.3–4, qokaiin am Ende/Anfang:** Catchword/Wiederaufnahme und
   mechanische Dittographie bleiben gleich ernst.
5. **f83r.52, finales L/O:** offen gelassene Relation und falsche
   Zeilensegmentierung bleiben Rivalen.
6. **A-Surfaces `shedy/cheedy/tedy`:** nicht automatisch drei Fehler oder drei
   Wörter. Im exakten Formalmodell gehören sie zu einer Karte mit
   positions-/handabhängiger Realisierung.

## Feste Vorhersagen auf den drei Seiten

1. Eine zweite, vor Value-Identität geblendete Bildkartierung wird bei den 38
   Loci überwiegend `GENERAL` oder `UNOWNED` wählen; feinere Rollen werden
   zwischen Beobachtern schlecht übereinstimmen.
2. Ein scheinbarer Value×Objektrollen-Effekt verschwindet, sobald Seite,
   Textblock und Stencil kontrolliert werden. Bleibt er stabil, verliert mein
   Korrektorenmodell.
3. Stencil-/Kadenzmodell: Bei gleichen Feldformen und vergleichbarer
   Zeilenlage ist die Wertvorhersage besser als aus Figur/Becken/Leitung.
   `f81v.17` und `f82r.7` bleiben der positive Kontrollzwilling.
4. Inhaltsmodell: Nichtbenachbarte Wiederwahl desselben Werts tritt auch in
   anderen mehrzelligen Records auf und ist nicht auf gleiche absolute
   Feldordinale beschränkt.
5. Dittographie-Modell: unmittelbare exakte Doppelungen häufen sich an
   Exemplarwiederholungen oder Zeilen-/Feldgrenzen; nichtbenachbarte Wiederkehr
   sollte deutlich seltener sein.
6. Die vier Familien bleiben nach Entfernen aller `ONLY`-Felder erhalten und
   überlappen weiterhin in Feldlänge und Ordinal. Kollabiert eine Familie auf
   einen einzigen Takt, ist sie eher Kadenzkarte als Zustandswert.

## Schluss

V15 liefert aus Korrektorensicht einen nützlichen negativen und einen
positiven Befund. Negativ: Die vier Werte dürfen nicht als `FIGUR`, `BECKEN`,
`LEITUNG` und `AUSGANG` gelesen werden. Positiv: Vier stabile, mobile
Payload+Commit-Karten füllen unterschiedliche Felder, ganze Zellen und
wiederholte Slots. Die beste explorative Deutung bleibt deshalb ein
**bildbezogenes Konfigurationsregister mit latenten Zustandswerten**, dicht
gefolgt von einem **generischen Exemplar-/Kadenzregister**. Eine bessere
Theorie muss beide Seiten gleichzeitig schlagen: die reale Schreibschablone
und die wiederverwendbare Wertidentität.
