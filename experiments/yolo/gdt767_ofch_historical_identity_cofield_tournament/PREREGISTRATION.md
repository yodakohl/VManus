# GDT767-Präregistrierung — historischer Identitäts- und Nachbarfeldtest

## Fragestellung

Können die bereits beobachteten vollständigen `ofch`-, `chor`-, `schor`- und
`lchor`-Wörter durch unabhängig lizenzierte Nachbarfelder einer konkreten
historischen Stoff- oder Arzneiformklasse zugeordnet werden, ohne dass ein
Zielwort, eine EVA-Initiale oder eine alte Analystenkomposition seine eigene
Bedeutung bestätigt?

Die Arbeitshypothese ist ein gemischtes pharmazeutisches Register um 1420:
gelernte Ganznamen stehen neben Pflanzenteil-, Form-, Zustand-, Grad-, Mengen-
und Prozessfeldern. Historische Wörter definieren vergleichbare Rollen, nicht
die Voynich-Schreibung.

## Fixierte Zielkohorte

- alle reader-exakten vollständigen Wörter, deren Oberfläche `ofch` enthält;
- zusätzlich exakt `chor`, `schor` und `lchor`;
- `pchor` ist kein Ziel und bleibt wegen seiner separaten Öffnungsrolle als
  Geber gesperrt;
- keine längere ähnliche Oberfläche wird als eines dieser Ganzwörter gezählt.

Rekonstruktionsziele:

- 25 `ofch`-Formen / 43 Vorkommen;
- `chor` 176, `schor` 3, `lchor` 2;
- insgesamt 28 Ganzformen / 224 Vorkommen.

Die Zeichenfolge `ofch` ist ausschließlich ein Kohortenselektor. Sie erhält
keinen Wort-, Stamm-, Laut- oder Abkürzungswert.

## Vor der Merkmalsextraktion gesperrte Geber

Die Gebermenge muss alle 28 Zieloberflächen, `pchor` und alle 172
GDT754-`PRODUCTIVE_COMPOUND`-Oberflächen ausschließen. Wegen Überschneidung
werden 200 verschiedene Oberflächen erwartet. Jeder verbleibende Geber muss
reader-exakt und quarantäne-sauber sein.

Es gibt keinerlei Rückgriff auf:

- frühere deutsche Zielglossen;
- sichtbare EVA-Anfangszeichen;
- Editdistanz oder Teilstringähnlichkeit;
- das verworfene `p/s/r/l = pulvis/semen/radix/lignum`-Modell;
- generische MATERIAL-Felder als Ersatz für Blatt, Wurzel, Holz, Harz, Salz
  oder Flüssigkeit.

## Fixierte Fenster und Merkmale

Pro Zielvorkommen werden `D1`, `R3` und `LINE` getrennt ausgegeben. Die
zugelassenen Merkmale sind:

```text
DRY | MOIST | HOT | COLD | STAGE | VALUE_AMOUNT |
CTHY_LEAF | CHOR_REPRO | PREP | PROCESS_CLOSE | H1 | H2
```

`CTHY_LEAF` verlangt das exakte vollständige `cthy`. `CHOR_REPRO` verlangt
exaktes vollständiges `chor`; im target-excluding Hauptlauf ist dieses Wort
gesperrt. Nicht vorhandene Identitätsmerkmale werden nicht aus breiteren
Rollen abgeleitet.

## Fixiertes historisches Deck

Das Deck umfasst 18 Karten:

- Stoff: benannte Droge, Blüte, Samen, Wurzel, Blatt, Holz/Rinde, Harz/Gummi,
  Salz;
- Form: offen, Rohdroge, getrocknete Droge, Pulver, Zubereitung, Mazerat oder
  feuchter Auszug, Öl, Wasser, Wein, Essig.

Die sechs Quellen sind Pal.lat.1234, Wellcome MS.542, Salzburg M I 89, Durham
MS B.III.12, Wellcome MS.105 und Wellcome MS.683. Jede Karte nennt ihre
historische Ausdrucksform, notwendige und verbotene Felder, passende
Recordkanäle und Attestationsgrenze. Historische Übereinstimmung gibt null
Schreibungs- und null Identitätskredit.

Über 28 Zielwörter sind genau 504 Kandidatenzeilen zu erzeugen.

## Fixierte Treffer- und Rangregel

Ein Kandidat trifft nur, wenn alle `gate_all_r3`-Merkmale, gegebenenfalls ein
`gate_any_r3`-Merkmal und kein `forbid_line`-Merkmal vorhanden sind. Eine
geforderte Wiederholung bedeutet mindestens zwei R3-Treffer.

Evidenzstufen:

```text
4 = wiederholter Treffer plus passende Zielrolle
3 = wiederholter Treffer ohne Rollenpassung
2 = ein Treffer plus passende Zielrolle
1 = ein Treffer ohne Rollenpassung
0 = kein Treffer oder vorab definierte semantische Redundanz
```

Die Rangfolge verwendet zuerst diese Stufe, dann den deskriptiven Score

```text
20*level + 10*(R3_hits/n) + min(9,R3_hits).
```

Ein zusätzlicher Explorationsscore darf Rollenpassung und den registrierten
Alt-Blütenkandidaten sichtbar machen, aber keine Evidenzstufe oder
Wörterbuchauswahl ersetzen.

`chor=Blattdroge` erhält eine Redundanzstrafe, sobald `cthy` wiederholt auf
derselben Linie steht. Die alternative Erwartung lautet dann: zwei
verschiedene Pflanzenteilposten. Blüte gegen Samen/Frucht bleibt offen.

## Fixierte Nebenprüfungen

1. Publiziere jede exakte `chor`/`cthy`-Parallelposition mit Richtung, Abstand,
   Reihenfolge und Direktheitsflag. Rekonstruktionsziel: 15 Positionen auf 14
   Loci, davon fünf direkte Paare.
2. Übernimm die vier GDT766-`ofch`-Kontakte mit `schor`, `chory` oder `shor`
   getrennt als Schattenaudit. Alle vier müssen null exakten-`chor`-,
   Identitäts-, Relations- und Komponentenwert behalten.
3. Gruppiere historische Kandidaten mit identischen vollständigen
   Supportvektoren als ungetrennte Rivalen.
4. Wähle pro Ganzwort Stoff- und Formkarte nur ab Evidenzstufe zwei;
   andernfalls verwende `S00` beziehungsweise `F00`.
5. Lass `chor` ohne einzelne Formklasse, falls mehrere unvereinbare
   Formkandidaten stark treffen.

## Readerregel

Alle 28 Zielwörter erhalten einen nichtleeren, konkreten, aber ersetzbaren
Default. Frühere Blütenlesungen dürfen als C0-Arbeitshypothesen stehen bleiben;
sie werden weder gelöscht noch bestätigt. Für `ofcheol` und `qofcheol` ist
„Blütenauszug“ nur bei unabhängiger Auszugs-/Flüssigkeitsevidenz zulässig,
sonst wird auf „Blütenzubereitung“ zurückgegangen.

Die fünf festgelegten Linien f22r.4, f22v.1, f41v.2, f93r.2 und f107r.38
enthalten zusammen 46 Tokenpositionen. Jede Position wird genau einmal in
geschriebener Reihenfolge ausgegeben. Semikolons sind Renderergrenzen und
keine behaupteten syntaktischen Relationen.

## Erwartete Artefakte und Claim-Grenze

Der Builder muss elf nichtleere Ergebnisartefakte erzeugen: Vorkommensatlas,
Formmatrix, `ofch`-Aggregat, `chor`/`cthy`-Atlas, Schattenaudit,
504-Kandidaten-Tournament, Separierbarkeit, 28er-Wörterbuch, 46-Token-Reader,
historischen Human Reader und `RESULT.json`.

Zulässig sind Form-/Zustandsklassifikationen, konkrete C0-Defaults, sichtbare
Rivalen und vollständige Arbeitslesungen. Nicht zulässig sind ein bestätigtes
Lexem, eine bestätigte Substanz oder Pflanze, eine Flüssigkeitsidentität, eine
Einheit, eine Sprache, ein Klartextsatz, Teilstringexport, ungesehene Formen,
neue Seiten/Bilder/Transkriptionen oder Zugriff auf `f84`/`f84r`.
