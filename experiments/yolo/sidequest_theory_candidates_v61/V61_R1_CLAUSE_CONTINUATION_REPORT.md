# V61 R1 — Aussagen und Fortsetzungen über physische Zeilen

Status: vollständige kreative Werkstattausgabe für elf Prosarecords, keine
Entzifferung. Eine physische Zeile ist Layout; weder Zeilenreset noch
Feldschluss wird als gesprochenes Satzzeichen behandelt.

## Ergebnis

Die 11 Records enthalten 57 physische loci, 135 Felder und 381 Ereignisse.
Innerhalb der Records liegen genau 46 Grenzen zwischen aufeinanderfolgenden
loci. R1 klassifiziert sie vollständig:

| Klasse | Grenzen | Werkstattfunktion |
|---|---:|---|
| `CONTINUE_SAME_CLAUSE` | 19 | offenes Schlussfeld und erstes Folgefeld auf demselben Klauselzettel lesen |
| `RESUME_ACTIVE_ITEM` | 8 | neue Klausel, aber Besitzer/Arbeitsbestand aus dem Register wiederaufnehmen |
| `NEXT_PARALLEL_CELL` | 10 | gleicher Bildbesitzer, neue gleichrangige Aktions-/Parameterzelle |
| `START_NEW_CLAUSE` | 8 | neue Prozessphase ohne grammatische Fortsetzung |
| `UNRESOLVED` | 1 | Grenze sichtbar offenhalten und keine fehlende Prosa erfinden |

Aus 135 zunächst getrennten Feldkandidaten entstehen damit 116 Aussagen. 98
bleiben auf einem locus, 17 überspannen zwei loci und eine Aussage überspannt
drei loci. Die 19 fortgesetzten Grenzen liegen in 18 Aussagen, weil
`B5-S003` zweimal über die Zeile trägt.

Das ist eine konservative Werkstattsegmentierung: Innerhalb eines locus wird
jedes Feld zunächst als eigener Klauselzettel behandelt; nur ein ausdrücklich
begründeter `CONTINUE_SAME_CLAUSE` vereinigt Felder über eine Zeile. OPEN
erzwingt keine Fortsetzung, TERMINAL beweist kein Satzende.

## Vollständigkeit nach Record

| Record | loci | Felder | Events | Grenzen | Aussagen | Grenzprofil |
|---|---:|---:|---:|---:|---:|---|
| H1 | 2 | 2 | 14 | 1 | 2 | 1 RESUME |
| H2 | 3 | 3 | 24 | 2 | 3 | 1 RESUME · 1 PARALLEL |
| H3 | 3 | 4 | 17 | 2 | 4 | 1 RESUME · 1 PARALLEL |
| H4 | 2 | 4 | 18 | 1 | 4 | 1 START |
| H5 | 7 | 7 | 27 | 6 | 6 | 1 CONTINUE · 2 RESUME · 3 PARALLEL |
| B1 | 7 | 24 | 66 | 6 | 21 | 3 CONTINUE · 2 PARALLEL · 1 START |
| B2 | 8 | 26 | 62 | 7 | 22 | 4 CONTINUE · 2 START · 1 UNRESOLVED |
| B3 | 10 | 38 | 86 | 9 | 34 | 4 CONTINUE · 3 RESUME · 1 PARALLEL · 1 START |
| B4 | 10 | 20 | 47 | 9 | 16 | 4 CONTINUE · 2 PARALLEL · 3 START |
| B5 | 3 | 5 | 11 | 2 | 3 | 2 CONTINUE |
| B6 | 2 | 2 | 9 | 1 | 1 | 1 CONTINUE |

`V61_R1_11_RECORD_CONTINUATION_SUMMARY.tsv` enthält für jeden Record zusätzlich
die vollständige Werkstattlektüre, den technischen Ganzrivalen, das ausgewählte
V60-Kartenskelett, den stärksten Segmentierungsdruck und die geerbte
Hauptkontradiktion.

## Der entscheidende Carry f82r.3 → f82r.4

`B2-LB02` ist `CONTINUE_SAME_CLAUSE` und vereinigt F050 und F051 zu
`B2-S005`:

```text
F050 OPEN
  fahre am zweiten Lauf fort
  → durch ein Tuch
  → durch die verbundenen Läufe
  → beginne den nächsten abgemessenen Posten

ZEILENRESET — nicht sprechen

F051 TERMINAL
  beginne den nächsten abgemessenen Posten
  → unter derselben Einstellung
  → das breite Gefäß
  → ziehe es ab und beende den Schritt
```

Die doppelte Posteneröffnung arbeitet als Schreiber-Catchword: Das Ende der
ersten Zeile kündigt den Posten an, der Anfang der zweiten nimmt ihn erneut auf
und führt ihn zum formalen Feldschluss. Der stärkste Rivale ist
`RESUME_ACTIVE_ITEM`: Die Wiederholung könnte eine absichtliche neue Klausel
mit demselben Posten markieren. Entscheidend ist die veröffentlichte Kostenangabe:
Beide Felder besitzen im ausgewählten V60-Deck ein leeres Kurzskelett. Der
Carry beruht auf OPEN→TERMINAL und der geerbten lokalen Exemplarlesung, nicht
auf einer neuen Kartenbedeutung.

Die Lehrregel lautet: F050 am rechten Rand nicht abschließen; den aktiven
Posten auf derselben Klauseltafel stehenlassen, F051 anschließen und erst dort
den formalen Schluss setzen. Die wiederholte Eröffnung wird zweimal kopiert,
nicht gelöscht.

## Alle 21 f83r-Grenzen

| ID | locus-Grenze | Feldgrenze | Klasse | knapper Druck |
|---|---|---|---|---|
| B3-LB01 | .3→.6 | F074 OPEN→F075 T | RESUME | nächster Posten wird als gereinigter aktiver Lauf wiederaufgenommen |
| B3-LB02 | .6→.8 | F079 OPEN→F080 T | RESUME | ANWENDEN?-Portion bleibt Besitzer der neuen Füll-/Klärphase |
| B3-LB03 | .8→.11 | F081 OPEN→F082 T | RESUME | angewandter, gerührter Bestand kehrt als ANSATZ? zurück |
| B3-LB04 | .11→.14 | F086 OPEN→F087 T | CONTINUE | offenes Ablaufschließen erhält Abkühlung und Schluss |
| B3-LB05 | .14→.15 | F092 OPEN→F093 T | CONTINUE | Posten, BEREIT?, ZIEL? und Portion tragen in Maß/Zeit/Rückstand weiter |
| B3-LB06 | .15→.16 | F095 T→F096 T | PARALLEL | nach ABLASSEN? startet eine neue Reinigungs-/Heizzellengruppe |
| B3-LB07 | .16→.20 | F098 OPEN→F099 T | CONTINUE | klar werdender Beckenbestand wird abgesetzt und geschlossen |
| B3-LB08 | .20→.22 | F103 OPEN→F104 T | CONTINUE | ANWENDEN? + MASS? wird abgezogen und gleichteilig gemischt |
| B3-LB09 | .22→.24 | F107 T→F108 T | START | nach abgeschlossenem Abziehen beginnt eine vollständige Bereitschaftsphase |
| B4-LB01 | .25→.26 | F111 OPEN→F112 T | CONTINUE | offener Lauf erhält ANTEIL?, TEMPERIEREN? und ANWENDEN? |
| B4-LB02 | .26→.27 | F113 T→F114 T | PARALLEL | abgeschlossene Auflage wechselt zur Tuch-/Misch-/Badezelle |
| B4-LB03 | .27→.28 | F116 T→F117 T | PARALLEL | Filterschluss wechselt zu MASS?/Wärme/Öffnung/SPÜLEN? |
| B4-LB04 | .28→.35 | F119 T→F120 OPEN | START | abgeschlossener Kochschritt vor neuem warmem Maßposten |
| B4-LB05 | .35→.37 | F120 OPEN→F121 T | CONTINUE | offener Maßposten wird ausdrücklich als voriger Ansatz gewaschen |
| B4-LB06 | .37→.38 | F123 T→F124 T | START | abgeschlossener Einlauf vor neuer ANSATZ?-Anwendung |
| B4-LB07 | .38→.39 | F124 T→F125 OPEN | START | Sofortanwendung endet; neue Klarheits-/Dauerprüfung beginnt |
| B4-LB08 | .39→.41 | F125 OPEN→F126 T | CONTINUE | Dauerprüfung trägt in Öffnen und ABLASSEN? weiter |
| B4-LB09 | .41→.44 | F127 OPEN→F128 T | CONTINUE | Becken + ZIEL? erhält Warmwasser und Schluss |
| B5-LB01 | .47→.48 | F131 OPEN→F132 OPEN | CONTINUE | bloßer Zeitslot wird mit Ziel, Wärme und MASS? ausgefüllt |
| B5-LB02 | .48→.49 | F132 OPEN→F133 OPEN | CONTINUE | VORIGES wird an zweiter Öffnung weitergerührt |
| B6-LB01 | .52→.54 | F134 OPEN→F135 OPEN | CONTINUE | erste Öffnung/Voriges trägt in MASS?, Tuch, Portion und Ziel |

`T` bedeutet hier nur `TERMINAL`, nicht Satzpunkt. Die vollständigen
Begründungen und stärksten Alternativen stehen zeilenweise in
`V61_R1_46_LINE_BOUNDARY_INVENTORY.tsv`.

## So liest und schreibt der Lehrling

1. Recordbesitzer und aktiven Arbeitsbestand auf zwei getrennten Merktafeln
   setzen.
2. Jedes Feld als vorläufigen Klauselzettel kopieren; Kurzskelett ausschließlich
   aus den ausgewählten exakten V60-Karten übernehmen.
3. Am locus-Ende die betreffende `LB`-Zeile nachschlagen. Der physische
   Zeilenreset selbst sagt nichts.
4. Bei `CONTINUE` denselben Klauselzettel weiterführen; bei `RESUME` einen neuen
   Zettel beginnen, aber den aktiven Gegenstand behalten.
5. Bei `PARALLEL` Besitzer behalten und Aktions-/Parameterslots zurücksetzen;
   bei `START` auch die Prozessphase zurücksetzen.
6. Bei `UNRESOLVED` eine sichtbare Klammer setzen. Keine Konjunktion, kein
   Subjekt und kein Objekt ergänzen.
7. TERMINAL/CLOSE nur als formalen Feldschluss ausführen und niemals sprechen.
8. Erst nach der Segmentierung die vollständige lokale Werkstattlesung oder den
   nichtmedizinischen Rivalen aus dem Exemplar einsetzen; beide sind keine
   Kartenglossen.

Der Korrektor liest rückwärts: konkrete Klausel → Klauselzettel → Grenzklasse
→ constituent fields → exakte V60-Mnemonics/UNKNOWN → unveränderte Events.
Ein Lehrling fällt durch, wenn er locus=Satz setzt, OPEN automatisch mit der
nächsten Zeile verschmilzt, TERMINAL laut liest oder aus der flüssigen Klausel
eine neue Kartenbedeutung gewinnt.

## Stärkste Widersprüche

1. Nur 85/381 Ereignisse tragen überhaupt ein ausgewähltes Mnemonic; die
   konkrete Segmentierung wird überwiegend durch geerbte lokale Prosa getragen.
2. Die 90 TERMINAL- und 45 OPEN-Felder sind formale Feldzustände, keine
   unabhängig bestätigte Interpunktion.
3. `CONTINUE`, `RESUME` und `PARALLEL` sind bei mehreren OPEN-Grenzen durch
   dieselbe Oberfläche vereinbar; das Grenzledger veröffentlicht deshalb für
   jede Zeile einen stärksten Rivalen.
4. Der markanteste f82r-Carry hat überhaupt kein ausgewähltes Kurzskelett.
5. Acht RESUME- und zehn PARALLEL-Entscheidungen benötigen einen aktiven
   Bildbesitzer oder Arbeitsbestand, der nicht als Kartenwort bestätigt ist.
6. `B2-LB04` bleibt bewusst `UNRESOLVED`: klare Flüssigkeit kann weiterdosiert
   werden oder ein neuer Badeposten beginnen.
7. Die 116 Aussagen sind eine ausführbare Edition, keine bestätigte Syntax und
   keine Übersetzung.

## Artefakte und Validierung

- `V61_R1_46_LINE_BOUNDARY_INVENTORY.tsv`: alle 46 Grenzen mit vollständigem
  Vor-/Nachfeldkontext, Klasse, Begründung, Alternative und Lehrregel;
- `V61_R1_116_STATEMENT_CLAUSE_MAP.tsv`: alle 116 Aussagen mit Start/Ende,
  constituent fields, 381/381 Eventserien, Kurzskelett, vollständiger Lesung,
  Rivalen und Rückleseregel;
- `V61_R1_11_RECORD_CONTINUATION_SUMMARY.tsv`: vollständige Recordebene;
- `V61_R1_BUILD_CLAUSE_MAP.py` und `V61_R1_VALIDATION.json`: reproduzierbare
  Ableitung und Counts.

Validierung: `PASS` für 11 Records, 57 loci, 46 Grenzen, 116 Aussagen, 135
Felder und 381 Ereignisse. Alle 21 f83r-Grenzen sind markiert; F050/F051 bilden
genau eine zweizeilige Aussage. Keine neue Karte, Seite oder Bedeutung wurde
eingeführt.
