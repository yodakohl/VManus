# GDT592 — Methode

## Frage

Kann jede der 254 bereits als `SH_BIO_BATHE` gelesenen Handlungen auf den sechs
bekannten Badseiten ein konkretes Arbeitsobjekt erhalten, ohne eine neue Seite,
Wurzel, Segmentierung oder freie Wortbedeutung einzuführen? Und bleibt die
ältere GDT569-Argumentspur sichtbar, wenn sie nicht mit diesem neuen
Episode-Objekt übereinstimmt?

## Feste Population und Eingaben

Die Population sind exakt die 254 aktionsslot-eindeutigen GDT583/GDT584-
Badhandlungen in 177 Aussagen auf f75r, f77r, f81r, f81v, f82r und f83r. Ein
Ereignis, E3243, enthält zwei getrennte SH-Slots; deshalb bleibt der
`action_slot_id`, nicht die Ereignis-ID, Primärschlüssel.

GDT581 liefert sämtliche Hostslots und Blocker, GDT584 die Hostreihenfolge und
Lesergrenzen, GDT587 die action-conditioned Nominalphrasen, GDT590 die 1.243
Carrier-Slots und den aktuellen 793-Aussagen-Leser, GDT591 die 92 festen
Körper/Station-Zuweisungen. GDT515 und ZL3b liefern Ort und physische
Absatzgrenze. GDT569 wird geschützt auf dieselben sechs Seiten geladen und nur
als parallele Ereignisspur hinzugefügt. Alle gemischten TSVs werden vor dem
Materialisieren nach Seite ausgewählt; f84/f84r bleiben gesperrt.

## Objektregel

Für jede Badehandlung gilt in dieser Reihenfolge:

1. geschriebenes Y übernimmt exakt GDT590/GDT591 `Körper` oder
   `Stationsansatz`;
2. geschriebenes OR ergibt `Badeinheit`, geschriebenes AIN
   `Anwendungsportion`; AIIN ist ausschließlich `Badfüllung`;
3. ein vollständiger GDT581-Hostblocker ergibt `Stationsansatz`;
4. an 13 vollständig benannten Vorkommen übernimmt die Handlung den näheren,
   zwischen altem Bad-Donor und Ziel stehenden Y/OR/AIN-Träger;
5. sonst wird das letzte Badeobjekt nur innerhalb derselben Aussage, desselben
   Readersegments und desselben physischen Absatzes fortgetragen;
6. ohne jeden Donor gilt neutral `Badegut` / `das zu badende Gut`.

Die 13 lokalen Übergaben sind occurrence-level Karten. Ihr Ziel, Gouverneur,
Aktionsslot, geschriebener Wurzelslot, Quellereignis, Hostabstand, sichtbarer
Ort und Donorklausel sind fest ausgegeben. Neun besitzen eine explizite
GDT587-Zuweisung; bei vier OK/K-Hosts stammt die bereits ausgeschriebene
Nominalphrase unverändert aus dem vollständigen GDT584/GDT587-Leser. Daraus
wird keine neue globale Handoff-Regel abgeleitet.

Ein Carry wird an Aussagenbeginn, nach `PARAGRAPH_AFTER` und bei physischem
Absatzwechsel gelöscht. Sichtbare Ereignisdistanz und abstrakter Hostabstand
werden getrennt geführt. Die elf verbleibenden Carries liegen null bis zwei
Ereignisse auseinander; kein langer Carry bleibt.

## Leserpatch und parallele GDT569-Spur

149 objektlose Klauseln werden ausschließlich am Präfix
`Halte im Bad` ergänzt. Fünf AIIN-only-Klauseln werden aus
`Halte die Badfüllung` zu `Halte <Objekt> im Bad bei der angegebenen Füllung`.
Der gesamte nachfolgende Klauseltext bleibt bytegleich. Weil 14 Zielhosts in
sechs Aussagen identische Klauseln besitzen, erfolgt der Austausch über
`statement_id + host_ordinal + primary_governor_key` mit Vorwärtscursor, nie
als globaler Textersatz.

GDT569 wird per `anchor_event_id = event_id` links angefügt. Seine
`inherited_argument_root` bleibt ausdrücklich eine andere Ebene als das neue
`episode_object`. Bei 61 neutralen Badegut-Defaults liefert sie schon einen
spezifischen Kandidaten: 49×Y, 8×AIN und 4×OR. Zwei wirkliche Konflikte bleiben
offen: E1719 Station gegen altes AIN und E2481 Station gegen altes OR.

## Behauptungsgrenze

GDT592 ist eine vollständige explorative Arbeitsübersetzung der vorhandenen
Badhandlungen. Sie darf ihre konkreten Defaults verwenden und bessere lokale
Donoren vorziehen, bestätigt aber kein Voynich-Lexem, keinen Stamm, Klartext,
Patienten, Körperteil, Stoff, Prozess, Krankheit, Heilung, Sprache,
historisches Codebuch oder neue Seite. `Badegut`, Körper, Station, Einheit und
Portion sind redaktionelle Bedeutungsrollen; GDT569 bleibt eine konkurrierende
Argumentspur und keine stillschweigende Wortgleichung.
