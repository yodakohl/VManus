# V48 R1 — invariante Werkstattparadigmen

## Rolle und Grenze

Diese Fassung denkt wie ein Lehrmeister einer kleinen Werkstatt um 1420: Eine
wiederkehrende Kartenkomponente muss für alle Schreiber einen kurzen,
gleichbleibenden Arbeitswert haben. Bild, Rezeptthema und vorheriger Satz dürfen
stille Argumente liefern, aber niemals den Stammwert ändern.

V47 blieb unverändert: die sechs Hostachsen `OK`, `OR`, `AL`, `E`, `OT`, `L`,
die fünf RIGHT-Werte sowie FRAME, INNER-D, DY und B3 wurden weder umbenannt noch
umgedeutet. Geprüft wurden alle 24 Mehrkarten-PAGE_HOSTs. Sechs waren bereits in
V47 eingefroren; für die übrigen 18 liegt in
`V48_R1_CANDIDATE_PARADIGMS.tsv` eine vollständige Annahme-/Ablehnungstafel vor.

## Die sechs neuen R1-Kerne

| Rang | Host | exakt gleicher Minimalwert | Karten / Ereignisse / Folios | Lehrmeisterurteil |
|---:|---|---|---:|---|
| 1 | `CHEY` | **AUSGEWÄHLTEN MATERIALANTEIL AUFNEHMEN** | 2 / 3 / 3 | stärkster neuer Kern |
| 2 | `CHOR` | **PFLANZENMATERIAL ZEITGEBUNDEN BESCHAFFEN** | 2 / 3 / 2 | starker kleiner Kern |
| 3 | `CH` | **FLÜSSIGEN BESTAND DURCH ABZUG TRENNEN** | 2 / 2 / 2 | brauchbare Operationskarte |
| 4 | `CHY` | **ERWÄRMTEN ANSATZ ZUFÜHREN ODER AUFLEGEN** | 2 / 2 / 2 | breiter als die alte Wärmedeutung |
| 5 | `OLK` | **TRANSFER ÜBER EIN ZWISCHENGLIED ODER IN EINEN EMPFÄNGER** | 2 / 3 / 3 | apparative Werkstattklasse |
| 6 | `RSHE` | **FLÜSSIGKEIT AN EINEN EMPFÄNGER ÜBERFÜHREN** | 2 / 2 / 1 | rücklesbar, aber nur ein Folio |

`CHEY` und `CHOR` sind die einzigen beiden, die ich einer Werkstatt schon jetzt
aktiv beibringen würde. `CH` und `CHY` sind konsistente Operationskarten, aber
mit nur je zwei Vorkommen. `OLK` ist eine nützliche technische Abstraktion über
Tuch und Becken. `RSHE` ist intern sauber, jedoch durch das einzelne Folio
besonders schwach. Die letzten vier sind daher keine gleich starken
Entzifferungsbehauptungen, sondern bewusst aggressive Kandidaten für die
Vierer-Synthese.

## Rückleseprobe

```text
dchey
  CHEY = AUSGEWÄHLTEN MATERIALANTEIL AUFNEHMEN
  lokal: die faserige untere Wurzel aufnehmen

otchey
  CHEY = AUSGEWÄHLTEN MATERIALANTEIL AUFNEHMEN
  FRAME-OT = markierten Sekundärbezug setzen
  lokal: den bezeichneten Anteil aufnehmen

chochor
  CHOR = PFLANZENMATERIAL ZEITGEBUNDEN BESCHAFFEN
  FRAME-O = Kontext/Voransatz fortsetzen
  lokal: die Pflanze im Frühjahr sammeln

qotchor
  CHOR = PFLANZENMATERIAL ZEITGEBUNDEN BESCHAFFEN
  FRAME-OT = markierten Sekundärbezug setzen
  lokal: vor der Blüte sammeln

dchdy / otchdy
  CH = FLÜSSIGEN BESTAND DURCH ABZUG TRENNEN
  DY = lokalen Arbeitsschritt schließen
  lokal: seihen / abziehen und den Schritt schließen
```

Die lokalen Wörter „Wurzel“, „Frühjahr“, „Blüte“, „Tuch“, „Becken“, „Wasser“
und „Person“ sind keine Stammwerte. Sie kommen weiterhin nur aus der kreativen
Zehnseiten-Arbeitstheorie.

## Bewusste Ablehnungen

Die auffällig häufigen Kandidaten wurden nicht automatisch aufgenommen:

- `Y` bleibt unbekannt: Anteil, Mischen und feuchte Heide widersprechen sich.
- `CHE` bleibt unbekannt: Spülen und Gleichteil-Mischen ergeben nur den
  wertlosen Oberbegriff „Nassprozess“.
- `LCHED` bleibt unbekannt: Beckenfolge ist reizvoll, aber „kühles Wasser“ passt
  nur nach starker Abstraktion.
- `O` bleibt unbekannt: Zusatz, Weinzugabe und Ziehen-bis-klar teilen keinen
  engen Werkstattwert.
- `D`, `ED`, `K`, `CHO`, `CHOL`, `EE`, `EEY` und `YK` bleiben Ganzkarten.

Die Kandidaten wurden aus identischem opakem PAGE_HOST plus kompatibler
Kartenfunktion gebildet, nicht aus frei gesuchten sichtbaren Substrings,
Edit-Abständen oder älteren Präfix-/Suffixideen.

## Vollständige Ausgabe

- `V48_R1_COMPLETE_173_CARD_LEXICON.tsv` enthält jede Karte;
- `V48_R1_COMPLETE_381_EVENT_INTERLINEAR.tsv` enthält jedes Vorkommen;
- `V48_R1_COMPLETE_135_FIELD_TRANSLATION.tsv` enthält jedes Feld;
- `V48_R1_VALIDATION.json` prüft Abdeckung und Wertgleichheit.

R1 reduziert dadurch 12 der 145 opaken V47-Karten auf sechs provisorische
gemeinsame Kerne; 133 Karten bleiben opak. Das ist eine kreative,
rücklesekonsistente Werkstatttheorie und keine Entzifferung oder Semantik.
`f84` und `f84r` wurden nicht geöffnet.
