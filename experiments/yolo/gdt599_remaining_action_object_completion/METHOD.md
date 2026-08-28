# GDT599 — Methode der vollständigen Objektlesung

## Frage

Kann der in GDT598 exakt bestimmte Rest von 793 Aktionshosts auf denselben
sechs Seiten mit einer kleinen, einheitlichen Werkstattgrammatik vollständig
mit Gegenständen oder Parametern versehen werden? Das Ziel ist eine
fortschreibbare Lesefassung, in der keine Aktion bedeutungsleer bleibt und in
der geschriebene lokale Hinweise Vorrang vor ergänzten Bedeutungen haben.

## Fester Arbeitsbestand

GDT599 öffnet keine weitere Manuskriptseite und dekodiert keine Bilder oder
Transkriptionen neu. Es liest ausschließlich die bereits veröffentlichten
GDT598-Artefakte für `f75r`, `f77r`, `f81r`, `f81v`, `f82r` und `f83r`:

- den geordneten Strom von 2.272 Hosts;
- die 793 noch objektlosen Aktionsslots;
- die vierzig getrennten lokalen Karten;
- die vierzig übernommenen manuellen Reviewkarten.

Dazu kommen drei kleine, offen einsehbare GDT599-Quellen: elf lokale
Objektentscheidungen, eine AIIN-Substratkorrektur und drei reine
Klauselglättungen. Die Seiten `f84` und `f84r` bleiben ausdrücklich gesperrt.

## Getrennter Zustandsraum

Das Modell unterscheidet Teilnehmer von Parametern. Teilnehmer sind `BODY`,
`BODY_PART`, `STATION`, `PORTION`, `UNIT` und `FLOW`. Parameter sind `MEASURE`
und `CONDITION`. Dadurch wird etwa eine Maßangabe nicht stillschweigend zum
bearbeiteten Stoff.

Die laufende Teilnehmerhistorie gilt nur innerhalb eines Arbeitsschritts.
`OT` und `DY` schließen sie ab. Ein neuer Kandidat darf deshalb nicht über
einen solchen Schnitt zurückgreifen. `FRAME-Q` verändert die Historie nie.
Ein aktionsgebundenes `CARRIER_Q` liest zuerst seinen Gegenstand und übernimmt
erst danach das Ergebnis als neuen Bad- oder Stationsansatz.

## Auswahlfolge für die 793 Restslots

Jeder Restslot wird in derselben Reihenfolge bearbeitet:

1. eigener geschriebener Teilnehmer aus `Y`, `AIN` oder `OR`;
2. eigenes AIIN ohne Teilnehmer als lokaler Mengen- oder Maßparameter;
3. die zwei ausdrücklich markierten unmittelbaren CH→SH-Brücken;
4. ein kompatibler geschriebener Teilnehmer rechts im selben Ereignis;
5. der nächste kompatible Teilnehmer links nach dem letzten `OT`/`DY`;
6. nur ohne linke Quelle: ein begrenzter rechter, bereits ergänzter
   Teilnehmer im selben Ereignis;
7. ein kurzer, ausdrücklich ersetzbarer Rootdefault;
8. eine lokale Werkstattentscheidung, wenn die regelhafte Projektion im
   konkreten Ablauf eine offenkundig schlechtere Lesung ergibt.

Die Referenzform folgt zugleich aus der Quelle: eine linke Quelle wird
anaphorisch (`derselbe`, `dieselbe`, `dasselbe`) gesprochen; eine rechte,
eigene oder defaultierte Quelle erhält eine bestimmte Nominalgruppe.

## Kurze Rootdefaults

Die Defaults sind bewusst einfache Nomina und keine versteckten Sätze:

| Root | Default | Arbeitslesung |
|---|---|---|
| CH | `STATION / Stationsansatz` | entnehmen oder ablassen |
| K | `STATION / Stationsansatz` | zuführen oder einbringen |
| OK | `STATION / Stationsansatz` | beschicken oder vorbereiten |
| P | `PORTION / Anwendungsportion` | anwenden oder einsetzen |
| R | `STATION / Stationsansatz` | kennzeichnen oder prüfen |
| SH | `CONDITION / Stationsbedingung` | einen Zustand halten |

Diese Defaults schließen eine Lücke, behaupten aber kein entschlüsseltes
Lexem. Jede bessere lokale oder spätere kompositionelle Deutung darf sie
ersetzen.

## AIIN als Mengenhülle

Die 46 AIIN-only-Fälle werden nicht mit einem fernen Gegenstand aufgefüllt.
CH, K und OK sprechen stattdessen eine abgemessene Menge des lokal bestimmten
Substrats; R spricht eine Maßangabe. Das Substrat kommt aus dem kurzen lokalen
Zustand oder, wenn dort nichts Passendes steht, aus dem Rootdefault. Drei
unmittelbar aufeinanderfolgende AIIN-Fälle werden als „eine weitere
abgemessene Menge“ gesprochen. Eine einzige dokumentierte Korrektur verhindert
eine sachlich unpassende Fernübernahme.

Das ist historisch als Formtyp plausibel, nicht als Sprachbeweis: spätmittel-
alterliche Rezept- und Kochhandschriften verbinden Imperative regelmäßig mit
benannten Mengen oder Portionen. Vergleichspunkte sind British Library Harley
MS 2378 (um 1395), Durham Cosin MS V.iv.8 (frühes 15. Jahrhundert) und die
Harleian cookery books (um 1430/1450).

## Lokale Werkstattentscheidungen

Elf Einzelfälle korrigieren die grobe Projektion, ohne ein globales Wort neu
zu definieren: sieben Pfadkontexte werden als `FLOW / Strom` gelesen, zwei
Q-Fälle erhalten eine Portion beziehungsweise den Inhalt einer Einheit, ein
kurzer Maßübergang wird explizit gemacht und eine Entnahme am Körperteil wird
als `PORTION / Probe` typisiert. Drei dieser Entscheidungen verändern auch den
unmittelbaren Folgesatz; diese Fortwirkungen stehen in einem eigenen Artefakt.

Drei weitere Einträge glätten nur den deutschen Satzbau von Bedingungen. Sie
ändern weder Objektklasse noch Lemma.

## Ausgabe und Kontrolle

Der Lauf erzeugt neben den 793 Einzelentscheidungen eine vollständige Edition
aller 1.443 Aktionshosts, aller 2.272 Hosts und aller 313 Aussagen. Der
Validator rekonstruiert alle Tabellen bytegenau, prüft die vollständigen
Populationen, Referenz- und Objektprofile, Q-Zustandswechsel, AIIN-Hüllen,
manuelle Fortwirkungen, Absatzgrenzen und die unveränderte GDT598-Quellspalte.
Die eindeutige Provenienzidentität ist `host_ordinal_global`; beschreibende
OWNER- und FRAME-Schlüssel dürfen sich wiederholen.

## Reichweite der Arbeitstheorie

GDT599 liefert eine konkrete, lückenlose deutsche Werkstattlesung der sechs
Arbeitsseiten und ein vorhersagbares Verfahren für lokale Objektfortsetzung.
Es bestätigt keine Voynich-Klartexte, keine historische Sprache und keine
einzelne reale Substanz, Krankheit, Person oder Behandlung. Vor allem die 54
Rootdefaults und die 125 markierten Reviewfälle bleiben bewusst die
beweglichste Schicht der Theorie.
