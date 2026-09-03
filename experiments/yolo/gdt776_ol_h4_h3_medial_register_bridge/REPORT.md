# GDT776 — mediales `ol` gegen H3/H4-Feldstruktur

Status: `PASS__H4_LEANING_HEURISTIC__INTERNAL_LATE_FIELD_BRIDGE__149_CONTEXTUAL__NO_PLAINTEXT`.

## Ergebnis

Der hash-gesperrte, über GDT769 bewachte Lauf bestätigt **183** mediale
`ol`-Zielkanten. Die vollständigen reader-exakten Kontrollen umfassen **102
H3-** und **350 H4-Kanten**. H4 führt gepoolt
(0.537863 gegen 0.376871), nach
Oberflächen-Ausgleich (0.417966 gegen
0.344710) und in 23 gemeinsam getragenen
Register×Ordinal-Strata (0.352534 gegen
0.205856). Das ist eine **H4-neigende strukturelle
Heuristik**, keine H4- oder Operator-Bedeutung.

Die schärfere Prüfung begrenzt die Deutung. Auf 18 gemeinsam aktiven bodies
führt H4 roh (0.407909 gegen
0.348869), doch nach body-Ausgleich kehrt sich die
Reihenfolge zu H3 um (0.304845 gegen
0.245539). Im strengsten identischen
body×Register×Ordinal-Kapazitätsview bleiben 9 bodies, 13 Zellen und 73
Zielkanten; der H4-Vorsprung beträgt nur
+0.034821 und ist im Zell-Labeltausch nicht
trennend. Die symmetrische Entfernung aller `o...`-bodies lässt nach
Oberflächen-Ausgleich einen kleinen H4-Vorsprung von
+0.019229. Gewählt wird daher der breitere
**internal/late record-field bridge**, nicht eine automatische
`FIELD_OPERATOR`-Semantik.

## Renderer und Wörterbuch

Die 25 vorab festgelegten wiederkehrenden rechten Ganzwörter decken 89 der 183
Zielkanten ab. Der GDT775-Durchsatz steigt von **123 auf 149** kontextuelle
Ausgaben. Die 26 neuen Ausgaben bestehen aus sieben nicht konsumierenden
`ol ol`-Kettengliedern und 19 neuen konsumierenden Ganzwortspannen. Zusammen
mit den 74 geerbten Spannen werden genau **93** rechte Token einmalig
konsumiert. Jede Ganzwortkarte nennt Lesart, Konfidenz, positive Evidenz und
Gegenevidenz; keine Karte exportiert freie EVA-Komponenten oder Klartext.

Alle 26 neu kontextualisierten Ausgaben sind C0/C1 statt C2; vierzehn sind
ausdrückliche Feld-/Strukturlesarten (`ol ol`, `ol r`, `ol dy`, `ol s`). Der
Gewinn ist daher eine schärfere Spangrammatik, nicht 26 entschlüsselte
Inhaltswörter. Insbesondere hält GDT759 außerhalb von Wertausdrücken für `s`
den Mengen-/Einheitsrivalen offen. Der nächste Komponierer muss deshalb das
folgende Wert- oder Zustandswort mitbinden, bevor er Mengenbezug und
H2-Unterposten trennt.

## Zieltyp-Sensitivität

- `BASELINE`: n=183; raw Δ(H4-H3)=+0.160992; surface-equalized Δ=+0.073256.
- `DROP_DAIIN`: n=179; raw Δ(H4-H3)=+0.140967; surface-equalized Δ=+0.016201.
- `DROP_FIXED_13`: n=125; raw Δ(H4-H3)=+0.067850; surface-equalized Δ=-0.086973.
- `DROP_NEW_10`: n=157; raw Δ(H4-H3)=+0.175918; surface-equalized Δ=+0.168926.
- `DROP_RECURRENT_25`: n=94; raw Δ(H4-H3)=+0.060445; surface-equalized Δ=+0.025876.

Der feste GDT775-13er-Drop dreht die oberflächen-ausgeglichene Führung zu H3;
gepoolt bleibt H4 in allen Drops vorn. Diese Zieltyp-Sensitivität und die
body-ausgeglichene Umkehr sind bindende Interpretationslimits.

## Drei praktische Passage-Patches

- `f79r.41`: `qokain shedy qotain oteedy chkain ol ol chedy oly`
  → qokain shedy qotain oteedy chkain ⟦Unterfeld: weiterer Ansatz⟧ ⟦Zustand: getrocknetes Ergebnis, Form I⟧ oly

- `f80r.52`: `sol tl shey qoklcheey lkaiin ol olor aiin y daiin cheol kain`
  → sol tl shey qoklcheey lkaiin ⟦Zutatenportion⟧ aiin y daiin cheol kain

- `f99v.34`: `yoiin ol ol olaiin qockhey qokol olshy qokeeor or aiin doldam`
  → yoiin ⟦Unterfeld: weiterer Ansatz⟧ ⟦Materialangabe: Stoff, Wert III⟧ qockhey qokol olshy qokeeor or aiin doldam

Die Doppelklammern markieren ersetzbare Ganzwort-/Spannenlesarten; übriges EVA
bleibt ausdrücklich ungelöst. Das sind keine übersetzten Sätze.

## GDT388-Grenze

Das Paket enthält 183+102+350 = **635** Transkriptionskanten. Alle sind als
`INELIGIBLE_EXPLORATORY_TEXT_RELATION` markiert. Der Intake lautet
`VALID_ACQUISITION_NOT_SCORE_READY`; weder Kapazitäts-, Holdout- noch
Mobile-null-Gate ist score-ready. Es wurden keine neuen Seiten, Bilder, OCR,
Transkriptionen, `f84`- oder `f84r`-Daten geöffnet.
