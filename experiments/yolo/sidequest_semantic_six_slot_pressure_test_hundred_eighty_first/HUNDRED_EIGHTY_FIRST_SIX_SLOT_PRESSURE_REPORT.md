# Hunderteinundachtzigste Runde: die sechs Slots tragen alle 116 Aussagen

Der grosse Ruecklauf benoetigt keinen siebten Bedeutungsplatz. Alle 381 Kartenereignisse in allen 135
Feldern und 116 Aussagen lassen sich als Quelle/Kontext, Auswahl/Mass, Zustand/Station,
Vorgang/Kontakt, Ziel/Reihenfolge oder Freigabe/Schluss lesen.

Die einfache Pfeilkette aus Runde 180 war aber noch zu starr. Die Korrektur ist klein und
werkstattpraktisch: Ein langes Feld darf mehrere **Mikro-Arbeitspakete** enthalten.

## Revidierte Satzmaschine

`AUSSAGE := FELD+`

`FELD := MIKROPAKET+ [G6]`

Ein Mikropaket bindet Quelle und Teilcharge, setzt bei Bedarf einen Zustand, fuehrt einen Vorgang an
einer Zielstelle aus und gibt den Zustand zurueck. G1/G2 bilden ein flexibles Adressbuendel. G3 darf
vor oder nach dem Vorgang stehen. G4 und G5 duerfen tauschen. Taucht nach begonnenem Vorgang erneut
G1 oder G2 auf, startet ein weiterer Teilvorgang mit demselben aktiven Ansatz.

## Ergebnis in Zahlen

- 107 von 135 Feldern brauchen nur ein Mikropaket;
- 24 brauchen zwei, zwei brauchen drei und zwei brauchen vier;
- zusammen entstehen 169 Mikropakete und 34 sichtbare Rueckspruenge zu Quelle oder Teilcharge;
- dreizehnmal steht das Ziel vor dem zugehoerigen Vorgang;
- alle 89 Schlussrollen stehen wirklich am Ende ihres Feldes;
- die vier Register aus Runde 180 reichen weiterhin.

Die schwierigsten Felder sind keine Gegenbeispiele, sondern auf engem Raum zusammengedrueckte
Arbeitsketten. `H1-S001` schaltet viermal zwischen Stoffauswahl und Bearbeitung. `B1-S002` tut dies in
zwei Feldern mit vier beziehungsweise drei Mikropaketen. Ein Schreiber braucht dafuer kein neues
Wortglied, sondern nur die Regel „nach einem Vorgang darf eine neue Portion desselben Ansatzes
aufgerufen werden“.

## Neue praktische Lesung

Die Kartenfolge verhaelt sich damit eher wie ein kompaktes Arbeitsprotokoll als wie ein fortlaufender
Satz. Ein Feld kann lauten: *Posten – Handlung – Quelle – Handlung – neue Teilcharge – Ziel –
Handlung*. Das ist nicht chaotisch, solange Ansatz, Teilcharge, Ziel und Station als laufende Register
erhalten bleiben.

Der naechste Schritt sollte diese Grammatik produktiv ausnutzen: eine dritte, deutlich laengere
Anweisung mit zwei Mikropaketen innerhalb desselben Feldes schreiben. Sie muss Quelle und Portion
nach einem begonnenen Vorgang wiederaufnehmen, ohne eine neue Karte oder Bedeutung einzufuehren.
