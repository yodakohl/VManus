# GDT727 — V99 six meaning debt dispatch

## Ergebnis

GDT727 besteht. Alle sechs offenen GDT726-Bedeutungsgruppen haben jetzt einen
ausgabefähigen Default. Fünf Ganzwortkerne wechseln von `Dosis/Dosen` zu
`Portion/Portionen`; 13 Positionswerte und dadurch neun der 51 Leserzeilen
ändern sich. 479 Positionen werden weiterhin genau einmal in 471 sichtbaren
Einheiten verbraucht. Scores, Scopes und Komponentenexport bleiben unverändert.

Die wichtigsten neuen Ausgaben sind:

- `ychedaiin`: drei Portionen der bis zur Mittelstufe getrockneten Droge
  abmessen.
- `kodeey`: vollständig erhitzte, fertige Portion der Zubereitung.
- `cpheesy`: vollständig bereitetes und abgeschlossenes Gemisch.
- `tail`: kaltgestellter Materialanteil II.
- `ypchesy` auf f86v5.4: das Samenpulver aus dem vorstehenden kalten Ansatz,
  Grad II, bis zur Mittelstufe trocknen.
- `yteedy` auf f86v6.25: den soeben abgeseihten heißen Drogenanteil I bis zur
  Endstufe abkühlen.

Auf f80r.17 wird `sheky` dreimal als dieselbe Handlung gelesen, aber nicht als
„dreimal“: zuerst an der feuchten Mischung, dann am heißen Drogenanteil I und
schließlich am heißen Holzanteil I im Ansatz auf Grad II.

## Warum die BOS-Lesungen jetzt besser sind

Die 51 ausgewählten Zeilen sind kein lückenloser Manuskriptauszug. Deshalb war
der vorherige Deck-Vorgänger als Rückbezugsziel falsch. GDT727 liest die vier
echten physischen Vorgänger. P002 und P142 sind zu lückenhaft beziehungsweise
semantisch zu gemischt und verlieren `hiervon`. f86v5.3 endet dagegen in
`otaiin otain` (kalter Ansatz Grad III/II), f86v6.24 in `qokar oly` (heißer
Drogenanteil I, abseihen); diese beiden Anschlüsse werden lokal sichtbar.

## Wörterbuchzustand

`V99_COMPLETE_WORD_CONFIDENCE.tsv` enthält weiterhin alle 1.586 Readings mit
Score, Confidence-Stufe, positiver Evidenz und Gegenbeleg. Zehn aktive
Lexikrecords erhalten neue Kontextaggregate; nur fünf davon ändern ihren
portablen Kern. Ältere globale V48-Einträge außerhalb der aktiven 51-Zeilen-
Tranche behalten vorerst ihre geerbten Dosisformulierungen. Sie sind der
nächste sinnvolle Familientest, nicht etwas, das still per Textersetzung
umgeschrieben werden sollte.

## Nächster Schritt

GDT728 soll alle geerbten Dosis-/Dosen-Ganzwörter des vollständigen
Wörterbuchs als eine Familie inventarisieren. Ziel ist eine vorhersehbare
Trennung zwischen `Portion`, `Teil`, `Maß` und nacktem `Wert`, bevor V99 auf
weitere Seiten angewendet wird.
