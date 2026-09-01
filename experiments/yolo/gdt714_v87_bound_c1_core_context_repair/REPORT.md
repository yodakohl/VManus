# GDT714 — V87 bound-C1 core/context repair

Status: `PASS_V87_18_BOUND_C1_READINGS_REVISED__18_TARGET_POSITIONS_12_PAGES__1_KEO_R_ONE_SHOT_SPAN__7_W0_135_W1_163_W2_19_W3__91_WEAK_READINGS_REMAIN__ALL_H0_NONE`

## Ergebnis

V87 bearbeitet die naechsten 18 schwachen C1-Ganzwortlesungen an 18
unveraenderten Positionen auf zwoelf bereits zugelassenen Seiten. Die 18
Kerne werden semantisch kompakter und kompositionell einheitlicher. Unbelegte Identitaeten
wie Droge, Arznei, Dosis und Charge verschwinden; erhalten bleiben die im
Arbeitsmodell sichtbaren Felder Menge, Portion, Zubereitung, trocken,
feucht, heiß, kalt sowie Anfangs-, Mittel- und Endstufe.

Beispiele:

```text
chedaiin   abgemessene Trockenmenge III, Mittelstufe
dshey      abgemessene Feuchtmenge, Mittelstufe
kor        heiße Portion
okees      heiße Zubereitung, Endstufe
orchey     trockene Portion, Mittelstufe
oteor      kalte Portion, Mittelstufe
oty        kalte Zubereitung, Anfangsstufe
```

`dshees` bleibt bewusst W1: `abgemessene Feuchtform, Endstufe` ist eine
brauchbare Default-Komposition, aber die interne Grenze D-SH-EE-S ist nicht
unabhaengig gesichert und gibt deshalb null neue Scorepunkte. `cholkain`,
`kc`, `keo`, `oteor` und `oty` werden sprachlich oder kontextuell repariert,
ohne Confidence-Promotion. `os` erhaelt ausschliesslich den maschinengeprueften
F_O-Bonus von drei Punkten und bleibt W0.

## Konkrete Rendererreparatur

GDT678 hatte den f7r.2-Rand bereits explizit entschieden. V87 macht diese
Entscheidung nun im kanonischen Kontextstrom ausfuehrbar:

```text
P288 keo + P289 r  ->  heiße Portion        (einmal)
```

Der neue Consumer-Trace konsumiert beide Quellpositionen, ersetzt P288 durch
genau diese eine Ausgabe und laesst P289 ohne eigene Ausgabe. Die komplette
f7r.2-Ausgabe besitzt dadurch acht statt neun Einheiten:

```text
eine Dosis vollständig trocknen und abschließen · heiße Portion · Blüte · Drogenstoff abmessen und abschließen · fertige abgemessene Mittelstufen-Trockenportion · heiß-trocken, Mittelstufe · kalt-trockene Zubereitung am Anfang des Grades · getrocknete Masse
```

Damit wird an dieser Stelle weder `heiße Zubereitung auf Mittelstufe` noch
`Wurzel` gedruckt. Der Span ist lokal und nicht exportierbar. Die globalen
Arbeitswerte bleiben erhalten: `keo = heiße Zubereitung, Mittelstufe` fuer seine
anderen GDT678-Kontexte und `r = Wurzel` fuer die 129 GDT661-Kontexte. Es wird
also weder ein freies `keo+r`-Gesetz noch ein neuer historischer Wortwert
erfunden.

## Bestand

- auditierte Lesungen / Positionen / Seiten: 18 / 18 / 12
- revidiert / bewusst gehalten: 18 / 0
- neue lokale Einmal-Spans / beruehrte Positionen: 1 / 2
- One-shot-Directives / tatsaechliche f7r.2-Ausgabeeinheiten: 2 / 8
- direkt gebundene Primaerevidenzzeilen: 18
- aktive Lesungen / Positionen: 324 / 479
- aktive Confidence-Stufen: `{"W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7, "W1_WEAK_WORKING": 135, "W2_PROVISIONAL_WORKING": 163, "W3_SOLID_WORKING_THEORY": 19}`
- komplettes Woerterbuch: 1582 Oberflaechen / 1586 Lesungen
- noch nicht einzeln bearbeitete schwache Lesungen: 91

## Grenze

Das ist die konkrete Arbeitsuebersetzung des aktuellen Modells, kein
bestaetigter Klartext. Confidence bleibt ein interner Evidenzindex, keine
Wahrscheinlichkeit. Keine neue Komponente wird als freies Voynich-Wort
exportiert; alle historischen Felder bleiben `H0_NONE`. Es wurden keine neue
Seite, kein Bild, keine neue Transkription, kein `f84` und kein `f84r` benutzt.
