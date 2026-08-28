# GDT590 — Methode

## Frage

Soll bei den vier bereits von GDT589 vollständig enumerierten, blockerfreien
`SH_BIO_BATHE`-Hosts mit geschriebenem Y und AIIN `Y` zuerst als Körper oder
als Stationsansatz gelesen werden? Hält die Wahl im vollständigen Host, in der
ganzen Aussage und im bestehenden 30-Seiten-Reader?

## Feste Population und Eingaben

Die Zielmenge ist vollständig und besteht nur aus G407-E2404, E2637, E2652 und
E3182 auf den bereits zugelassenen Seiten f77r und f82r. GDT589 liefert alle
953 Hosts, 1.243 geordneten Slots, 361 Biological-Y-Guards, 74 Sonderpackets
und 793 laufenden Aussagen. GDT515 liefert die unveränderten Events; ZL3b und
GDT242 liefern Zeilen- und Absatzkoordinaten.

Für den separaten Bildpass werden offizielle Yale-IIIF-Kopien von f77r und
f82r mit URL, Pixelmaß und SHA-256 in `sources/gdt590_manual_image_sources.tsv`
gebunden. Das layoutbewusste ZL3b-Artefakt liefert insbesondere den Bruch nach
Wort 4 auf f82r.1. Die exakten menschlichen Grafikannotationen dienen nur dem
Negativabgleich: Keines der vier Ziele ist ein Figuren- oder Objektlabel.

Keine neue Seite, OCR, Segmentierung, Rootzerlegung, Grammatikregel oder
enthaltene Teilzeichenfolge wird geöffnet.

## Vollhostregel

Ein Y wird am bestehenden Biological-Host als Körper gelesen, wenn:

1. die feste Aktionsregel `SH_BIO_BATHE` ist;
2. mindestens ein Y geschrieben ist;
3. alle geschriebenen Carrier Y oder AIIN sind; und
4. kein Relations-, Form- oder Adressblocker vorliegt.

Jede Y-Position bleibt einzeln `Körper`, jede AIIN-Position bleibt
`Badfüllung`; Reihenfolge und Multiplizität verschwinden nicht. AIIN ist damit
eine zusätzliche Füllung, kein Grund, ein sonst blockerfreies Badeobjekt zur
Station umzudeuten. Die Regel umfasst im vorhandenen Bestand 48 schon vorher
als Körper gelesene Hosts und genau die vier Restgabeln. Die 40 geblockten
Y-Badehosts bleiben Station.

## Vier Evidenzebenen

Für jeden Zielhost werden getrennt gespeichert:

- vollständige Carrierfolge, Slot-IDs und Blocker;
- ganze Aussage mit vor- und nachfolgenden Handlungen;
- Minimalpaare innerhalb aller 92 Y-Badehosts und aller elf
  `BIOLOGICAL_BATH_FILL`-Packets;
- manuelle Bildnähe auf der exakten Prosa- und Wortposition.

Die Rangfolge der Arbeitsentscheidung ist vollständiger Host und Blocker,
danach Satzfolge und Minimalpaar, zuletzt Bildnähe. Ein Bild darf ohne
Wort-Figur-Zeiger keine Denotation erzwingen. Deshalb kann das Gesamtmodell
Körper wählen, obwohl drei Wortpositionen bildlich leicht zur Apparatur neigen.

## Vollständiger Replay

Nur die vier Y-Slots werden `Stationsansatz → Körper` umgestellt. Die vier
AIIN-Slots bleiben `Badfüllung`. Danach werden exakt vier Klauseln im
793-Aussagen-Leser ersetzt. Alle alten GDT589-Spalten, Repeat-Overlays und 789
nicht betroffenen Leser bleiben bytegleich. Ein Neubau muss alle neun
erzeugten Artefakte byteidentisch reproduzieren.

## Behauptungsgrenze

Das Ergebnis ist eine occurrence- und aktionsgebundene deutsche
Arbeitsbedeutung. Es macht Y nicht global zu einem Voynich-Wort für Körper und
bestätigt weder Klartext, Sprache, Patient, Anatomie, Stoff, Verfahren,
Krankheit, Heilung, historisches Codebook noch eine neue Seite. E2652 bleibt
wegen seines einzigartigen bloßen SH und des entfernten Y-Trägers der offenste
Fall; Stationsansatz bleibt bei allen vier sichtbar.
