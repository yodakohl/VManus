# Pass1024 — Biological/Celestial als jeweils neue Lehrlingsseite

## Kurzantwort

**Keine grobe Anschluss-, Scope- oder Stackregel ist auf nur einer Seite nötig.** Alle zwölf Seiten lassen sich mit einer Regel lesen, die auf mindestens einer anderen der zwölf Seiten bereits vorkommt. Es werden weder ein neuer Kernwert noch ein neuer Stackgriff gebraucht.

Der Replay umfasst 2.684 laufende Karten in 559 Aussagen mit 3.096 Fokusanschlüssen. Davon waren in Pass1023 270 ausdrücklich entschieden und 125 gegenüber Pass1022 geändert worden. Hinzu kommen 358 reine Himmelslabels auf f69v/f70v. Kein einziger der insgesamt 3.454 Replay-Einträge verlangt eine seitenprivate Elternregel.

## Seite für Seite

| Seite | Lauftext / Labels | Pass1023 entschieden → geändert | lokale Besitzerlast | Woher der Lehrling die Regeln kennt |
|---|---:|---:|---|---|
| f75r | 408 / 0 | 37 → 17 | 1 Besitzer; 19/433 Fokuswerte direkt dort | andere Biological-Seiten |
| f76r | 560 / 0 | 45 → 27 | 13 Besitzerblöcke; 27/641 direkt dort | andere Biological-Seiten |
| f77r | 321 / 0 | 41 → 19 | 1 Sammelbesitzer; 23/359 direkt dort | andere Biological-Seiten |
| f81v | 253 / 0 | 23 → 7 | 1 Besitzer; 11/282 direkt dort | andere Biological-Seiten |
| f82r | 278 / 0 | 32 → 14 | 1 Besitzer; 7/353 direkt dort | andere Biological-Seiten |
| f83r | 341 / 0 | 33 → 10 | 1 Besitzer; 12/389 direkt dort | Biological, außer offenem Seitenende aus f67r2/f71v |
| f67r2 | 126 / 0 | 15 → 8 | 1 Besitzer; 3/145 direkt dort | andere Celestial-Seiten |
| f68r1 | 31 / 0 | 5 → 0 | 1 Besitzer; 0/44 direkt dort | andere Celestial-Seiten |
| f69v | 0 / 140 | 0 → 0 | 140 Adressen in 31 Loci | Adresskopie von f70v |
| f70v | 0 / 218 | 0 → 0 | 218 Adressen in 50 Loci | Adresskopie von f69v |
| f71v | 78 / 0 | 5 → 2 | 3 Ringbesitzer; 0/105 direkt dort | andere Celestial-Seiten |
| f72r | 288 / 0 | 34 → 21 | 10 Ringbesitzer; 7/345 direkt dort | Celestial, außer AR/AL-Besitzerrückfall aus Biological |

Zehn Seiten bleiben vollständig innerhalb ihres eigenen Panels lehrbar. Nur zwei benutzen für genau einen groben Griff ein Beispiel aus dem anderen Panel:

- **f83r — `TRUE_OPEN_END`:** Innerhalb Biological ist f83r der einzige echte offene Schluss. Der Griff ist aber bereits auf f67r2 (`PAGE_END_OPEN`) und f71v (`TRUE_OPEN_FINAL_RING`) sichtbar. Neu ist nur der lokale Grund für das offene Ende, nicht die Stackregel.
- **f72r — `OWNER_ADDRESS_FALLBACK`:** Im Celestial-Lauftext ist f72r die einzige Seite mit dem nackten AR/AL-Rückfall zum Besitzer. Derselbe Griff ist auf allen sechs Biological-Seiten vorhanden. f72r übernimmt also eine bekannte Besitzerregel und erfindet keine Himmels-Sondergrammatik.

## Die sechs wirklich seitenprivaten Exact-Signaturen

Seitenprivat sind sechs sehr enge Beschriftungen, aber keine ihrer Elternregeln:

| Seite | private Exact-Signatur | Stellen | bekannte Elternregel |
|---|---|---:|---|
| f67r2 | `GRADE_TO_NEXT_COMPATIBLE_HEAD` | 1 | höchstens eine Karte zum nächsten kompatiblen Kopf |
| f67r2 | `OPENING_ARGUMENT_TO_NEXT_Q_PACKET` | 2 | kopfloses Anfangspaket + ein Karten-Vorgriff + Q-Push |
| f77r | `FORWARD_RELATION_FRAME` | 1 | L/AIR-Rechtsrahmen |
| f81v | `R4_TAIL_BEFORE_OL` | 1 | positionsabhängiger R-Schwanz + OL-Fortsetzung |
| f82r | `CLOSE_OPEN_HEAD_BEFORE_NEXT_HEAD+R1_HEAD_WITH_LOCAL_RIGHT` | 1 | nächster Kopf, Gleichstand links + R als lokaler Kopf |
| f82r | `R1_HEAD_IN_RIGHT_FRAME` | 2 | L-Rechtsrahmen + R als erster Kopf darin |

Damit sind acht Fokusstellen in einer nur lokal vorkommenden Exact-Konfiguration, aber alle zerfallen vollständig in bereits anderswo gebrauchte Werkstattgriffe. Besonders f82r braucht keine neue „vierte R-Funktion“: Es kombiniert lediglich Rechtsrahmen, Gleichstand-links und den bekannten positionsabhängigen R-Kopf.

Auch die seitenprivaten sichtbaren Endnamen sind nur lokale Geometrie: f76r hat `VISIBLE_PARAGRAPH_BOUNDARY`, f77r den Reset zu den unteren Stationslabels, f71v zwei Ringnamespace-Wechsel und einen offenen Schluss, f72r die sichtbare Ring-/Besitzergrenze. Alle gehören zu den anderswo belegten Familien **sichtbarer Besitzer-/Proseblock-Reset** oder **echtes offenes Ende**.

## Scope und Stack

Die laufenden Seiten verwenden in wechselnder Dichte denselben kleinen Stapel:

- mehrere Köpfe verschachteln;
- laufenden Kopf über Karten tragen;
- `Q` pusht;
- `OT` wechselt;
- `OL` führt fort;
- `OS`/VORBEZUG restauriert — auf f67r2 und f72r gegenseitig belegt;
- lizenziertes `DY` schließt;
- sichtbare Besitzer-/Proseblockgrenze resettet;
- ein wirklich offenes Ende bleibt offen.

Jede dieser Familien steht auf mindestens zwei Seiten. Selbst das größte lokale Paket — fünf Köpfe auf einer Karte in f82r — verlangt nur den auf vielen anderen Seiten sichtbaren Multihead-Nestgriff.

Die Bilderlast erscheint deshalb nicht als neue Syntax, sondern im Besitzerstapel. f76r verteilt seinen unbebilderten Lauftext auf 13 dokumentierte Besitzer-/Textblöcke, f72r auf zehn Ringbesitzer und f71v auf drei Ringgruppen; die übrigen laufenden Seiten haben meist einen breiten Seitenbesitzer. Der Stack bleibt derselbe, nur der sichtbare Besitzer wechselt häufiger.

## f69v und f70v: die Tür bleibt geschlossen

f69v und f70v besitzen in Pass1023 **keinen Lauftext, kein Statement und keinen Fokusanschluss**. Ihre 140 beziehungsweise 218 Gruppen bleiben vollständig `LOCAL_ADDRESS_OR_LABEL`.

Das ist wichtig, weil die Oberflächen vertraute Kerne enthalten: Auf f69v tragen 70 Labelzeilen handlungsähnliche Kerne, auf f70v 91. Das öffnet trotzdem keinen Prose- oder Handlungsstack. Der Lehrling kopiert die jeweilige Ringposition beziehungsweise lokale Adresse als Ganzes zum sichtbaren Besitzer. f69v und f70v belegen diese OWNER/ADDRESS-only-Tür gegenseitig; ihre bekannten Teilzeichen werden nicht zu neuen Sätzen hochgerechnet.

## Arbeitsfassung nach dem Replay

Die Pass1023-Grammatik bleibt unverändert. Für eine neue Seite genügt:

> Zuerst entscheiden, ob die Gruppe Lauftext oder lokale Adresskopie ist. Im Lauftext gelten nächster Kopf, Gleichstand links, L/AIR rechts, nacktes AR/AL zum Besitzer, höchstens eine Karte Vorgriff und der positionsabhängige R-Kopf/-Schwanz. Q/OT/OL/VORBEZUG/DY verändern nur den bekannten Stapel. Sichtbare Besitzergrenzen resetten; Labelringe eröffnen keinen Prosegang.

Die vollständige Fallliste steht in `BIO_CELESTIAL_REPLAY_FULL.tsv`, die zwölf Seitenbilanzen in `BIO_CELESTIAL_REPLAY_PAGE_SUMMARY.tsv` und die Exact-zu-Elternregel-Zuordnung in `BIO_CELESTIAL_REPLAY_RULE_SUPPORT.tsv`.
