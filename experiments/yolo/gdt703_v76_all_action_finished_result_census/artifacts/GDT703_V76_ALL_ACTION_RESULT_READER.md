# GDT703 — V76 all-action result reader

Status: `PASS_V76_83_ACTION_RIGHT_CONTEXTS__60_NOMINAL_15_ACTION_8_EOS__7_FINISHED_STATE_FIRSTS__3_LOCAL_READS_4_OPEN__C013_C014_ADDED__ZERO_WORD_DELTA`

## Was die zwei neuen Arbeitslesarten konkret sagen

> **C013 / f26r.2:** Die Krautdroge bis zur Mittelstufe erhitzen und abschließen [Quelle von ‚hiervon‘ offen]. Zustand: mittlere Trockenstufe erreicht. Dieselbe erhitzte Krautdroge bis zur Mittelstufe abkühlen und abschließen [C011/C013-Arbeitshypothese].

> **C014 / f115r.23:** Heißen Auszug bereiten und abschließen. Ergebnis: leicht getrocknete, abgeschlossene Zubereitung.

C013 macht den schon geschriebenen Zustandsvermerk #5 zum Ergebnis von #4; C011 bleibt die separate Fortführung desselben #4-Ausgangs zu #6. Es gibt ausdrücklich keinen #5→#6-Pfeil. C014 endet an #4; die neue Aktion #5 bleibt außerhalb.

## Alle sieben unmittelbaren Fertigzustände

| Fall | Stelle | Aktion → geschriebener Zustand | Arbeitsentscheidung | stärkste Gegenlesung |
|---|---|---|---|---|
| F001 | `f105r.2` | #11 `odar` → #12 `cheody` | HOLD_OPEN | #12 kann einen neuen selbständigen Nominalblock eröffnen; Abmessen erzeugt den Trockenstand nicht. |
| F002 | `f105v.1` | #4 `ykaiin` → #5 `olpchedy` | ADMIT_INHERITED | #5 könnte trotz der Materialkonkordanz einen neuen Registerblock eröffnen. |
| F003 | `f105v.14` | #3 `qokaiir` → #4 `olpchedy` | HOLD_OPEN | Nehmen produziert kein Ergebnis, und Drogenanteil versus Holzpulver ist ein sichtbarer Materialbruch. |
| F004 | `f115r.1` | #3 `qochedain` → #4 `otedy` | HOLD_OPEN | #4 eröffnet einen achtgliedrigen Registerblock; der unmittelbare Produktionsübergang bleibt ungeschrieben. |
| F005 | `f115r.23` | #3 `qokeod` → #4 `chody` | ADMIT_NEW | #4 kann ein selbständiger Materialcheckpoint vor #5 qokcho sein; die leichte Trocknung ist nicht als eigenes Verb im linken Schritt sichtbar. |
| F006 | `f26r.2` | #4 `ykecthey` → #5 `chedy` | ADMIT_NEW | #5 besitzt keinen eigenen Materialkopf und könnte als ungebundener Registerwert gelesen werden; die Quelle von „hiervon“ bei #4 bleibt offen. |
| F007 | `f77v.7` | #5 `ycheedy` → #6 `okedy` | HOLD_OPEN | Endtrocknung und heißer Mittelstufenansatz widersprechen sich als unmittelbarer Zustand desselben unbekannten Patienten. |

## Vollständigkeit

Der Zensus umfasst **alle 83 Aktionsklauseln**. Unmittelbar rechts folgen **60 Nominalblöcke, 15 Aktionsklauseln und 8 Zeilenenden**. Genau **7** erste rechte Einträge sind bereits als `HIGH`-Fertigzustand typisiert: ein bestehender lokaler Edge (C012), zwei neue lokale Arbeitsedges (C013/C014) und vier offen gehaltene Nicht-Edges. Kein attraktiveres späteres Wort wurde übergangen.

Der kumulative Leser besitzt jetzt **14 Kanten in 10 Komponenten**. Die 479 Wortglossen, 51 Zeilenübersetzungen und 3 gebundenen Spannen bleiben unverändert; hinzu kommt keine neue Wortbedeutung und keine Seite.
