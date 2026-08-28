# GDT591 — Methode

## Frage

Bleibt die in GDT590 gewählte Trennung `blockerfreies Y-Bad = Körper` gegen
`geblocktes Y-Bad = Stationsansatz` auch dann lesbar, wenn nicht nur einzelne
Hosts, sondern ganze Aussagen und physische Absätze als Badeepisoden verfolgt
werden? Insbesondere: Ist das formal ungewöhnliche E2652 nur wegen einer
missverständlichen Fernanhängung schwach, oder bricht es die Arbeitsregel?

## Feste Population und Eingaben

Die Zielpopulation sind exakt die 92 Y-tragenden `SH_BIO_BATHE`-Hosts aus
GDT590 auf f75r, f77r, f81r, f81v, f82r und f83r. Ihre Rollen, Blocker,
Gouverneure, Slots und 793-Aussagen-Lesung bleiben eingefroren. GDT587 liefert
die vollständigen Carrier-Zuweisungen, GDT581 die unveränderte
Anhängungsgeometrie und Slotgrenzen, GDT515 die Ereignisorte und die beiden
ZL3b-Tabellen physische Zeilen, Absatzanfänge und Layoutunterbrechungen.

Für die exakte E2652-Signatur wird die vollständige bereits zugelassene
GDT589-Population von 953 Hosts geladen. Die Auswahl erfolgt vor dem
Materialisieren über den geschützten Seiten-Selector; f84 und f84r bleiben
gesperrt. Keine neue Seite, Bilddatei, Oberfläche, Wurzel, Segmentierung oder
Leserregel wird geöffnet.

## Methode

Die 92 Hosts werden zuerst nach ihrer festen Hostposition innerhalb der
Aussage und getrennt nach ihrer physischen ZL3b-Absatzposition geordnet. Für
jedes benachbarte Paar werden Körper/Station, Blockerzustand, neuer Gouverneur,
zwischenliegende `OL`/`OT`-Kontrollen und etwaige alte Lesergrenzen ausgegeben.
Eine alte Lesergrenze wird ausdrücklich nicht mit einem sichtbaren
Manuskriptabsatz gleichgesetzt.

Carrier heißen hier `remote`, wenn ihr geschriebenes Quellereignis nicht das
Aktionsanker-Ereignis ist. Ein anderer Slot im selben Ereignis reicht dafür
nicht. Das ist Ereignisferne, keine Aussage über den Abstand auf dem Blatt.
Jeder dieser Slots wird auf seine einzelne
GDT581-Anhängung zurückgeführt; Gouverneur, Lookahead sowie Owner- und
Aussagegrenze dürfen nicht verändert werden.

E2652 wird zusätzlich gegen alle 953 vollständigen Hosts über die exakt
geschriebene Signatur `complete_host_values_written=AIIN|SH|Y` plus
`direct_governor_tokens=SH` geprüft. Teilvergleiche bleiben als solche
gekennzeichnet. Die vier GDT590-Ziele werden außerdem mit ihrer bereits
geprüften Layoutspur in einen kompakten Episodenleser übernommen.

## Entscheidungsregel und Behauptungsgrenze

Der Pass gilt als konsistent, wenn alle Rollenwechsel innerhalb einer Aussage
an neuen SH-Gouverneuren liegen und der Blockerzustand immer mit der Rolle
wechselt. Ein Wechsel beweist keine Bildchronologie; er zeigt nur, dass das
Arbeitsmodell ganze Sequenzen ohne willkürliche hostinterne Umdeutung lesen
kann. E2652 darf als Körper-first gestärkt werden, wenn seine Carrier physisch
kompakt und grammatisch korrekt gebunden sind. Ohne exakten Vergleichshost
bleibt `Stationsansatz` dennoch sichtbar.

GDT591 ändert kein Lemma und keine der 793 Aussagen. Es bestätigt kein
Voynich-Wort, keinen Stamm, Klartext, Patienten, Körperteil, Stoff, Prozess,
Krankheit, Heilung, historische Quelle oder Sprachsyntax. Die Tabellen sind
eine ausführbare Arbeitslesung, nicht unabhängige Denotationsevidenz.
