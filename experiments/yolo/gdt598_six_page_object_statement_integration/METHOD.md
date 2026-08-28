# GDT598 method

## Eingaben und Guard

GDT584 liefert die geordnete Hostebene, GDT582 nur die geschriebenen
Y/AIIN/AIN/OR-Trägerslots an noch offenen Aktionen. Beide gemischten TSVs
werden durch `vmanus-exp query-tsv` mit sechs expliziten `--allow`-Werten und
einer festen Spaltenliste gelesen; f84-Präfixe werden vor dem Materialisieren
verworfen. Die bereits sechsseitigen GDT596- und GDT597-Replays werden auf
dieselbe Seitenmenge geprüft.

## Exakter Join

Ein GDT596-Action-Slot `RUNNING:G407-E…@n` wird zum vorhandenen
GDT584-Governor `ACTION:G407-E…@n:SH`. GDT597 besitzt diesen Governor bereits
direkt. Beide Mengen sind disjunkt und treffen 650 von 1.443 eindeutigen
Aktionshosts:

| Schicht | Rootmenge | Aktionen |
|---|---|---:|
| GDT596 | SH_BIO_BATHE | 254 |
| GDT597 | T, CHD, S | 396 |
| zusammen | SH, T, CHD, S | 650 |

Nur `gdt598_integrated_clause_de` wird am getroffenen Host ersetzt. Alle
übrigen 1.622 Hosts behalten die GDT584-Klausel. Danach werden die Hosts in
unveränderter Aussage- und Absatzfolge neu zusammengesetzt.

## Restinventar

Die vollständige GDT584-Sechs-Seiten-Ebene enthält 1.443 Aktionen. Nach dem
650er Join bleiben 793:

| Root | Rest | Teilnehmerpacket Y/AIN/OR | nur AIIN-Parameter | ohne Träger |
|---|---:|---:|---:|---:|
| CH | 196 | 32 | 1 | 163 |
| K | 159 | 106 | 7 | 46 |
| OK | 285 | 132 | 34 | 119 |
| P | 55 | 8 | 0 | 47 |
| R | 52 | 20 | 4 | 28 |
| SH außerhalb SH_BIO_BATHE | 46 | 0 | 0 | 46 |
| gesamt | 793 | 298 | 46 | 449 |

Die 344 geschriebenen Hosts tragen zusammen 410 Slots. 298 enthalten
mindestens Y, AIN oder OR und besitzen damit einen sichtbaren Teilnehmer; 46
sind AIIN-only und liefern zunächst nur ein Maß. Roots und GDT582-Nomen werden
vollständig ausgegeben, aber GDT598 entscheidet noch nicht, wie ein
Mehrfachpacket syntaktisch zu lesen ist. Die 46 Parameter-only- und 449
trägerlosen Hosts bleiben ausdrücklich Referenz-/Defaultaufgaben.

Der Join erfolgt nur über `action_slot_id`. Die 650 Aktionen liegen in 610
Ereignissen; 36 Ereignisse tragen zwei bis vier fertige Aktionen, davon 20 aus
beiden Phrasebookschichten. Ein Event-Dictionary verlöre 40 Klauseln. Ebenso
führen zehn der nur 154 verschiedenen alten Klauselstrings an insgesamt 240
Slots zu mehreren verschiedenen Endfassungen. Stringersetzung ist daher
unzulässig.

Vierzig lokale GDT586-Karten werden in einen getrennten Seitenanhang kopiert.
Fünf davon besitzen sieben Name-Overrides; alle vierzig verbieten ausdrücklich
Vererbung in laufende Aussagen. Die 23 GDT596- und 17 GDT597-Reviewkarten
erhalten namespacete IDs, weil `W01` bis `W17` sonst kollidieren.

Der frühere breitere GDT582-Census von 900 CH/K/P/OK/R-Hosts ist nicht die
richtige Zielzahl für die Satzedition: GDT598 zählt nur die 793 tatsächlich in
GDT584 gerenderten Restaktionen und schließt die 46 nichtbadenden SH-Hosts ein.

## Ausgabegrenze

GDT598 integriert, ohne neue Semantik zu erfinden. Die 793er Tabelle ist die
exakte Startpopulation des nächsten Objektpasses. Deutsche Nomen bleiben
austauschbare Arbeitsdefaults; Roots, Oberfläche, Parser und Seiten ändern
sich nicht.

## Handling-Korrektur

Ein delegierter explorativer Suchlauf verwendete beim ersten Q-Marker-Trace
versehentlich ein globbasiertes `rg` über gemischte globale TSV-Artefakte statt
des vorgeschriebenen Guards. Im ausgegebenen Trefferstrom wurde keine
f84/f84r-Zeile sichtbar; dennoch werden sämtliche Beobachtungen dieses Laufs
verworfen. Die hier berichteten sechsseitigen Counts stammen ausschließlich
aus erneuten `vmanus-exp query-tsv`-Abfragen mit expliziten Allow-Seiten und
Spalten. Der falsche Zugriffspfad wurde nicht weiterverwendet.
