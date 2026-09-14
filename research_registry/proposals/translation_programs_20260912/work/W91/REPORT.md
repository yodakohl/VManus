# W91 — der konkrete Folgerungsentwurf für f83r ist nicht ausreichend gebunden

Die erste Begründungslesung wurde tatsächlich an allen sieben bereits exponierten f83r-Records ausgeführt. Unter ihren festen Annahmen trägt keine der sieben sol-Stellen einen nachgewiesenen Schluss: fünf besitzen eine Zielaussage, die aus den gelesenen vorherigen Voraussetzungen nicht folgt; zwei bleiben ohne Zielbindung. Das ist ein Defizit dieses Entwurfs, kein Nachweis unlogischer Manuskriptprosa. 298 von 341 geschriebenen Gruppen bleiben semantisch offen. Eine nahezu vollständige Lesung, ein Syllogismus und eine Wortübersetzung wurden nicht erreicht.

## Konkrete Lesung und Auswahl

Der Ansatzpunkt im vollständig gelesenen Arbeitsmaterial war f83r.20–21:

```
.20 solkeedy qoteedy qokeey qokedy sol cheeety qokedy qoky saiin
.21 solkeedy qokedy otedy sol chedy lkedy qokchedy qokedy chckhdy sar
```

Für genau diesen explorativen Entwurf wurden qoteedy=P, qokedy=Q und chedy=R als **unübersetzte Aussagenplatzhalter** behandelt; qokeey erhielt versuchsweise die Funktion „wenn … dann …“, sol einen Folgerungsanspruch. Die Platzhalter sind keine Stoffe, Klassen oder bestätigten Prädikate. Ihre Wiederholung ersetzt noch keine grammatisch gebundene vollständige Aussage. Die Wahl entstand nach Sichtung des bereits bekannten Textes, nicht blind. Frühere P16-Zustands- und Handlungsbedeutungen wurden nicht übernommen.

Der Ansatz ist eine ausdrücklich begrenzte propositionale Vorstufe zur breiteren IDEA000127. Deren Klassenargumente, Quantoren, bildlich gebundene Zeugen und historische Beweisregister wurden hier **nicht** rekonstruiert oder allgemein geprüft. Auch P16s Bedingungen und seine Widersprüche bleiben unverändert.

Die vor der Auswertung festgelegte [Modellbeschreibung](MODEL.json) legt die nächsten passenden Aussagen links/rechts bis zum nächsten Operator als Operanden fest. Diese Regel ist eine Annahme, keine erkannte Syntax. Überbrückte offene Wörter bleiben sichtbar. Beispielsweise verbindet die Regel außerhalb der Ausgangsstelle auch Wörter über eine Zeilengrenze hinweg; dafür wird keine sprachliche Rechtfertigung behauptet. Kein neuer Decoder und keine Normalisierung verwandter Schreibungen.

## Alle sieben Folgerungsstellen

Wahrheitswerte P/Q/R werden unabhängig in allen acht Kombinationen geprüft. Eine Folgerung muss in jeder mit den bereits gelesenen Voraussetzungen vereinbaren Kombination gelten. Ein gescheiterter früherer Schluss wird nicht als neue Voraussetzung eingeschmuggelt. Zukünftige Behauptungen dürfen frühere Schlüsse nicht nachträglich rechtfertigen.

| sol-Stelle | Ziel | Vorher gebundene Voraussetzungen | Konkretes Gegenbeispiel oder Bindungsfehler |
|---|---|---|---|
| f83r.2:1 | P auf .2:7 | keine | P falsch ist noch möglich |
| f83r.20:5 | Q auf .20:7 | P → Q | P falsch, Q falsch: Bedingung erfüllt, Schluss falsch |
| f83r.21:4 | R auf .21:5 | P → Q; Q auf .21:2 | P falsch, Q wahr, R falsch |
| f83r.37:1 | offen | keine | nächstes sol wird vor einer gewählten Aussage erreicht |
| f83r.42:1 | R auf .42:5 | keine | R falsch ist noch möglich |
| f83r.49:1 | R auf .49:3 | keine | R falsch ist noch möglich |
| f83r.55:1 | offen | keine | Record endet ohne gewählte Zielaussage |

[PROOF_CASES.json](PROOF_CASES.json) enthält sämtliche passenden Wahrheitsbelegungen und Gegenmodelle, nicht nur diese Beispiele. „Keine Voraussetzungen“ bedeutet keine im Entwurf gebundenen Voraussetzungen, nicht keinen vorausgehenden Manuskripttext.

An der stärksten Stelle lautet der Versuch damit:

> [offener Text] Wenn P, dann Q. Folglich [offenes cheeety] Q. [offener Text] Q [offenes otedy]. Folglich R. [weiterer offener Text und Q]

Zwei verschiedene Bindungen fehlen: Für den ersten Schluss würde beispielsweise eine vorherige Behauptung P genügen. Für den zweiten würde zusätzlich eine zuvor ausgedrückte Beziehung Q → R genügen. Das sind **ausreichende mögliche Ergänzungen, keine im Text gefundenen Aussagen und nicht die einzig möglichen Prämissen**. Den unbekannten Wörtern wurden diese Bedeutungen nicht nachträglich gegeben. Auch ein bloß wiederholtes Q wäre noch keine gehaltvolle neue Folgerung.

## Vier Bedingungsstellen, einschließlich der ungünstigen

| qokeey-Stelle | Angebundene Aussagen | Befund des festen Entwurfs |
|---|---|---|
| f83r.5:7 | R auf .4:9 → P auf .5:9 | gebunden, aber sieben offene Zwischengruppen insgesamt; kein Beweis der Anbindung |
| f83r.20:3 | P auf .20:2 → Q auf .20:4 | unmittelbar benachbarte Operanden; Motivationsstelle |
| f83r.25:3 | ? → Q auf .25:4 | linke Aussage fehlt im Record |
| f83r.26:2 | R auf .25:5 → R auf .27:2 | bloße Tautologie; sieben offene Zwischengruppen insgesamt |

Die letzte Stelle zeigt eine Belastung derselben Regel außerhalb der ausgewählten kurzen Folge. Die Hypothese bekommt dort keine neue Sonderfunktion. [OPERATORS.tsv](OPERATORS.tsv) dokumentiert alle elf Operatorpositionen und jede überbrückte Rohposition.

## Vollständige Gegenlesung

Die Fassung U behält Aussagen und Bedingungen bei, liest sol jedoch als Einleitung einer **zusätzlichen Behauptung**, ohne Folgerungsanspruch. Sie behauptet beispielsweise Q nach „Wenn P, dann Q“, statt Q daraus beweisen zu wollen. Das ist logisch möglich, bestätigt aber kein Wort wie „ferner“ oder „und“.

| Ganzer Record | Geschriebene Gruppen | Positionen mit einer Hypothese | Offene Positionen | sol-Ziele gebunden / insgesamt |
|---|---:|---:|---:|---:|
| P1 | 72 | 13 | 59 | 1/1 |
| P2 | 84 | 5 | 79 | 0/0 |
| P3 | 63 | 12 | 51 | 2/2 |
| P4 | 33 | 6 | 27 | 0/0 |
| P5 | 62 | 4 | 58 | 1/2 |
| Q1 | 11 | 2 | 9 | 1/1 |
| Q2 | 16 | 1 | 15 | 0/1 |
| **Alle** | **341** | **43** | **298** | **5/7** |

Beide vollständigen tokengetreuen Entwürfe stehen mit sämtlichen Rohzeilen in [READINGS.md](READINGS.md); [ALIGNMENT.tsv](ALIGNMENT.tsv) enthält 682 Positionszeilen. Vollständig ist die **Wiedergabe des Ausgangstexts**, nicht dessen Übersetzung. Die offenen Wörter können syntaktisch und semantisch entscheidend sein; ihre angezeigten Klammern erlauben nicht, sie als Füllwörter zu streichen.

Alle unbedingten Gegenlesungen sind in diesem schwachen positiven Drei-Aussagen-Modell erfüllbar. Das liefert keine unabhängige Bestätigung: es fehlt eine gebundene Verneinung, und das bloße Weglassen eines Beweisanspruchs erleichtert definitionsgemäß die Passung. Am Recordende haben A und U in sechs Records sogar dieselben noch möglichen Wahrheitsbelegungen, weil spätere bloße Behauptungen die zuvor unbewiesenen Aussagen nochmals liefern oder ohnehin keine Bindung entsteht. Nur Q1 trennt sie: A lässt R offen; U behauptet R. Kein beobachteter Bedeutungsbefund entscheidet diesen Unterschied. Die A-Endzustände sind die **überlebenden gelesenen Prämissen**, kein erfolgreicher Beweis des ganzen Records.

## Entscheidung

**sol = folglich nicht übernehmen; qokeey = wenn/dann nicht übernehmen.** Der konkrete Entwurf liefert keine neue gültige Folgerung und ist als fortführbare Gesamtlesung zu schwach. Keine Negation, kein Quantor, kein Inhaltswort wird übersetzt. Das Modell wird nicht durch zusätzliche freie Bedeutungen repariert. W89s Rezeptpause bleibt bestehen.

Der Erkenntnisumfang ist begrenzt: Der tatsächlich motivierende Wiederholungsanschluss liefert unter dieser ausdrücklich angesetzten Syntax keine Beweiskette. Nicht bewiesen sind allgemeine Unmöglichkeit einer Argumentationslesung, falsche Schlüsse des Schreibers oder die Abwesenheit der benötigten Aussagen in den 298 offenen Gruppen. Die breitere IDEA000127 bleibt ohne diese konkrete Ausführung des historischen und bildlich gebundenen Teils offen; W91 ist kein Ausschluss der ganzen Familie.

Ein neuer Versuch wäre erst ein anderer sinnvoller Kandidat, wenn er eine konkrete geschriebene Prämissenbindung statt derselben freien Lücken liefert. Diese Anforderung ist keine Forderung nach einem vorher bestätigten Wort; sie verhindert lediglich, die fehlenden Aussagen unsichtbar vorauszusetzen. Kein automatischer weiterer Operator-, Fenster- oder Quellentausch wird daraus ausgewählt.

## Reproduktion und Grenzen

Aus der Repositorywurzel:

```
python3 research_registry/proposals/translation_programs_20260912/work/W91/build.py
python3 research_registry/proposals/translation_programs_20260912/work/W91/validate.py
```

[DECISION.md](DECISION.md) entstand vor der vollständigen neuen Quellsichtung; [MODEL.json](MODEL.json) nach der explorativen Sichtung und vor der Konsequenzauswertung. [SOURCE.json](SOURCE.json) bindet die vorhandene P12-Projektion und den neuen selector-first Export. Sieben f83r-Records/51 Zeilen, nur ZL3b in diesem vorhandenen Paket; alternative Transkriptionen liefern hier keine zusätzliche Prüfung. Keine neue Seite, kein Bild, kein Experte, kein Kontakt, keine Reserven. f84/f84r bleiben geschlossen. Vorherige Projektexposition wird ausdrücklich nicht als Unabhängigkeit ausgegeben.

Der zweite lokale Algorithmus rekonstruiert Operanden über abgegrenzte Textsegmente, prüft die Reihenfolge der Prämissen und verwendet Mengen von Wahrheitsbelegungen statt des Builder-Prädikats. Er prüft außerdem alle Ausgangspositionen und die Hashbindungen. PASS bestätigt diese Modellrechnung, nicht ihre semantischen Annahmen; derselbe Root verfasste beide Programme. Kein signifikanter Suchbefund und keine unabhängige Bedeutungsbestätigung. Die Ideenpipeline meldete lediglich eine vorhandene andere Rohidee; sie prüfte weder W91 noch dessen Text.

Primärvorgänger: [P16](../P16/REPORT.md) (bedingte versus unbedingte Aussagen), [GDT611](../../../../../experiments/yolo/gdt611_lexical_slot_permutation_audit/REPORT.md) (semantische Umbenennungsfreiheit; Repositorypfad siehe unten). GDT611 zeigt im damaligen Rollenmodell keine Auswahl konkreter Namen; hier gilt entsprechend: Umbenennen von P/Q/R liefert keine Wörter.

Kanonischer GDT611-Pfad: `experiments/yolo/gdt611_lexical_slot_permutation_audit/REPORT.md`.

Die lokale Validierung und der geprüfte Veröffentlichungsumfang bestehen. Der globale Repositorycheck meldet unverändert sieben ungebundene Reproduktionsdateien in GDT600; diese fremde Altlast wurde nicht verändert und der Gesamtcheck nicht als bestanden ausgegeben.
