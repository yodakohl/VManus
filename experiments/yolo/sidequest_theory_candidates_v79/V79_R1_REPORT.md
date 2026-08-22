# V79 R1 — unabhängige Lehrlingsprobe

## Ergebnis

Ein neuer Schreiber kann die ausgewählten Einheiten mit einem 16-Schritt-Manual formal vorwärts kopieren und rückwärts in dieselben Karten-, Grenz- und Besitzerstrukturen zerlegen.

Die Pflichttraces sind vollständig:

- H2: 24/24 Ereignisse;
- B2: 62/62 Ereignisse, einschließlich E180/E181 und aller vier sichtbaren Besitzer-Resets;
- f69v linkes Rad: 28/28 lokale Slot-Buckets mit 33/33 opaken Gruppen.

Die allgemeine Carry-Regel findet unter allen 19 Satz-internen physischen Linienübergängen genau den ausgewählten E180→E181-Fall:

`TP=1, FP=0, FN=0, TN=18`.

Damit besteht PER? den engen V79-Falsifikator mechanisch, bleibt aber wegen nur eines Positivbelegs und des gleich starken Formal-/Dittographie-Rivalen probationär. ET? bleibt ebenfalls nur provisorisch; die Rückgewinnung der sichtbaren Karte unterscheidet ein Wort nicht von einem stummen formalen Link.

Die Validierung ist `PASS`. Dies ist eine Kopier- und Rückleseprobe einer kreativen Edition, keine Entzifferung.

## Das kompakte Manual

Der vollständige maschinenlesbare Text steht in `V79_R1_COMPACT_MANUAL.tsv`. Für einen Lehrling genügt folgende Kurzform:

1. Wähle genau einen eingefrorenen Record oder eine lokale Astro-Namespace. Kopiere Besitzer und Grenzen zuerst.
2. Kopiere jede sichtbare exakte Karte beziehungsweise opake Astrogruppe; ähnliche Formen werden weder vereinigt noch zerlegt.
3. `dcda…` wird als ein Fragezeichenwort `ET?` geführt und nur mit `UND?/AUCH?` rückgelesen.
4. `b5fcea…` wird probationär als `PER?` geführt und nur mit `DURCH?/GEMÄSS?` plus genau einem sichtbaren Exemplarkomplement rückgelesen.
5. Die zwei formalen Karten werden ausschließlich `[FORMAL; KEIN WORT]`.
6. Jede andere Karte bleibt `[EXEMPLARWERT UNBEKANNT]`; konkreter Inhalt steht ausschließlich in `[EXEMPLAR:…]`.
7. Ein physisches Zeilenende beendet keinen Satz. Satz- und Besitzergrenzen entscheiden.
8. Bei sichtbarer Lücke werden Stoff, Ziel und Richtung zurückgesetzt.
9. Astrogruppen bleiben in ihrem lokalen Rad, Paneel oder Slot. Es gibt keinen Seiten- oder Instrumentenschlüssel.
10. Vorwärts wird die Formspur geprüft; rückwärts wird erst die Formspur und danach, falls vorhanden, die Exemplarschicht gelesen.

## Die Carry-Regel ohne Locusliste

An jedem Satz-internen physischen Linienübergang prüft der Lehrling nur fünf sichtbare/formale Bedingungen:

1. links steht die letzte Karte der alten physischen Linie;
2. rechts steht die erste Karte der nächsten physischen Linie;
3. beide exakten Karten-IDs sind gleich;
4. Satz und lokaler Besitzer bleiben gleich;
5. weder links noch rechts steht `CLOSE`.

Sind alle Bedingungen erfüllt, werden beide sichtbaren Karten kopiert. Bei der Rücklesung ist die erste Kopie eine zeilenrandliche Vorausnahme; nur die zweite wird als ein Quellentoken gesprochen. Scheitert eine Bedingung, werden beide Ereignisse gewöhnlich und unabhängig gelesen.

### Vollständiger Audit

Die 116 V78-Statements enthalten 19 Linienübergänge in 18 Statements. Nur E180→E181 hat dieselbe exakte Karte an beiden Seiten. Dieser Übergang bleibt in B2-S005, beim selben Besitzer und ohne Close. Die Regel feuert dort.

Bei den übrigen 18 Übergängen unterscheiden sich die Karten. Vier davon enthalten zusätzlich einen sichtbaren Besitzer-Reset:

- B2: E202→E203;
- B3: E263→E264;
- B3: E290→E291;
- B4: E355→E356.

Es gibt keinen falschen positiven und keinen falschen negativen Carry-Fall. `V79_R1_CARRY_AUDIT.tsv` veröffentlicht alle 19 Kanten, nicht nur den Treffer.

Das Ergebnis ist praktisch stark, aber evidenziell schmal: Die Regel ist auf diesem Panel vollständig deterministisch und reversibel, besitzt jedoch nur einen Positivbeleg. Sie beweist weder eine allgemeine mittelalterliche Kustodenpraxis noch den Wortwert PER.

## Pflichttrace 1 — H2

H2 bindet E015–E038, drei Felder und drei Statements an denselben Ganzpflanzenbesitzer. Die Vorwärtsspur kopiert alle 24 Karten. Rückwärts entstehen:

- 20 Karten mit `[EXEMPLARWERT UNBEKANNT]`;
- zwei `[FORMAL; KEIN WORT]`;
- zwei `ET?`.

Die stärkste Lehrstelle ist E026–E031:

```text
E026 [EXEMPLARWERT UNBEKANNT]
E027 ET?
E028 [EXEMPLARWERT UNBEKANNT]
E029 ET?
E030 [FORMAL; KEIN WORT]
E031 [EXEMPLARWERT UNBEKANNT]
```

Der Lehrling kann die A–ET?–B–ET?–C-artige Formfolge reproduzieren. Mit dem Masterexemplar liest er die vollständige pflanzenbezogene Arbeitsausweitung. Ohne Exemplar bleiben Öl, Fraktion, Mischung, Salbe und äußerer Gebrauch unbekannt; nur die zwei ET?-Kategorien und zwei formalen Nichtwörter sind verfügbar.

Das beweist eine lehrbare Kartenordnung, nicht „et“ als Manuskriptwort.

## Pflichttrace 2 — B2

B2 bindet E167–E228, 26 Felder und 22 Statements. Vier sichtbare Lücken beginnen neue lokale Besitzer:

| Ereignis | neuer lokaler Besitzer | vorgeschriebene Korrektur |
|---|---|---|
| E189 | mittlere linke Geräte-/Inline-Knotenstation | Stoff, Ziel, Richtung resetten |
| E198 | mittlere rechte unaufgelöste Station | Stoff, Ziel, Richtung resetten |
| E203 | unteres grünes Mehrfigurenfeld | Stoff, Ziel, Richtung resetten |
| E212 | untere Beckenrandstationen | Stoff, Ziel, Richtung resetten |

### E180/E181 vorwärts

```text
f82r.3, Linienende: E180 = b5fcea… = sichtbare PER?-Kopie
[physischer Linienwechsel; gleicher Satz; gleicher Besitzer; kein Close]
f82r.4, Linienanfang: E181 = b5fcea… = Hauptkopie PER?
```

Beide Karten bleiben im Faksimile-/Literalbestand. Es wird nichts gelöscht oder vereinigt.

### E180/E181 rückwärts

Die sichtbare Regel klassifiziert E180 als Vorausnahme und E181 als Haupttoken. Der Quellentokenzähler liest `PER?` einmal. Ein gewöhnliches unabhängiges `PER? PER?` wäre weiterhin ein harter Syntaxbruch; die Carry-Regel ist die einzige zugelassene Reparatur.

B2 enthält insgesamt 55 unbekannte Exemplarkarten, vier formale Nichtwörter und drei sichtbare PER?-Karten. Ohne Masterexemplar sind die konkreten Bade-, Gefäß-, Flüssigkeits-, Temperatur- und Richtungsinhalte nicht wiedergewinnbar. Die sichtbaren drei PER-Kopien ergeben durch Carry zwei vorgeschlagene Quellentoken; ob diese DURCH oder GEMÄSS heißen, bleibt ohne Komplementexemplar offen.

## Pflichttrace 3 — f69v linkes 28-Slot-Rad

Der Lehrling kopiert die 28 sichtbaren lokalen Radial-Slot-Buckets des linken Rades. Die Adressen `L01`–`L28` sind nur editorielle Prüfhilfen, kein behaupteter Start und keine Laufrichtung.

- 28/28 Slots werden rekonstruiert;
- 33/33 opake Gruppen kehren in denselben Slot zurück;
- L01, L02, L22, L23 und L28 enthalten je zwei Gruppen, die übrigen je eine;
- alle bleiben in `A3_LEFT_WHEEL_ONLY`;
- kein Wert wandert zum mittleren oder rechten Rad.

Mit Exemplar kann der Lehrling die kreative lokale Mondstations-/Kalenderabschnittsbeschreibung abschreiben. Ohne Exemplar bleiben nur linkes Rad, lokaler Slot, Gruppenzahl und opake Identitäten. Name, Rang, Anfang, Richtung, Zyklus und Himmelsbedeutung sind nicht rückgewinnbar.

## Recovery-Matrix

| Trace | vorwärts exakte Identität | rückwärts exakte Identität | Grenzen/Besitzer | mit Exemplar | ohne Exemplar |
|---|---:|---:|---:|---|---|
| H2 | 24/24 | 24/24 | 3 Felder, 3 Statements | 24 Ausweitungen abschreibbar | 20 konkrete Inhalte unbekannt; nur 2 ET? + 2 Formal |
| B2 | 62/62 | 62/62 | 26 Felder, 22 Statements, 4 Resets | 62 Ausweitungen abschreibbar | 55 konkrete Inhalte unbekannt; 3 PER-Kopien/2 vorgeschlagene Token + 4 Formal |
| f69v links | 33/33 Gruppen | 33/33 Gruppen | 28/28 Slot-Buckets | 28 lokale Etikettausweitungen abschreibbar | keine Himmels-/Kalenderwerte; nur Namespace, Slots und Gruppen |

„Mit Exemplar“ bedeutet mechanisches Abschreiben. Es ist keine unabhängige semantische Wiedergewinnung.

## Lehrlingsfehler und Korrektur

Die zehn wichtigsten Fehler stehen vollständig in `V79_R1_ERROR_CONTRADICTIONS.tsv`. Besonders schwer sind:

- aus einem physischen Zeilenende ein Satzende machen;
- bei bloßem Linienwechsel Carry annehmen, obwohl die Karten verschieden sind;
- E180 beim Vorwärtskopieren auslassen, weil es rückwärts nicht gesprochen wird;
- E180 und E181 als zwei unabhängige PER-Wörter sprechen;
- ein sichtbares Besitzer-Reset ignorieren;
- ET? durch einen neuen Prozesssinn retten;
- einem formalen Nichtwort MASS, Maß oder Ziel geben;
- `[EXEMPLAR:…]` mit Kartenbedeutung verwechseln;
- L01–L28 als geordnete Mondhausfolge lesen;
- Werte zwischen den drei f69v-Rädern übertragen.

## Entzugsentscheidungen

### ET?

`RETAIN_PROVISIONAL__FORMAL_LINK_RIVAL_TIED`

ET? wird nicht entzogen, weil ein Lehrling alle 19 exakten Karten mit genau einer additiven Fragezeichenkategorie reproduzieren kann, ohne Zusatzsinn. Es wird nicht promoviert: Dieselbe formale Spur kann weiterhin ein stummer Link oder Slotfüller sein. Formrückgewinnung entscheidet diese Alternative nicht.

### PER?

`RETAIN_ON_PROBATION__VISIBLE_CARRY_RULE_TP1_FP0_FN0__FORMAL_OR_DITTOGRAPHY_RIVAL_LIVE`

PER? wird in dieser Runde nicht entzogen, weil die vorab verlangte lokusfreie Carry-Regel auf allen 19 Übergängen ohne FP/FN funktioniert und E180/E181 reversibel macht. Es wird nicht promoviert. Die Evidenz besteht aus genau einem positiven Carry-Fall; ein formaler Feldanfangs-/Resetmarker oder bloße Dittographie bleibt mindestens ebenso möglich.

## Wissenschaftliche Decke und Dateien

Es wurden keine Wörter, Kartenwerte, Stämme, Laute, PAGE_HOST-Werte oder Seiten ergänzt. Nur die bereits historisch belegten Fragezeichenkategorien ET?/PER? wurden geprüft; alle übrigen Inhalte bleiben geklammertes Exemplar. f84 und f84r blieben vollständig versiegelt.

Ausgaben:

- `V79_R1_COMPACT_MANUAL.tsv`
- `V79_R1_REQUIRED_TRACES.tsv`
- `V79_R1_REQUIRED_TRACES.md`
- `V79_R1_CARRY_AUDIT.tsv`
- `V79_R1_ERROR_CONTRADICTIONS.tsv`
- `V79_R1_BUILD_SUMMARY.json`
- `V79_R1_build_apprentice_audit.py`
- `V79_R1_validate_apprentice_audit.py`
- `V79_R1_VALIDATION.json`
