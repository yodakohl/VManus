# GDT591 — Das Körper/Station-Modell hält als Badeepisode

## Ergebnis

Die GDT590-Trennung hält auch oberhalb des Einzelhosts. Die 92 Y-Badehosts
verteilen sich auf 64 Aussagen und 17 physische ZL3b-Absätze. Alle 14
Körper/Station-Wechsel innerhalb einer Aussage geschehen an einem neuen
SH-Gouverneur; auf der Körperseite fehlt ausnahmslos ein Blocker, auf der
Stationsseite ist ausnahmslos einer sichtbar.

Das macht die Arbeitslesung nicht wahr, aber deutlich weniger beliebig: Der
Leser wechselt sein Badeobjekt nicht wegen der gewünschten deutschen Phrase,
sondern an einer sichtbaren formalen Grenze.

## Vollständiger Bestand

| Ebene | Bestand | Übergänge | Rollenwechsel |
|---|---:|---:|---:|
| Host | 92: 52 Körper, 40 Station | – | kein Host mischt Rollen |
| Aussage | 64 | 28 | 14 |
| physischer Absatz | 17 | 75 | 35 |

Die 112 geschriebenen Y-Slots teilen sich in 55 Körper- und 57
Stationspositionen. Alle 127 Carrier bleiben sichtbar: 88 stehen im
Ankerereignis, 39 in einem anderen Quellereignis als der Aktionsanker. Die 28
aussageinternen Folgen lauten:

- Körper→Körper: 10;
- Station→Station: 4;
- Körper→Station: 7;
- Station→Körper: 7.

Sie bleiben sämtlich im selben physischen Absatz. Sieben der 14 Rollenwechsel
haben zusätzlich mindestens einen zwischenliegenden Kontrollhost: fünf mit
`OL`, zwei mit
`OT`. Zwei überschreiten eine alte Lesergrenze, aber keine physische
Absatzgrenze. Absatzweit entstehen 25 Körper→Körper, 15 Station→Station, 17
Körper→Station und 18 Station→Körper. Von 35 Absatzwechseln liegen 14 innerhalb
und 21 zwischen Aussagen.

## Was `remote` tatsächlich bedeutet

Die 39 remote Carrier verteilen sich auf 27 Hosts und auf `Y×25`, `AIIN×6`,
`AIN×4`, `OR×4`. Ihre Geometrien sind 19-mal `PREVIOUS_CARD_ACTION`, zwölfmal
`INHERITED_ACTION` und achtmal ein begrenzter Ein-Karten-Lookahead. Alle 39
behalten exakt ihren GDT581-Gouverneur und überschreiten weder Owner noch
Aussage.

Damit war die bisherige Kurzform „entferntes Y“ bei E2652 irreführend. Remote
heißt hier ausschließlich: nicht im selben Quellereignis wie der
Aktionsanker geschrieben; ein anderer Slot allein genügt nicht.

## E2652: stärker, aber nicht geschlossen

Die vollständige Spur lautet:

```text
E2650@2  Y=Stationsansatz      → Owner-Rahmen auf f77r.40
E2651@1  AIIN=Badfüllung       → bounded-next zu ACTION:E2652:SH
E2652@1  SH                    → Aktionsanker
E2653@2  Y=Körper              → previous-card zu ACTION:E2652:SH
```

Auf dem Blatt stehen die letzten drei Teile unmittelbar als
`daiin – sh – qolchey`, f77r.41 W1–W3. Die grammatische Anhängung ist also
ereignisfern, die sichtbare Sequenz aber kompakt. Das stützt die Lesung:

> Verwende für den vorangehenden Arbeitsschritt den Stationsansatz. Halte den
> Körper im Bad bei der angegebenen Füllung. Fahre im selben Arbeitsgang fort.

Der Haken bleibt real: Unter allen 953 vollständigen GDT589-Hosts kommt die
Kombination `AIIN|SH|Y` mit nur `SH` als direktem Gouverneurtoken genau einmal
vor. Keiner der sechs Teilvergleiche reproduziert den gesamten Aufbau. Deshalb
steigt Körper-first von der schwächsten explorativen GDT590-Stelle zu einer
mittleren Arbeitslesung, nicht zu einem geschlossenen Befund. Die Fortsetzung
des Stationsreferenten über `OL+Y` bleibt die stärkste Gegenlesung.

## Gut lesbare Episoden

Neun Aussagen enthalten beide Rollen. Besonders nützlich sind:

- S382: Körper+Badfüllung → L-geblockte Station;
- S495: stark geblockte Station → Körper+Badfüllung → Körper;
- S392: Körper → Station → Körper → Station, wobei beide Stationsphasen ihre
  eigenen Blocker tragen;
- S119: neun Badehosts mit mehreren Wechseln, ohne eine einzige Umkehr der
  Blockerregel.

Die vollständigen deutschen Arbeitsfassungen stehen in
`artifacts/GDT591_BATH_EPISODE_READER.md`.

## Umfang und nächster sinnvoller Pass

GDT591 ändert null Slots und null Aussagen; es ordnet nur die bereits gewählte
Lesung in Episoden. Der nächste produktive Schritt ist deshalb nicht noch ein
E2652-Rundlauf, sondern die 254 Badeaktionen vollständig mit einem
Arbeitsobjekt zu versehen: zuerst geschriebener Körper/Stationsansatz, danach
episodisch fortgetragenes Objekt und nur bei fehlendem Kontext ein neutrales
`Badeobjekt`. Das kann die bisher 149 objektlosen Badeaktionen füllen, ohne
neue Seiten oder Wurzeln zu öffnen.

## Behauptungsgrenze

Die Episode ist eine kohärente Werkstattlektüre, keine bestätigte
Bildchronologie. Es gibt weiterhin null bestätigte Voynich-Lexeme und keinen
bestätigten Klartext. Insbesondere folgen weder Patient, Anatomie, Stoff,
Krankheit, Heilung, historische Quelle noch Sprache aus diesem Pass.

Validierung: 83/83 Prüfungen grün, einschließlich byte-identischem Neubau der
zehn erzeugten Ergebnisartefakte.
