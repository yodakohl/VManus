# P11 — sechs Prädikate mit einer gemeinsamen Teilnehmerregel

Alle vier HERB4-Absätze wurden vollständig ausgerichtet und als Beschreibung
sowie Anweisung ausgearbeitet. [Das konkrete Kapitel](CHAPTER.md) enthält die
vollständigen Absatzkonzepte, ihre Ergänzungen und alle unbequemen Folgen.

**Die Arbeitsfassung hält ein genanntes Material aktiv, wenn das nächste Nomen
nur Inhalt oder Ortsargument eines Prädikats ist.** Dadurch wird zum Beispiel
aus `okaiin sho tshaiin chkaiin` hypothetisch „Ansatz enthält Auszug; der Ansatz
ist gemischt“ beziehungsweise „Führe dem Ansatz Auszug zu; vermische den Ansatz“.
Das ist eine konkrete gemeinsame Syntax, noch keine entschlüsselte Aussage.

## Alle sechs Prädikatskarten und alle Vorkommen

Die [sechs Karten](SIX_PREDICATE_CARDS.tsv) fixieren Bedeutungshypothesen,
Stellenzahlen und sämtliche Loci. Es wurde keine Stellenzahl pro Fundstelle
geändert. [PARTICIPANTS.tsv](PARTICIPANTS.tsv) enthält alle20Vorkommen,
[ROLE_BINDINGS.tsv](ROLE_BINDINGS.tsv) jede einzelne Rolle beider Fassungen.

| Ganzform | Beschreibung D0/D1 | Anweisung I0 | Vorkommen |
|---|---|---|---:|
| chol | ist trocken | trockne | 7 |
| shol | ist feucht | befeuchte | 3 |
| sho | enthält | führe zu | 4 |
| qotchy | befindet sich bei | überführe nach | 2 |
| shey | ist heiß | erwärme | 2 |
| chkaiin | ist gemischt | vermische | 2 |

Alle145Gruppen bleiben an ihrer Position in [D0/D1](READING_D0.md) und
[I0](READING_I0.md).36gemeinsame Nomen-/Nebenwerte plus sechs Prädikate ergeben
83hypothetisch belegte und62offene Positionen. Die Nomenwerte sind frei
angesetzte konkrete Kandidaten, teilweise aus früheren Arbeitshypothesen:
kein Beweis aus GDT559/770/809 oder P05/P09. Insbesondere sind `tcho=Pflanzenmaterial`,
`tshaiin=Flüssigauszug` und die drei Trockenmaterialformen nicht identifiziert.

## Sämtliche zweistelligen Inhalts-/Ortsbeziehungen

| Stelle | Aktiver Materialkandidat | Direktes rechtes Argument | D0/D1 | I0 |
|---|---|---|---|---|
| f21r.9:2 sho | okaiin, Ansatz | tshaiin, Flüssigauszug | Ansatz enthält Auszug | Auszug dem Ansatz zuführen |
| f32v.10:1 sho | cthaiin, Pflanzenportion | keol, Öl | Portion enthält Öl | Öl der Portion zuführen |
| f32v.11:2 sho | cthol, Trockenmaterial | chy, Wasser | Material enthält Wasser | Wasser dem Material zuführen |
| f29v.4:8 sho | cthy, Kraut | okaiin, Ansatz | Kraut enthält Ansatz | Ansatz dem Kraut zuführen |
| f32v.9:1 qotchy | shan, Feinanteil | cfhy, Filterstelle | Feinanteil befindet sich bei Filterstelle | Feinanteil zur Filterstelle überführen |
| f29v.3:6 qotchy | odaiin, Zusatzportion | taiin, Auffanggefäß | Portion befindet sich beim Gefäß | Portion zum Gefäß überführen |

Die sechs rechten Argumente passen zu den **angenommenen** Typen; es wurden
keine ungeeigneten Nachbarn übersprungen. Diese Passung ist keine unabhängige
Semantikbestätigung, da das Wörterbuch Teil des Entwurfs ist. Filterstelle und
Auffanggefäß bleiben Orte; sie werden nicht zugleich als neuer Materialträger
oder Werkzeug benutzt. Alle Wortrollen und ihre Inanspruchnahme sind sichtbar.

Beide qotchy-Fälle nennen unter den Annahmen dasselbe jeweilige Material vor
und am Prädikat. Eine bereits gebundene Anfangslage oder eine spätere unabhängig
aufgelöste Materialwiederaufnahme fehlt jedoch. Der zuvor genannte Mörser auf
f29v ist nicht automatisch der Inhaltsträger der Zusatzportion. **Bewegung und
bloße Ortsangabe bleiben daher ununterschieden.** Ein fehlender Ausgangsort
wird nicht als grammatischer Fehler von „überführe nach“ gewertet.

## Wiederholungen und Konsequenzen der festen Regel

* `shol chol shol` in f21r.11 betrifft unter dieser Regel dieselbe Materialnennung
  qotchol aus f21r.10. Zeitlos auf derselben Eigenschaftsachse entsteht feucht →
  trocken → feucht, zwei gegensätzliche Folgezustände. Als zeitliche Folge ist
  das formulierbar, sowohl als Anweisung I0 als auch als Beschreibung D1.
  Die Wiederholung selbst ist aus GDT809 bekannt, keine neue Entdeckung.
* Die beiden chol-chol-Folgen auf f29v beziehen sich jeweils auf dasselbe
  vorherige Material, einmal Feinpulver, einmal zerkleinerte Blüten. Keine
  Intensivierung, keine Addition und kein frei eingeführter zweiter Gegenstand.
* `kor shey` erwärmt unter I0 die noch aktiven Blüten, nicht den Mörser.
  `sho okaiin` führt dem Kraut Ansatz zu, nicht umgekehrt. Diese unbequemen
  Folgen wurden nicht nachträglich umgedreht.
* Doppelte daiin bleiben doppelte Maßnennungen; ihre Achsen/Träger sind nicht
  durch P11 gelöst. `sheey` bleibt verschieden von `shey`; keine Umsegmentierung.

[STATIC_CONFLICTS.tsv](STATIC_CONFLICTS.tsv), [STATE_TRACE.tsv](STATE_TRACE.tsv)
und [TOPIC_TRACE.tsv](TOPIC_TRACE.tsv) machen sämtliche Zustands- und
Teilnehmerfortführungen nachvollziehbar. Die24vorläufigen Einheiten in
PROVISIONAL_UNITS.tsv sind keine bewiesenen Sätze; alle145Gruppen werden darin
einmal erhalten. Unbekannte Gruppen könnten in der wirklichen Sprache andere
Themen, Grenzen oder Negationen enthalten. Das ist eine offene Voraussetzung
des ganzen Modells, keine erfolgreiche Auswertung dieser unbekannten Wörter.

## Entscheidung

Als vorsichtige Arbeitsdarstellung wird **D1, eine zeitlich gegliederte
Beschreibung**, geführt: dieselben D0-Wortwerte und Rollen, mit nicht rückwärts
laufender Aussagezeit für den gesamten Absatz. D0s strikte Zeitlosigkeit ist
bei angenommenem gleichen Träger/gleicher Achse unzureichend. **Der Imperativ
I0 bleibt offen; keine Aufforderungsform ist erkannt.**

D0/D1 verwenden26Rollenpositionen, I0 46. Die Differenz besteht ausschließlich
aus20Verwendungen von vier gemeinsamen impliziten Bearbeitern. Diese sind
normale mögliche Anweisungsadressaten, nicht20unerklärte neue Personen. D1s
sparsamere Darstellung ist daher kein wissenschaftlicher Sieg über I0.
Auch das Fehlen ungeschriebener Materialplätze unter dem konkreten Nomenlexikon
bestätigt dieses Lexikon nicht.

P11 liefert einen ersten durchgängigen Teilnehmerentwurf und präzisere offene
Fragen. Der Unterschied enthalten/zuführen und Standort/Bewegung ist noch
nicht entschieden. Die62offenen Positionen verhindern eine vollständige
Gesamtlesung. Nächster eigenständiger Ansatz: **P12, ausgelassene Subjekte und
Rückverweise**, mit erneuter Hypothesenkennzeichnung der Teilnehmeridentitäten.

## Daten, Vorgänger und Reproduktion

DECISION.md liegt vor der Ausführung. Verwendet wurde ausschließlich die bereits
exponierte P09-INPUT-Kopie, SHA256-gebunden an GDT809s vollständige vier Absätze.
Keine neue Rohtranskription, kein BATH3-Zugriff, keine neue Bildzulassung. GDT559s
Komponentenmodell und GDT770s Maskenranking werden nicht erneut ausgeführt;
deren Befunde und alle alten Quellbytes bleiben unverändert.

ZL-gerahmte Darstellung: insbesondere f29v.2 hat in IT die andere Segmentierung
`schol chol`; f32v.8 in RF `cthodaiin` statt `ctho daiin`. Keine nachträgliche
Normalisierung, keine ganze Dreileserrobustheit behauptet. Alternative Lesungen
zählen nicht als unabhängige Manuskripte.

`python3 research_registry/proposals/translation_programs_20260912/work/P11/build.py`
reproduziert Quelle, Karten, Ausrichtungen und alle Bindungen. VALIDATION.json
prüft Quellen-/Regeltreue, nicht Bedeutung. Keine neue scorefähige visuelle
Relationsevidenz; die Rollen sind interne Hypothesen und kein GDT388-Besitzerbeweis.

Keine Signifikanz oder Suche-Gegenkontrolle. Unabhängige Bestätigungskapazität0,
bestätigte Wortbedeutungen0. Keine Kontakte, keine Reserveseitenprüfung;
f84/f84r und sonstige zurückgehaltene Seiten bleiben geschlossen.
