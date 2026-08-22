# R2 — historische Wärme-, Zeit- und Prozessrunde

## Rollenprofil, unverändert übernommen

1. Du kennst zeitgenössische Herbarien, Materia medica, Rezeptbücher, Abkürzungen und kompilierte Sammelhandschriften.
2. Du vergleichst Namen, Beschreibungen, Qualitäten, Habitate, Zubereitungen, Anwendungen und Rezeptfortsetzungen.
3. Du unterscheidest überlieferte Textpraxis von modernen Tabellen-, Datenbank- oder Übersetzungsannahmen.
4. Du darfst historische Quellen recherchieren, aber niemals Voynich-Formen über Klang oder Buchstabenähnlichkeit zuordnen.
5. Du lieferst die historisch plausibelste Quelltextstruktur samt Gegenbelegen und eng begrenzter Pseudoübersetzung.

## Ergebnis

Die beste knappe Prozessordnung benutzt nicht eine einzige „Zeit“-Silbe, sondern drei getrennte kleine Achsen und einige gelernte Zustandskarten:

```text
E / EE / EEE     KURZGRAD / HALTEGRAD / VOLLGRAD
IIN              GRAD, genauer Soll- oder Öffnungsgrad
OT / OL          FOLGE / FORTSETZUNG

CHK              WÄRMEN
CTH              BEREIT
SHED             ABSETZEN
```

Dazu kommen gelernte Ganzkarten wie `STANDZEIT`, `DAUER`, `ABSETZSTAND`, `KLARPUNKT`, `ANWÄRMEN`, `NOCH WARM`, `HANDWARM`, `ROH`, `TEMPERIERT`, `AUSKÜHLEN` und `KÜHLLAGER`. Das passt besser zu einer medizinisch-technischen Rezeptsammlung als die Annahme, jeder sichtbare Gradträger müsse eine genaue Zahl von Minuten oder Stunden bedeuten.

Diese Ausgabe bleibt eine kreative Werkstattlesung, keine Entzifferungsbehauptung. Keine Form wurde über Klang, Buchstabenähnlichkeit oder eine moderne Sprache zugeordnet.

## Arbeitsbereich

- Ausgangspunkt war ausschließlich die aktive ausgewählte Stoff-/Flüssigkeitsausgabe.
- Prosaseiten: f10r, f11r, f55v, f56r, f81v, f82r und f83r.
- Keine zusätzliche Seite, kein neues Bild, keine neue Transkription.
- Die Astro-Ausgabe wurde nicht verändert.
- f84 und f84r blieben vollständig versiegelt.
- Alle 173 exakten Karten behalten einen konkreten Default.
- Eine Wortkarte erhält keinen ganzen Satz als Stammwert.

## Historischer Vergleich, ca. 1370–1450

Die Edition *Medieval Welsh Medical Texts* beruht auf vier frühen medizinischen Sammlungen des späten 14. Jahrhunderts und ist deshalb ein besonders naher Vergleich für die Arbeitsweise, nicht für die Sprache des Voynich-Manuskripts. [Editionsüberblick](https://www.ncbi.nlm.nih.gov/books/NBK558253/)

In Buch 5 erscheinen genau die Prozessunterscheidungen, die hier getrennt werden:

- Rezept 5/1 lässt eine Mischung neun Tage stehen, kocht sie danach, presst sie durch Leinen und verwahrt sie.
- 5/2 kocht in Weißwein bis zur Halbierung, presst, kocht erneut und rührt, bis die Hitze vergangen ist.
- 5/22 reduziert beim Kochen bis zur Hälfte und gibt die Arznei, solange sie warm ist.
- 5/23 unterscheidet Wein von lauwarmem Wasser.
- 5/27 setzt zwei oder drei Tage sowie zweimal tägliche Reinigung an.
- 5/38 erhitzt bis zu einem beobachtbaren Härtepunkt.
- 5/47 lässt einen Ansatz sieben Tage reifen, kocht, presst und verwahrt ihn.
- 5/50 verlangt einen zweiten Kochgang; 5/51 langes Kochen und Anwendung der warmen Mischung.

Siehe den [edierten Primärtext mit Übersetzung](https://www.ncbi.nlm.nih.gov/books/NBK558238/), besonders 5/1–2, 5/22–23, 5/27, 5/38, 5/47 und 5/50–51.

Das historische Muster ist wichtig: Rezeptschreiber unterscheiden

1. eine Tätigkeit wie kochen, anwärmen oder absetzen;
2. einen qualitativen Zustand wie roh, lauwarm, warm, klar oder hart;
3. eine Dauer oder Wiederholung wie neun Tage, bis zur Hälfte, erneut oder zweimal;
4. den nächsten Schritt beziehungsweise die Fortsetzung mit dem vorigen Ansatz.

Genau diese Trennung motiviert das R2-Modell. Sie beweist keine einzelne Kartenbedeutung.

Die bereits aktive Vergleichsquelle, das Bologneser Rezeptmanuskript 2861 aus dem 15. Jahrhundert, zeigt ebenfalls aufgelöste Abkürzungen, Maßzeichen und getrennte Wärme-/Stoffzustände. [Biblioteca Universitaria di Bologna](https://bub.unibo.it/it/bub-digitale/manoscritto-bolognese). Die vor 1438 abgeschlossene norditalienische Rezeptsammlung Othmer MS 1 ist ein zweiter zeitnaher Vergleich für eine große Fachkartenliste um einen kleineren Prozesskern. [Othmer MS 1](https://openn.library.upenn.edu/Data/0025/html/OthmerMS1.html)

## 1. E / EE / EEE: Arbeitsgrad, nicht ein universeller Zeitwert

Die drei Grade sind in mehreren verschiedenen Wirten verwendbar:

| Grad | Default | Karten | Ereignisse | lokale Realisierungen |
|---|---|---:|---:|---|
| E | KURZGRAD | 7 | 30 | kurz anlegen, kurz benetzen, mild wärmen, kurz auffangen, kurz absetzen, kurz bereithalten |
| EE | HALTEGRAD | 12 | 32 | länger halten, länger einwirken, warm halten, länger auffangen, länger absetzen, länger fortsetzen |
| EEE | VOLLGRAD | 1 | 1 | vollständig durchtränken |

Die Bedeutung ist deshalb nicht schlicht `E = eine Zeiteinheit`. Beim Auffangen und Absetzen ist der Unterschied zeitlich; beim Wärmen ist er mild gegenüber gehalten; beim Durchtränken ist EEE ein Vollständigkeitsgrad. Der gemeinsame Kern ist die **Arbeitsstufe**.

Die wichtigsten Kompositionen lauten:

```text
OK + E  + Y       kurz anlegen
OK + EE + Y       länger halten
OK + E  + DY      kurz benetzen; Schluss
OK + EE + DY      länger einwirken; Schluss
OK + EEE + DY     voll durchtränken; Schluss

CHK + E  + Y      mild wärmen
CHK + EE + Y      warm halten
CHK + EE + DY     warm halten; Schluss

SOLK + E  + Y     kurz auffangen
SOLK + EE + Y     länger auffangen
SOLK + EE + DY    länger auffangen; Schluss

SHED + E  + DY    absetzen lassen; Schluss
SHED + EE + DY    länger absetzen lassen; Schluss
```

Das ist die stärkste Verbesserung dieser Runde: ein einziger Gradkontrast erklärt Kontakt, Wärme, Auffangen und Absetzen, ohne die Tätigkeit selbst in E hineinzulesen.

## 2. IIN: GRAD; AIIN bleibt MASS

Die drei IIN-Karten bilden eine kleine Zieltabelle:

| Form | Komposition | Default |
|---|---|---|
| `oiiin|soiiin` | IIN | Sollgrad |
| `kaiiin` | K + IIN | Weichgrad |
| `daiiin` | DA + IIN | Öffnungsgrad II |

`IIN=GRAD` ist nicht `AIIN=ZEIT`. Die exakte AIIN-Karte `aiin|chaiin|daiin|saiin|taiin` bleibt in 20 Ereignissen **VORGESCHRIEBENES MASS**. Zwei gelernte Ganzkarten können AIIN dennoch lokal in einen zeit-/standähnlichen Fachnamen aufnehmen:

- `SHFYDAIIN = STANDZEIT`;
- `CHLDAIIN = ABSETZSTAND`.

Das exportiert keine produktive Regel `AIIN=Zeit`. Gerade die ähnlich aussehenden `daiin` und `daiiin` müssen als verschiedene exakte Karten behandelt werden.

## 3. CHK: WÄRMEN

CHK bleibt über vier Karten konstant:

| Form | Default | Ereignisse |
|---|---|---:|
| `cheky` | mild wärmen | 3 |
| `cheeky` | warm halten | 2 |
| `chkeey` | Posten warm halten | 1 |
| `chkeedy` | warm halten; Schluss | 1 |

Die E-Stufe liefert mild/kurz, die EE-Stufe gehalten/länger, Y den laufenden Posten und DY den Schluss. CHK muss weder „Feuer“ noch einen bestimmten Temperaturwert heißen.

## 4. CTH: BEREIT; SHECTHY bleibt TEMPERIERT

Die produktive Bereitschaftsfamilie ist kurz:

```text
CTHY              bereit                 7 Ereignisse
CTH + E + Y       kurz bereithalten      2 Ereignisse
```

`SHECTHY=TEMPERIERT` bleibt dagegen eine gelernte Ganzkarte. Sie wird nicht in SH+CTH+Y zerlegt. Das ist historisch plausibel: ein Rezept kann sowohl einen allgemeinen Fertigzustand als auch ein gelerntes Wort für einen temperierten Zustand besitzen.

Weitere gelernte Zustandskarten sind:

- `QEKEY = ROH`;
- `ROL = NOCH WARM`;
- `LOL = HANDWARM`;
- `RSHEAL = WARMWASSER`;
- `SKAR = WARMAUSGUSS`.

## 5. SHED: ABSETZEN

Das frühere „ruhen oder absetzen“ war keine echte Wörterbuchentscheidung. Als Arzt-/Apothekerschreiber wähle ich für die Flüssigkeits-, Becken- und Auffangabläufe den konkreten Werkstattwert **ABSETZEN**:

| Form | Default | Ereignisse |
|---|---|---:|
| `cheedy|shedy|tedy` | absetzen lassen; Schluss | 12 |
| `sheedy` | länger absetzen lassen; Schluss | 1 |
| `shedal` | Absetzstelle | 2 |
| `solshedy` | mit dem Vorigen absetzen; Schluss | 1 |
| `qokshedy` | zum Absetzen stellen; Schluss | 1 |

Diese Entscheidung macht B3-S014 knapp lesbar: **Wasser in Gang setzen → länger absetzen lassen → Schluss.** Sie passt auch zur expliziten Beckenfolge B3-S026.

Gegenbeleg: In einer rein körperlichen Anwendung könnte „ruhen“ besser klingen. Auf den festen Seiten erklärt `ABSETZEN` jedoch mehr technische Flüssigkeitsnachbarn und liefert die kürzere wiederverwendbare Karte.

## 6. Gelernte Wärme-, Zeit- und Endpunktkarten

| exakte Karte | R2-Default | Status |
|---|---|---|
| `schoal` | Weinsud | Produktname; Kochen nicht als freier Stamm exportiert |
| `qotchol` | anwärmen | gelernte Ganzkarte |
| `oltchy` | anwärmen | gelernte Ganzkarte |
| `tchody` | auskühlen; Schluss | gelernte Ganzkarte |
| `chary` | auskühlen | gelernte Ganzkarte |
| `ral` | abkühlen | aktive Ganzkarte bestätigt |
| `ody` | Kühllager; Schluss | gelernte Ganzkarte |
| `rol` | noch warm | gelernter Gebrauchszustand |
| `lol` | handwarm | gelernter Zielzustand |
| `qekey` | roh | gelernter Ausgangszustand |
| `shecthy` | temperiert | aktive Ganzkarte bestätigt |
| `shfydaiin` | Standzeit | kurzer Fachname |
| `chckhal` | Dauer | aktive Ganzkarte bestätigt |
| `chldaiin` | Absetzstand | beobachtbarer Endpunkt |
| `chealror` | Klarpunkt | beobachtbarer Endpunkt |

`STANDZEIT`, `DAUER`, `ABSETZSTAND` und `KLARPUNKT` sind vier verschiedene Dinge: vorgegebene Wartephase, freie Dauerangabe, mechanischer Pegel/Zustand und sichtbarer Klärendpunkt. Sie dürfen nicht als eine allgemeine „Zeit“-Kategorie kollabieren.

## 7. OT und OL: FOLGE versus FORTSETZUNG

### OT = FOLGE

Elf Kompositionen und 21 Ereignisse benutzen OT für den geordneten Nachschritt:

```text
OT + OR          Folgeansatz
OT + AIIN        Folgemaß
OT + AL          Folgestelle
OT + Y           Folgeposten
OT + AR          Folgeauslass
OT + E + DY      danach kurz einwirken; Schluss
OT + EE + DY     danach länger einwirken; Schluss
OT + CHED + DY   Folgeumsetzung; Schluss
OT + OL          danach fortsetzen
```

„Nächst“ bei einem Gegenstand und „danach“ bei einer Handlung sind zwei grammatische Realisierungen derselben Folgebeziehung.

### OL = FORTSETZUNG

Zehn Kompositionen und 34 Ereignisse verbinden den laufenden Schritt mit schon vorhandenem Material:

```text
OL               fortsetzen
OL + DY          fortsetzen; Schluss
OK + OL          Fortsetzung einsetzen
OL + CHED + DY   fortsetzen; Schluss
OL + AIN         Fortsetzungsportion
OL + OR          Fortsetzungsansatz
CH + OL          Fortsetzungsposten
OK + EE + OL     länger fortsetzen
OL + SHED + DY   mit dem Vorigen absetzen; Schluss
```

`VORIGER POSTEN` und `WEITERARBEITEN` werden damit nicht mehr als zwei unverbundene OL-Bedeutungen behandelt: Beides ist **FORTSETZUNG aus dem Vorigen**.

## 8. Wiederholung und Stufen

- `QOKOKCHY = WIEDERANSATZ`: der doppelte Arbeitsaufruf wird zu einem kurzen gelernten Wiederholungswort.
- `LKEDY = DOPPELWASCHUNG; SCHLUSS`.
- `CHEEETY = ERSTE SPÜLUNG` bleibt unverändert kurz.
- Mehrere genaue Ganzkarten heißen erste oder zweite Öffnung; sie werden nicht zu einer produktiven Zahlensilbe vereinigt.
- `CHODALY = BLÜTEBEGINN` und `KEOL = JE GABE` bleiben lokale Herbal-Zeitkarten.

## Exakte Gegenbeispiele

1. **AIIN ist nicht IIN.** Zwanzig AIIN-Ereignisse tragen Maß; vier IIN-Ereignisse tragen Grad.
2. **SHECKHAL ist nicht CHCKHAL.** SHECKHAL heißt mäßige Menge, CHCKHAL Dauer.
3. **SHEY, SHEEY, LCHEEY und CHEEETY sind keine E/EE/EEE-Paradigmen.** Sie sind Klarauszug, erste Öffnung, benetzte Stelle und erste Spülung.
4. **DSHEDY ist nicht SHED.** Die exakte Karte bleibt Frischwasser; Schluss.
5. **OTYTCHOL ist kein OT-Kompositum.** Es bleibt die gelernte Karte AUFFANGEN.
6. **QOTCHOL ist nicht produktiv OT+OL.** Es ist als Ganzkarte ANWÄRMEN gespeichert.
7. **OLTCHY, ROL, LOL und TEOL werden nicht wegen sichtbarem `ol` als Fortsetzungsformen zerlegt.** Ihre exakten Werte sind anwärmen, noch warm, handwarm und erste Öffnung.
8. **SCHOAL ist nicht SCHO+OL.** Es bleibt der Produktname WEINSUD.

## Korrektur eines alten Wärmesatzes

`OLDY` hat zwei Ereignisse und die aktive exakte Kartenbedeutung Fortsetzung plus Schluss. Im bisherigen Kontext hatte B4-S010 dennoch die frei erfundene Aussage „Erwärme den Bade- oder Waschzusatz sanft und beende den Arbeitsschritt“, während H4-S003 dieselbe Karte anders verwendete.

R2 vereinheitlicht beide Ereignisse zu:

> **FORTSETZEN; SCHLUSS**

Damit geht eine attraktive Wärmeanweisung verloren, aber die genaue Kartenidentität wird wieder eingehalten. Wärme in B4 bleibt durch echte CHK-, WARMWASSER- und WARMAUSGUSS-Karten reichlich vertreten.

## Konkrete Rücklesungen

### H1-S002 — f10r

> Laufenden Posten einsetzen → **anwärmen** → mit dem vorigen Ansatz fortsetzen → **bereit**.

Das ist die kürzeste Herbal-Wärmekette: Handlung, Fortsetzung und Fertigzustand sind getrennt.

### H3-S001 — f11r

> Blütenkraut → Weinsud bereiten → auswringen → **Standzeit** einhalten → nachseihen → Klarauszug → **auskühlen; Schluss**.

Die Karte `SHFYDAIIN` enthält nicht mehr den ganzen Satz „für die vorgeschriebene Zeit stehen lassen“, sondern nur den Fachnamen STANDZEIT.

### H4-S003–S004 — f55v

> Maß des Postens → Auszug entnehmen → **warm halten** → fortsetzen; Schluss.

> Vorgeschriebenes Maß → Stelle → **anwärmen** → Ansatz → Posten → Ansatzportion.

### B1-S008 — f81v

> Posten → Fortsetzung → **mild wärmen** → Fortsetzung → **absetzen lassen; Schluss**.

### B2-S005 und B2-S012 — f82r

> Posten zur Stelle setzen → Seihtuch → Durchlass → Maß → gleiche Einstellung → **Posten warm halten** → abziehen und schließen.

> Flüssigkeitsposten abziehen → Klarauszug → **kurz bereithalten** → länger halten → benetzte Stelle → Maß → Posten → **voll durchtränken; Schluss**.

### B3-S014, B3-S021 und B3-S026 — f83r

> Wasser starten → **länger absetzen lassen; Schluss**.

> Maß → bereit → Stelle → Posten → Maß → **Absetzstelle** → temperiert → Posten → Stelle → bereit → umsetzen; Schluss.

> Beckenstation → **Absetzstand** → Posten umsetzen → Portion → bereit → **Klarpunkt** → länger auffangen; Schluss.

### B4-S011 und B4-S015 — f83r

> Maß → mild wärmen → länger fortsetzen → Portion → Posten umsetzen → Fortsetzung → **Doppelwaschung; Schluss**.

> Portion → Klarauszug → Portion → **Dauer** → kurz auffangen → hinausführen; Schluss.

### B5-S003 und B6-S001 — f83r

> Absetzstelle → Stelle → Fortsetzung → bis **handwarm** → an der Stelle umsetzen → Maß → Fortsetzung → **Öffnungsgrad II** → Posten umsetzen.

> Länger auffangen → **roh** → erste Öffnung → Fortsetzung → Maß → Fortsetzung → Tuch → Posten → bezeichnete Stelle.

## Was nicht geschlossen ist

- `HANDWARM` für LOL ist der beste konkrete Singletonwert, aber ein allgemeiner Wärmepunkt bleibt ein starker Rivale.
- `ABSETZEN` für SHED ist im technischen Flüssigkeitsablauf besser als `RUHEN`; in einer eindeutig körperlichen Passage könnte diese Entscheidung kippen.
- `WEINSUD` impliziert historische Zubereitung durch Wärme, doch SCHOAL allein beweist das Verb KOCHEN nicht.
- E/EE/EEE ordnen Grade; sie liefern keine absoluten Zeiten oder Temperaturen.
- OT/OL ordnen Schritte und Fortsetzung, nicht notwendigerweise grammatische Tempora.
- Die Öffnungszahlen können Apparaturstationen statt zeitliche Reihenfolge bezeichnen.

## Artefakte und Validierung

- `R2_173_DICTIONARY.tsv`: 173 vollständige Karten.
- `R2_381_INTERLINEAR.tsv`: 381 vollständige Ereignisse.
- `R2_116_SENTENCES.tsv`: 116 vollständige Aussagen.
- `R2_11_RECORDS.md`: 11 vollständige Records.
- `R2_PARADIGM.tsv`: 77 eindeutige Wärme-/Zeit-/Folge- und Kontrollkarten mit allen Event-IDs.
- 56 Karten, 138 Ereignisse und 80 Aussagen wurden revidiert.
- `R2_VALIDATION.json`: PASS, 49 Prüfungen.

Builder und Validator sind `R2_BUILD_THERMAL_TEMPORAL.py` und `R2_VALIDATE_THERMAL_TEMPORAL.py`. Route und Ledger wurden nicht verändert; es wurde nichts committed oder gepusht.
