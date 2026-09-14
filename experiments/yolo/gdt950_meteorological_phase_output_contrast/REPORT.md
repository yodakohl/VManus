# GDT950 — Wetterbegriffe unter einer festen Ergebnisregel

**Die Kombination „kondensieren/gefrieren + genanntes Ergebnis“ scheitert in
ZL3b und IT2a an zwei verschiedenen wiederholten Ergebnisformen.** RF1b lässt
wegen abweichender Rohlesungen weniger Fälle prüfen und lässt72 Kandidaten
offen. Kein Wetterwort ist dadurch gelesen. Die allgemeine Wetterhypothese
und die einzelnen möglichen Wortbedeutungen sind damit nicht widerlegt.

Die [Kandidatentabelle](artifacts/CANDIDATE_TABLE.tsv) enthält jede der240
festgelegten Zuordnungen, beide Verbrichtungen, alle Widerspruchs-IDs und ihre
Mehrdeutigkeitsklasse. [Alle einzelnen Konsequenzen](artifacts/CONSEQUENCES.tsv),
[vollständige Quellzeilen](artifacts/COMPLETE_MATCHING_LINES.json) und
[die vorab eingefrorenen Wortwerte/Vorhersagen](src/CANDIDATES.json) erlauben
die direkte Kontrolle. Die240 Kombinationen sind keine240 unabhängigen Ideen:
Der tatsächlich beobachtete Test unterscheidet nur vier Vorhersageklassen.

## Was die Lesung konkret behauptete

Die zwei ganzen Formen qokeedy und qoteedy sollten einmal „kondensieren“ und
einmal „gefrieren“ bedeuten; beide Richtungen wurden festgelegt. Die vier alten
Nominalpaare erhielten alle injektiven Belegungen mit vier von fünf Begriffen:
Tau, Regen, Reif, Schnee, Hagel. Zum Beispiel konnte otedy „Tau“ heißen und
qotedy „als Ergebnis Tau“. Es wurde kein allgemeiner q-Decoder gebaut.

Der entscheidende Zusatz war eine ausdrücklich angenommene Konstruktion:
Ein solches q-Wort unmittelbar nach einem der zwei Verben nennt dessen
Ergebnis. Kondensieren sollte hier flüssiges Wasser hervorbringen, Gefrieren
einen festen Niederschlag. Das sind die engeren, atomaren Lesungen dieses
Versuchs. Eine anschließende zweite Operation war nicht stillschweigend Teil
des Verbs. Die historische Motivation steht im [Quellenvertrag](src/HISTORICAL_CONTRACT.md).
Die genaue einschlägige Aquinas-Stelle liegt in I.14–15; I.13 behandelt noch
die Milchstraße und trägt keine Ergebnisbedingung bei.

## Der tatsächlich geprüfte Unterschied

| Ganze geschriebene Folge | ZL3b-Stellen | Bedingung unter kondensieren / gefrieren |
|---|---|---|
| qokeedy qotedy | .14, .27, .42 | qotedy müsste flüssig sein |
| qoteedy qotedy | .43 | dieselbe benannte Erscheinung müsste fest sein |
| qokeedy qokaiin | .26 | qokaiin müsste flüssig sein |
| qoteedy qokaiin | .11, .14 | dieselbe benannte Erscheinung müsste fest sein |

Alle Stellen gehören zu f77r. Beim Vertauschen der zwei Verben tauschen sich
flüssig und fest; der Widerspruch bleibt. Dazu muss kein gleicher Stoffvorrat
über mehrere Zeilen fortgeführt werden: Ein fest gewählter Erscheinungsname
hat bereits seinen angenommenen Zustand. Zwei verschiedene Schneeportionen
wären unter diesem Modell beide fest.

Ein konkretes Beispiel ist M001: otedy=Tau, otol=Regen, otaiin=Reif,
okaiin=Schnee, qokeedy=kondensieren und qoteedy=gefrieren. Die Folge auf .27
wäre bedingt „kondensiert zu Tau“, auf .43 dagegen „gefriert zu Tau“.
Die .26-Folge wäre zusätzlich „kondensiert zu Schnee“. Die Fehler wurden
nicht durch eine neue Bedeutung von Tau, Schnee oder den Verben beseitigt.
Alle anderen Wörter bleiben sichtbar ungelesen; dies ist keine vollständige
Satz- oder Absatzübersetzung.

## Vollständiger Umfang und Varianten

| Lesung | Rohgruppen im gesamten Paket | passende Ergebnispaare auf f77r | andere Verbstellen ohne passende Ergebnisgruppe | widerspruchsfreie Kandidaten |
|---|---:|---:|---:|---:|
| ZL3b | 477 | 7 | 22 | 0/240 |
| IT2a | 464 | 7 | 23 | 0/240 |
| RF1b | 467 | 3 | 24 | 72/240 |

Die Rohgruppen umfassen f77r und die vier bereits exponierten HERB4-Absätze.
Alle17 qualifizierenden Paare,69 nicht aufgelösten Verbstellen und alle
zugehörigen ganzen Zeilen sind erhalten. Die nicht aufgelösten Stellen
gelten nicht als richtige Vorhersagen. Sie verbieten eine behauptete ganze
Lesung, werden aber nicht zusätzlich als Phasenfehler gezählt.

RF1b schreibt auf .14/.42/.43 qote@152;y und auf .26 qokee@152;y. Diese
Formen wurden nicht normalisiert. Übrig bleiben dort zweimal qoteedy qokaiin
und einmal qokeedy qotedy. Die72 offenen Zuordnungen bilden nur eine Klasse
für diese beobachtbaren Konsequenzen. Ihr Fortbestehen stammt aus fehlenden
gleichartigen Prüffällen, nicht aus einer unabhängigen Bedeutungsbestätigung.
Die nachträgliche [native Bildkontrolle](src/NATIVE_RECHECK.md) löst diese
Transkriptionskonvention nicht unabhängig auf und verändert die Rechnung nicht.

## Verbleibende Mehrdeutigkeit und Bestätigungskapazität

| Tatsächlich unterscheidbare Klasse | Kandidaten | Widersprüche ZL / IT / RF |
|---|---:|---:|
| O01 | 72 | 5 / 5 / 3 |
| O02 | 48 | 3 / 3 / 2 |
| O03 | 48 | 4 / 4 / 1 |
| O04 | 72 | 2 / 2 / 0 |

Der Test unterscheidet innerhalb derselben Phase weder Tau von Regen noch
Reif von Schnee oder Hagel. otol/qotol und otaiin/qotaiin kommen in keiner
der qualifizierenden Ergebnispositionen vor. Ihre Bedeutungen bleiben in
diesem Test unbeobachtet. Die14 Klassen für alle acht theoretisch möglichen
Verb/Ergebnis-Kombinationen reduzieren sich deshalb auf vier Klassen für
die tatsächlich17 gelesenen Fälle. Die Listen stehen in
[OBSERVED_PREDICTION_CLASSES](artifacts/OBSERVED_PREDICTION_CLASSES.json).

Die zusätzlichen physischen Blätter f17, f21, f32 und f29 liefern unter der
vorab festgelegten Regel **null** passende Ergebnispaare. Ihr formales
„kein Widerspruch“ ist eine leere Prüfung. Darüber hinaus sind auch diese
Texte projektexponiert. Unabhängige Bedeutungsbestätigungskapazität: null.

## Entscheidung

Diese Phasenverb-/Ergebniskonstruktion wird nicht als Lesung weitergebaut.
Eine andere Referenz- oder Satzgrenzenregel wird nicht nachträglich zur
Rettung eingeführt. Insbesondere gewinnt eine weniger verpflichtende
Flusslesung nicht einfach dadurch, dass sie keinen Phasenwechsel vorhersagt.

Der kleine Versuch hat eine wirkliche Textfolge gegen eine zusätzlich festgelegte
inhaltliche Konsequenz geprüft. Er hat kein neues Wort übersetzt und keine bestimmte
Wetterdeutung ausgewählt. Die strengere Schlussfolgerung „diese Wörter
können niemals kondensieren/gefrieren heißen“ wäre falsch: Auch die hier
angenommene Ergebnisbindung kann falsch sein. Eine künftige Wiederaufnahme
braucht eine anders begründete beobachtbare Konstruktion, keine neue
Permutation derselben fünf Namen.

Die [Präregistrierung](PREREGISTRATION.md) nennt die bereits bekannten
Motivationsstellen. Alle Quellen waren exponiert; keine Signifikanzrechnung,
Reserveöffnung, neue Manuskriptquelle oder Kontaktaufnahme. Alte Experimente
und deren Befunde sind unverändert. Root entwickelte und berechnete das
Modell; die getrennte Validierung prüft Reproduktion und Quellenabdeckung,
keine Wortbedeutungen. [Ergebnis](artifacts/RESULT.json),
[Validierung](artifacts/VALIDATION.json).

## Spät gefundene Vorläufer

GDT817/818 hatten bereits Kondensation und eine ganze geratene Wetterzeile
behandelt; GDT820 ergänzte räumlichen Aufstieg. Diese Primärberichte wurden
erst nach der Rechnung wiedergefunden und vor Veröffentlichung geprüft. Neu
ist hier nur die engere Phasen-/Ergebniskonjunktion. Wetter ist keine neue
Projektidee. Der [späte Abgleich](src/LATE_PREDECESSOR_AUDIT.md) legt den
Suchfehler und den genauen Unterschied offen; die Präregistrierung bleibt
unverändert.
