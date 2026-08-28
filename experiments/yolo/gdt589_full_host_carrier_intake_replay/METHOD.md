# GDT589 — Methode

## Frage

Kann der in GDT588 veröffentlichte Vollhost-Intake alle 953 bekannten
GDT587-Carrier-Hosts samt Gate, Regel, geordneter Rootfolge, Nomenformen,
Packet und Wiederholungen wiedergeben? Welche Anzeige- oder Routinglücken
werden erst im vollständigen Replay sichtbar?

## Feste Eingaben

- GDT582s vollständiges Ledger liefert alle Slotwerte eines Governors;
- GDT584 liefert die eindeutige Aktionszeile, direkten Tokens, sichtbare
  Vor-/Nachhandlung, GDT583-Elternregel und gegebenenfalls manuelle Regel;
- GDT587 liefert die 1.243 geordneten Carrier-Assignments und die bestehende
  flüssige Hostlesung;
- GDT588 liefert Gate-Klassen, die beiden vollständigen Leser und die 13
  bereits markierten Sonderpacket-Wiederholungen.

Keine neue Seite, Bilddekodierung, OCR, Surface-Segmentierung oder
Substring-Zerlegung wird verwendet. `primary_governor_key`, nicht Event-ID,
ist die Hostgrenze; 289 Hosts reichen über mehrere Source-Events.

## Vollhost-Rekonstruktion

Für jeden Governor werden alle GDT582-Zeilen in Ledgerreihenfolge gesammelt.
Carrier sind exakt die dazugehörigen GDT587-Assignments in
`assignment_ordinal`-Reihenfolge. Wiederholte Roots bleiben als getrennte
Slots erhalten. Der Host wird danach in drei Klassen geroutet:

1. `AUTO_CONTEXT`: GDT588 wählt aus dem vollständigen Host eine portable
   GDT583-Regel und die gebundenen GDT587-Nomen.
2. `MANUAL_GDT584_OVERRIDE`: der portable Elternweg und der explizite alte
   manuelle Weg werden nebeneinander ausgegeben. Direkter Eltern-Nomensinn
   und konservativer Runtime-Fallback bleiben getrennt.
3. `SOURCE_ID_BOUND`: die alte ID-Regel muss abgewiesen werden; anschließend
   wird mit neutraler Zukunfts-ID der portable Fallthrough ausgeführt.

Ein automatischer Host gilt nur dann als exakt, wenn Regel, Slotzahl,
Carrier-Root, Reihenfolge, Kontextfamilie, Lemma, Objekt-/Genitivform und
Packet übereinstimmen. Manuelle und source-gebundene Fälle werden nicht in die
Automatikquote hineingerechnet.

## Drei Anzeigeebenen

Ein Carrier-Slotlemma ist nicht immer identisch mit der fertigen
Packet-Komposition. Deshalb werden getrennt gespeichert:

- die ordinale schriftliche Spur, etwa `OR–Y–OR`;
- kompositionelle Packet-Elemente, einschließlich eines vom Verb gelieferten
  Kopfes wie `Auszug`;
- der flüssige deutsche Arbeitssatz.

Alle 117 Repeat-Hosts erhalten eine ordinale Spur und zusätzlich ein Multiset.
Der flüssige GDT587-Satz bleibt dabei erhalten. Das korrigiert zugleich die
13 GDT588-Klammerformulierungen, deren `×N` nicht als Realobjektzahl gelesen
werden darf und bei neun Sätzen eine sichtbare Relation verarmte.

## Explorative Semantikgabel

Beim Packet `BIOLOGICAL_BATH_FILL` ist `Körper` im bisherigen Code logisch
unerreichbar, sobald das für dieses Packet nötige `AIIN` geschrieben ist. Vier
Y+AIIN-Hosts besitzen dennoch keinen Relations-, Form- oder Adressblocker.
GDT589 führt dort `Körper im Bad` als erste Arbeitshypothese und
`Stationsansatz im Bad` als sichtbare Alternative. Der historische Replay
bleibt unverändert; die Gabel ist eine nächste Lesebasis, kein umetikettiertes
Regressionsergebnis.

## Behauptungsgrenze

Der Pass prüft interne Reproduzierbarkeit und verbessert die Arbeitsanzeige.
Er bestätigt weder Voynich-Klartext noch Sprache, historische Quelle,
Realobjektzahl, Patient, Heilmittel, Krankheit oder Einzellexem. Die deutschen
Nomen bleiben ersetzbare Arbeitsbedeutungen auf festen Hosts.
