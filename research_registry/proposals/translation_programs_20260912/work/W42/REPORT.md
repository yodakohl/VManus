# W42 — ein Arbeitsverzeichnis als konkrete Gegenlesung

**Die sechs daiin-Angaben auf f32v lassen sich unter festen Verträgen als zwei gemeinsame Arbeitsleistungen oder als sechs Leistungen je Stoff ausformulieren.** Eine dritte Arbeitsfassung liest Tarife je Materialmenge und bleibt ohne diese Mengen unberechenbar. Die alte Stoffmengenfassung macht dagegen überhaupt keine Aussage über Arbeitsaufwand. Das sind unterschiedliche inhaltliche Konsequenzen, keine vier Namen für denselben Wert.

**Keine Kosten-/Aufwandsbedeutung wird ausgewählt.** Weder eine gelesene Summe noch eine Einheit entscheidet zwischen den Fassungen; 13 der 17 angesetzten Tätigkeiten haben keine daiin-Angabe. Diese Tätigkeiten dürfen nicht kostenlos verbucht werden. Es wurde kein Preis, keine Zahl und kein neues Wort identifiziert.

## Alle Kandidaten und ihre Konsequenzen

IDEA000187; [DECISION.md](DECISION.md) und [SPEC.json](SPEC.json) vor Berechnung. Alle vier exponierten HERB4-Absätze /17Zeilen/145Gruppen, **alle acht daiin-Stellen**. Nur dieses ganze Wort erhält alternative Dimensionen. Andere P05-v03-Wortwerte bleiben gleich; insbesondere wird dain nicht automatisch zum kleineren Preis und dair bleibt offen. Die Untersuchung beansprucht nicht, sämtliche mengenähnlichen Wörter der Schrift zu erklären.

| Kandidat | Konkrete Vorhersage an jeder Stelle | Folge im vollständigen Vergleich | Offene Verpflichtungen / Widersprüche | Entscheidung |
|---|---|---|---|---|
| M: Materialmenge | Gebundener Stoff hat Masse Q·U_M. | Acht Stofffelder, davon sechs auf f32v. Kein Arbeitskonto. | U_M und Q offen; Stoff-/Bindungsannahmen nicht bestätigt. | Bleibt eigener Rivale. |
| E: ganze Tätigkeit | Die referierte Tätigkeitsnennung hat insgesamt Aufwand Q·U_E. | Acht Angaben beziehen sich auf vier Tätigkeitsnennungen; auf f32v zweimal drei Angaben zu jeweils derselben Tätigkeit. Teilkonto dort 2Q·U_E. | Wiederholung derselben Leistungsangabe und die Tätigkeitsbindung sind Annahmen; 13 Tätigkeiten unbepreist. Kein interner Wertkonflikt, da überall dasselbe Q steht. | Formulierbar, nicht ausgewählt. |
| L: Leistung je Stoff | Jede verschiedene Tätigkeit-Stoff-Kombination hat Aufwand Q·U_E. | Acht verschiedene Kombinationen; f32v besitzt sechs. Teilkonto dort 6Q·U_E. | Die getrennte Abrechnung der beteiligten Stoffe ist eine zusätzliche Annahme; U_E und Q offen, 13 Tätigkeiten unbepreist. | Formulierbar, nicht ausgewählt. |
| T: Tarif | Je Kombination gilt Tarif Q·U_E/U_M; Aufwand hängt von der Materialmasse ab. | Acht Tarifbeziehungen; keine numerische Aufwandssumme. | Alle benötigten Massen und Einheiten offen. M darf nicht zusätzlich zur Tariffassung angenommen werden, um Q² zu erzeugen. | Ohne Mengen kein berechneter Aufwand. |

Unabhängige Bestätigungskapazität **für jeden Kandidaten 0**. Geringere Zahl von Buchungen, vollständig besetzte Modellrollen oder eine glatt klingende Leistungsbeschreibung wählen keine Bedeutung. In E/L/T sind Stoffmengen offen; in M ist der Aufwand offen. Es wird kein Vergleich verschiedener physikalischer Dimensionen als Zahlenwiderspruch ausgegeben.

## Nachvollziehbare Tabelle aller acht Angaben

Die beiden unmittelbaren daiin verteilen sich unverändert gemäß P05/S07 auf die letzten beiden verschiedenen Materialformen. Die anderen Angaben binden das letzte linke Material. Tätigkeiten folgen S07s fester Liste und letzter linker Nennung im selben Absatz. Diese Regeln sind gewählte Syntaxhypothesen.

| daiin-Stelle | Stoffhypothese | Zugeordnete Tätigkeit | E | L | T |
|---|---|---|---|---|---|
| f21r.12:7 | chor, Blüten | shey .11:7, einfüllen | Q für diese ganze Tätigkeit | Q für Einfüllen von Blüten | Tarif Q je offene Blütenmasse |
| f32v.8:2 | odan, Rest | shckhy .7:8, vermischen | Q für die gemeinsame Mischung | Q für Rest-Bearbeitung | Tarif Q je Restmasse |
| f32v.8:3 | otchol, getrocknetes Gut | dieselbe shckhy-Nennung | dieselbe Leistungsangabe Q | Q für Trockenmaterial-Bearbeitung | Tarif Q je Trockenmaterialmasse |
| f32v.8:5 | ctho, Pflanzenpulver | dieselbe shckhy-Nennung | dieselbe Leistungsangabe Q | Q für Pulver-Bearbeitung | Tarif Q je Pulvermasse |
| f32v.9:5 | chocthy, Pflanzenmark | skey .9:3, zurückhalten | Q für diese ganze Tätigkeit | Q für Zurückhalten des Marks | Tarif Q je Markmasse |
| f32v.9:7 | cthaiin, Pflanzenportion | dieselbe skey-Nennung | dieselbe Leistungsangabe Q | Q für Zurückhalten der Portion | Tarif Q je Portionsmasse |
| f32v.10:5 | chor, Blüten | dieselbe skey-Nennung | dieselbe Leistungsangabe Q | Q für Zurückhalten der Blüten | Tarif Q je Blütenmasse |
| f29v.1:11 | cthy, Pflanzengut | shytchy .1:6, benetzen | Q für diese ganze Tätigkeit | Q für Benetzen des Pflanzenguts | Tarif Q je Pflanzengutmasse |

Hier steht Q jeweils nur als Kurzform für den Aufwand beziehungsweise Tarif in der jeweiligen offenen Einheit. In M trägt jeder der genannten Stoffe stattdessen die Massenangabe Q·U_M. [FIELDS.tsv](FIELDS.tsv) enthält alle Bindungsloci und vollständigen Zwischenwörter; [PREDICTIONS.tsv](PREDICTIONS.tsv) alle **32 konkreten Modell-/Stellenvorhersagen**, einschließlich Dimension und fehlender Einheiten.

Die dritte Angabe bei der Mischung und die dritte beim Zurückhalten werden nicht weggelassen, nur weil S07 ursprünglich zwei Zweierpaare hervorhob. Gerade die vollständige Fortsetzung ergibt hier je drei Materialfelder. Auf f32v.10 wird chor wegen der unveränderten Tätigkeitsliste weiter an skey gebunden. Das setzt keine neu gefundene Rückverweisung voraus: Es ist ausdrücklich die Folge dieser alten Positionsregel.

## Der zusammenhängende Gegenentwurf auf f32v

```text
f32v.7 ksho cphos she sheaiin otshcho r dain shckhy s odan
f32v.8 otchol daiin daiin ctho daiin qotaiin otchy d shan
f32v.9 qotchy cfhy skey chocthy daiin cthaiin daiin
f32v.10 sho keol chor chol daiin cpho l cthol da ar
f32v.11 ol sho chy
```

E lässt als zusätzlichen Leistungskern formulieren: „Vermische Rest, getrocknetes Gut und Pulver; für diese gemeinsame Arbeit Aufwand Q. Halte Pflanzenmark, Pflanzenportion und Blüten zurück; für diese gemeinsame Arbeit Aufwand Q.“ Die sechs geschriebenen Wertangaben bleiben in der Wortausrichtung erhalten; diese Prosa fasst ihre postulierten Bezüge zusammen und ist keine vollständige Übersetzung der fünf Zeilen.

L gibt denselben drei Stoffen je Arbeitsgruppe jeweils eine eigene Leistung Q und kommt rechnerisch auf 3Q+3Q. T setzt stattdessen für die Mischung den Ausdruck

`Q·U_E/U_M × (m(Rest)+m(Trockenmaterial)+m(Pulver))`

an. Ein analoger Ausdruck gilt für die drei Zurückhaltefelder. Die Stoffmassen sind nicht bekannt. **Diese Summen sind vom Modell abgeleitete Teilkonten, keine entzifferten Summenzeichen oder geschriebenen Rechnungsabschlüsse.**

Das Einfüllen auf f21r.11:7 wird mit Blüten auf .12:7 verbunden, obwohl dazwischen acht Gruppen stehen, fünf davon im festen Lexikon ungelesen. Alle acht stehen in FIELDS.tsv. Ein verbundener Arbeitsauftrag ist dadurch nicht bewiesen. Die P05-Bedeutung shey=fülle ein wird nicht mit P03s anderer Ruhe-/Wirkungslesung vermischt.

## Vollständigkeit des Leistungsblatts

| Absatz | daiin-Angaben | Angesetzte Tätigkeitsnennungen | Davon ohne daiin | E-Teilkonto | L-Teilkonto |
|---|---:|---:|---:|---|---|
| f17r | 0 | 0 | 0 | kein angesetzter Posten | kein angesetzter Posten |
| f21r | 1 | 2 | 1 | Q·U_E | Q·U_E |
| f32v | 6 | 8 | 6 | 2Q·U_E | 6Q·U_E |
| f29v | 1 | 7 | 6 | Q·U_E | Q·U_E |

Einheiten bleiben je Absatz offen; keine gemeinsame Geldsumme über die Blätter. f17r ist kein Beleg für Kosten null, sondern enthält unter diesem Lexikon keinen passenden Posten. [Alle 17 Tätigkeiten einschließlich der 13 unbepreisten](ACTIVITY_ACCOUNTS.tsv), [Absatzkonten](RECORD_ACCOUNTS.tsv). Die übrigen Mengenformen können andere Felder ausdrücken, wurden aber nicht nachträglich zur Ergänzung fehlender Preise benutzt.

## Entscheidung und Prüfung

**Die einfache Behauptung „jede daiin-Wiederholung ist eine zusätzliche Arbeitsleistung“ wird nicht übernommen:** Ob sie eine neue Leistung zählt, hängt an der nicht entschiedenen Trennung E/L. Ein Kostenverzeichnis als vollständige Erklärung dieser vier Absätze ist ebenfalls nicht erreicht. Der Gewinn dieses Passes ist eine explizite Gegenlesung mit verschiedenen Teilkonten, keine empirische Wahl der Dimension und kein neues übersetztes Wort. Keine anschließende Suche nach einer passenden Währung, Einheit oder Summenform gestartet.

Alle vier vollständigen Fassungen stehen in [READING.md](READING.md), jede der 580 wortweisen Modellpositionen in [ALIGNMENT.tsv](ALIGNMENT.tsv). **90 Positionen behalten Bedeutungsannahmen, 55 bleiben offen**; die alternative daiin-Dimension erhöht diese Abdeckung nicht. P03, P05, P14, S07 und W40 bleiben unverändert.

[VALIDATION.json](VALIDATION.json): PASS. Getrennter Code prüft alle acht Bindungen, bewahrt sämtliche vier alten Paarträger von S07, rekonstruiert die 17 Tätigkeitsintervalle und rechnet die unterschiedlichen Teilkonten ohne Builderimport nach. Elf Eingabedateien hashgebunden. Gleicher Bearbeiter; keine unabhängige Bedeutungsprüfung. Ein anfänglicher Syntaxfehler stoppte den Builder vor Auswertung und wurde ohne Vertragsänderung behoben.

Alle Texte und motivierenden Beispiele waren exponiert. Keine Kontakte, neuen Bilder/Seiten, Reservetests, Signifikanz, bestätigten Pflanzen-/Wortnamen oder scorefähige Relationsevidenz. f84/f84r und sämtliche Reserveseiten geschlossen.

```sh
python research_registry/proposals/translation_programs_20260912/work/W42/build.py
python research_registry/proposals/translation_programs_20260912/work/W42/validate.py
```

Repository-Prüfung: W42-Nachrechnung und Ideenregistry PASS. Die globale Prüfung bleibt bei den acht bekannten Altfehlern (sieben ungebundene GDT600-Dateien und veralteter Experimentindex); diese Dateien wurden nicht verändert. Die separate Prüfung des exakten Publikationsstands auf private Inhalte und fremde Dateien ersetzt keine globale Freigabe.
