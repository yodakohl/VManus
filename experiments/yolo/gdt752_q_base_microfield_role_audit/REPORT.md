# GDT752 — direkter q/Basis-Mikrofeldtest

## Ergebnis

Die q/Basis-Paare sind als **vollständige Formpaare** weiterhin interessant,
aber die konkrete Rollenregel „q-Form = Qualität/Zustand, Basisform =
Zubereitung“ hält im unabhängigen Außenfeld nicht.

Von 44 festen q/Basis-Kontakten auf 27 Seiten besitzen 27 auf beiden
Außenseiten ein vollständig begrenztes Mikrofeld. Darunter gibt es:

- **null** eindeutige Treffer für q-seitige Qualität/Stufe plus
  basisseitige `PREPARATION`;
- **null** eindeutige Umkehrtreffer;
- genau einen beidseitig belegten Fall, `qokeey/okeey` auf `f99r.50`, der auf
  beiden Seiten dieselben Achsen HOT|PREPARATION|LEVEL_II trägt und deshalb
  symmetrisch, nicht richtungsweisend ist;
- im breiteren Trägertest je einen Treffer in beide Richtungen.

Die 42 direkten Nicht-q-Kontrollen auf 36 Seiten sind nicht schwächer: 28
Felder sind vollständig, ein exakter Umkehrtreffer überlebt, und der breite
Trägertest ergibt zwei hypothesenkonforme gegen drei umgekehrte Fälle. Damit
ist die gesuchte Rollenrichtung keine q-spezifische Regel.

## Was mit dem einzigen attraktiven q-Treffer geschieht

`qokeol/okeol` auf `f99v.22` sieht zunächst passend aus. Außen neben `qokeol`
steht `ctheol` mit MATERIAL|MIDDLE_STAGE; auf der anderen Seite von `okeol`
liegt `otey` mit COLD|PREPARATION|MIDDLE_STAGE. Der Vorbereitungshinweis wird
aber erst am fünften Außenplatz erreicht und das Feld bleibt dort
radius-zensiert. Deshalb ist dies ein guter Folgehinweis, aber keine aktive
Karte.

Das ist keine endgültige Widerlegung der Arbeitshypothese. Es ist die klare
Grenze zwischen „weiter untersuchen“ und „bereits in die Übersetzung
schreiben“.

## Konkrete Renderer-Korrektur

Alle zehn GDT751-Karten `heiße Zubereitung an der End-/Vollstufe` besitzen
null unabhängige, vollständige Außenfeldbestätigungen für den Träger
`PREPARATION`. Ihre robustere GDT750-Information bleibt jedoch erhalten:

> **heiß an der End-/Vollstufe; Trägerrolle offen**

`Zubereitung` wird nicht gelöscht, sondern als explorative Hintergrundannahme
geführt. Es wird nur nicht mehr als bereits gewonnene Übersetzungsinformation
ausgesprochen. Die drei übrigen `qokeey/okeey`-Kontakte erhalten weiterhin
keine zusätzliche Karte.

## Was weiterhin gilt

GDT751s schwache komplette Paarbeziehung bleibt bestehen: 44 direkte Kontakte
von zwölf q/Basis-Paartypen bei erhöhter Kontaktdichte. GDT752 prüft nicht, ob
die Formen zusammengehören, sondern ob sie **diese eine konkrete
Rollenaufteilung** tragen. Dafür lautet die Antwort derzeit nein.

EVA q erhält weiterhin keinen Buchstaben-, Laut-, Präfix-, Morphem-,
Abkürzungs-, Teilstring- oder Wortwert. Auch die historischen Feldnamen sind
Arbeitsrollen, keine entschlüsselten Lexeme.

## Nächster sinnvoller Schritt

Der knappste verbleibende positive Hinweis ist das vollständige Formpaar
`qokeol/okeol`: 34 beziehungsweise 41 reader-exakte Vorkommen, zwei direkte
Kontakte und der eine abgeschnittene gerichtete Außenfeldtreffer. Der nächste
Test sollte alle Vorkommen beider Ganzformen target-zentriert vergleichen und
fragen, ob `qokeol` wiederholt Prozess/Material plus Mittelstufe trägt, während
`okeol` wiederholt eine Zubereitungsrolle trägt. Die gleichen Schnitte müssen
auf frequenzähnliche q/Basis- und Nicht-q-Paare angewandt werden. Erst eine
seitenübergreifende Wiederholung würde eine konkrete Ganzformbedeutung
rechtfertigen.

## Reproduktion

```bash
python3 experiments/yolo/gdt752_q_base_microfield_role_audit/src/run.py
python3 experiments/yolo/gdt752_q_base_microfield_role_audit/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt752_q_base_microfield_role_audit/artifacts/GDT752_GDT388_SIDE_ROLE_EDGE_PACKET.tsv
```

Der Validator besteht 1.895 Prüfungen und reproduziert alle neun erzeugten
Artefakte byte-identisch. Das einzelne symmetrische Relationselement bleibt
erwartungsgemäß `INVALID_PACKET` und nicht score-ready.
