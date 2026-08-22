# V39 R1 — Prüfung des gemeinsamen Zwölf-Karten-Lehrdecks

## Rolle und Grenze

Ich behandle das Material wie ein Werkstattlehrmeister um 1420: Eine Karte
muss kopierbar, im Ablauf verwendbar und von einem zweiten Schreiber
zurücklesbar sein. Das ist eine absichtlich konkrete Sidequest-Rekonstruktion,
keine Entzifferung. Grundlage sind ausschließlich die zehn freigegebenen
Seiten, die zwölf handübergreifenden exakten Karten aus V38 und deren
V25-Kontexte. `f84` und `f84r` blieben versiegelt.

## Hauptergebnis

Das Zwölf-Karten-Deck bleibt als Lehrkern brauchbar, aber V38 war an drei
Stellen unnötig eng:

1. `otchey` bedeutet besser **NIMM DEN BEZEICHNETEN TEIL** als „nimm den
   letzten Anteil“. Beide Belege sind feldinitial; nur einer bezeichnet einen
   Endanteil, der andere leitet Temperieren und Anwenden ein.
2. `dal` bedeutet besser **BRINGE ES AN DIE BEZEICHNETE STELLE** als bloß
   „anwenden“. Seine Kontexte umfassen Öffnung, unteren Ablauf und Becken. Die
   Karte kann örtliche Zufuhr bezeichnen, ohne jede Stelle als Körperstelle zu
   erzwingen.
3. `daiin` wird als **EIN VORGESCHRIEBENES MASS** gelehrt. Das ist konkreter
   und zugleich weiter als „in der üblichen Menge“: Die Karte kann neben einer
   Portion, Zutat, Öffnung oder Behandlung stehen und muss keine Präposition
   kodieren.

`char` wird entsprechend als rückweisendes **DARAUS, AUS DEMSELBEN ANSATZ**
gelehrt. Das vermeidet die Behauptung, jede seiner fünf Stellen bezeichne eine
eigenständige neue Charge.

## Warum die übrigen acht Defaultwerte stehen bleiben

- `chol` und `cholor` bilden ein plausibles kurzes/langes Vorbezugs-Paar. Das
  kurze `chol` ist häufig und frei einsetzbar; das seltene `cholor` kann den
  vorherigen Ansatz ausdrücklich wieder aufnehmen.
- `dy` ist so breit verteilt, dass **DIESE PORTION** als deiktische
  Werkstattkarte besser passt als ein Stoffname.
- `oky` steht bei Pflaster, Bad, Spülung und unmittelbarem Gebrauch. **WENDE
  DIESE PORTION AN** deckt diesen gemeinsamen Vollzug ab.
- `chor` erscheint als `chor/shor/or/sor` in Pflanzen- und Badeabläufen.
  **ZUBEREITETER SUD / ARBEITSFLÜSSIGKEIT** ist ein lehrbarer gemeinsamer
  Nenner; die Wrapper sind keine neuen Bedeutungen.
- `cthy`, `shey` und `chty` bilden ein plausibles kleines Zustandsdreieck:
  bereit, klar, gleichmäßig. Ihre Werte bleiben konkret, aber rivalisierende
  Zeit-, Abschluss- und Mischlesungen bleiben offen.

## Lehrbarer Encoder

Der Lehrling arbeitet nicht buchstabenweise, sondern mit Musterkarten.

1. **Stummen Eigentümer setzen:** Bild, Artikel oder vorheriger Arbeitsschritt
   liefert Pflanze, Körperstelle, Gefäß und bereits eingeführten Ansatz.
2. **Absicht in Karten zerlegen:** NIMM / MASS / VORBEZUG / SUD / ZUSTAND /
   VOLLZUG / ORT. Für jeden dieser Werte wird ausschließlich die exakte
   Karten-ID aus `V39_R1_SHARED_CARD_LEXICON.tsv` gewählt.
3. **Felder bauen:** Ein Feld enthält gewöhnlich einen neuen Auftrag plus seine
   Ergänzungen. Zustandskarten folgen dem betroffenen Ansatz; örtliche
   Vollzugskarten stehen gegen Feldende.
4. **Oberflächenform kopieren:** Der Schreiber nimmt eine für Hand und Register
   bereits belegte Realisierung der exakten Karte. `chor`, `shor`, `or` und
   `sor` bleiben dieselbe Karte; ebenso etwa `dy/chy/shy/y/sy/chey`.
5. **Schließen:** Das letzte Inhaltswort ist nicht automatisch Satzzeichen.
   Feldgrenze, DY/B3-Schluss und physischer Zeilenumbruch werden aus dem
   passenden Exemplar kopiert. Eine Aussage darf über die Zeile weiterlaufen.
6. **Keine freie Erfindung:** Fehlt eine Karte, wird sie aus dem lokalen
   Exemplar übernommen; der Lehrling baut keine unbekannte Form aus vermeintlichen
   Präfixen oder Suffixen.

## Lehrbarer Decoder

1. Sichtbare Gruppen nach der vorhandenen Tabelle in **exakte Karten-IDs**
   zurückführen; Wrapper nicht als eigenes Wort übersetzen.
2. Jede bekannte Kernkarte zunächst mit genau ihrem Defaultwert lesen.
3. `dies`, `daraus`, `vorherig` und `bezeichnet` auf den nächsten verfügbaren
   Eigentümer auflösen: zuerst laufendes Feld, dann vorheriges Feld, dann Bild.
4. Feldgrenzen als Arbeitsgliederung lesen; physische Zeilenenden nur als
   Platz-/Kopiergrenzen behandeln.
5. Einen Rivalen nur einsetzen, wenn der Default einen konkreten lokalen
   Widerspruch erzeugt. Der Randvermerk nennt dann Karte, Rivalen und Grund;
   die Kartenbedeutung wird nicht stillschweigend geändert.
6. Rückleseprobe: Ein zweiter Schreiber muss aus den Karten dieselbe Folge von
   Werkstattaufträgen gewinnen, auch wenn er die lateinische oder volkssprachige
   Ausgangsform nicht kennt.

## Ergebnis der Dreifeldprobe

Die revidierte Folge verwendet alle zwölf Karten genau einmal, jede in einer
V38-belegten Feldposition:

```text
otchey daiin | chol chor char chty shey | cholor dy cthy oky dal
```

Flüssige deutsche Rücklesung:

> Nimm vom bezeichneten Teil ein vorgeschriebenes Maß. Setze es mit der
> vorigen Zubereitung zum Arbeitssud an; bearbeite daraus alles gleichmäßig,
> bis die Flüssigkeit klar läuft. Nimm aus dem vorherigen Ansatz diese Portion;
> sobald sie bereit ist, wende sie an der bezeichneten Stelle an.

Diese Anweisung ist absichtlich allgemein: Bild und Artikel liefern Stoff und
Ort. Sie ist aber ausführbar, lernbar und ohne neue Karte rücklesbar.

## Verbleibende Schwäche

Das Deck ist durch Hand **und** Register ausgewählt; auf den zehn Seiten sind
diese Faktoren stark gekoppelt. Ein gemeinsamer Werkstattkern ist daher eine
gute Rekonstruktion, aber nicht bewiesen. Besonders `chol`/`cholor` und
`cthy`/`chty` könnten statt semantischer Paarungen formale Registervarianten
oder feste Phrasenkarten sein. Das Lehrmodell hält deshalb pro Karte zwei
konkrete Rivalen sichtbar.
