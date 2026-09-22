# GDT1034: notwendige Kapazität eines gemeinsamen Galen-Wortcodes

## Frage und Entscheidung vor der Zählung

Könnte irgendeine neue globale Einzelwertbelegung die vier bereits vollständigen
Galen-Projektionen II/III/IV/V gemeinsam realisieren? Die alten Glossen werden
als Wortzuweisungen vollständig freigegeben. Ihre vollständigen semantischen
Inventare bleiben fixiert: II49 + III46 Positionen in Familie A und IV55 + V33
Positionen in Familie B. Keine neue Quelle, Absatzwahl, Zerlegung, Auslassung
oder zusätzliche Wortposition. Die originalen getrennten Entwürfe werden nicht
überschrieben; insbesondere hatten sie keinen gemeinsamen Code behauptet.

Die offene Frage unterscheidet sich vom bereits geprüften Schnitt der13
alten Wortzuweisungen. GDT1007/1008 zeigen, dass Konflikte einzelner gespeicherter
Belegungen keine Unmöglichkeit aller gemeinsamen Neubelegungen beweisen.
GDT901 liefert den notwendigen Inzidenz-Präzedenzfall. Hier wird ein noch
schwächerer, kleiner, zertifizierbarer Test verwendet, kein neuer Decoder.
Vorbereitung, Quellprüfung, Ausführung, Validierung und Veröffentlichung sind
zusammen von11:09 bis11:54UTC begrenzt. Danach keine automatische Erweiterung.

## Unveränderte Quelle und gelockerte Zuordnung

RAW496/500 liefern67 A-Einträge, RAW499/501 liefern59 B-Einträge. Maßgeblich ist
bei A qoky die bereits in RAW500 offengelegte breitere NO-Denotation; GDT1028
bleibt historisch unverändert. Jeder bisher bezahlte lexikalische Ausdruck
bleibt ganz: etwa THOROUGH_REBOIL, BOTH_THUS_PREPARED und GOOD_JUICED werden nicht
zerlegt. Implizite Argumente, Topic-Rückverweise und intrinsische Juice-Profile
werden nicht als zusätzliche Wörter gezählt. Die beiden V-Rekapitulationen
bleiben ausdrücklich Teil des vorhandenen Inventars.

Angenommen wird eine Funktion M von exakter Wortschreibung zu einer einzigen
vollen lexikalischen Denotation. Beliebig viele verschiedene Schreibungen
dürfen dieselbe Denotation tragen. **Keine Injektivität und kein Synonymverbot.**
Jede der183 Wortgruppen realisiert genau eine der183 Quellrealisierungen.
Innerhalb einer Familie dürfen sämtliche Realisierungen beliebig umgeordnet
werden, auch zwischen deren zwei Absätzen. Satzgrammatik, Reihenfolge,
Referenzbindung und Morphologie werden nicht eingeschränkt. Das ist eine
notwendige Relaxation einer vollständigen gemeinsamen Lesung, selbst keine Lesung.

Verglichen werden lexikalische Denotationen vor Auflösung von Referenzen.
THIS_FOOD kann in einem Satz Kohl aufgreifen, ohne dieselbe lexikalische
Denotation wie CABBAGE zu besitzen. Eine gleiche ausgegebene Entität ersetzt
keine gleiche Funktion. Gleichzeitig werden nicht sicher getrennte Funktionen
in COMPATIBILITY.json absichtlich großzügig als mögliche Paarungen zugelassen.
Jede zusätzliche Kante macht einen Widerspruch schwieriger, nicht leichter.
Die vollständige Quellprüfung und alle zulässigen Kanten werden vor Zielzählung
versiegelt. Die Vollständigkeit dieser semantischen Übermenge ist eine explizite
inhaltliche Voraussetzung, kein vom Computer bewiesenes Resultat.

## Kurzer notwendiger Beweis

Für jede Schreibung w seien a(w), b(w) ihre Häufigkeiten in den beiden Familien.
Eine gemeinsame Zuordnung verlangt für diese Schreibung mindestens
min(a(w), b(w)) disjunkte A/B-Positionspaare gleicher Denotation. Verschiedene
Schreibungen belegen verschiedene Positionen, auch wenn sie synonym sind.
Daher induziert jeder gemeinsame Code ein Matching der Größe

    K = Summe_w min(a(w), b(w)).

Der Quellgraph hat alle95 A- und88 B-Positionsknoten, mit einer Kante genau dann,
wenn deren Einträge in der vorher fixierten Kompatibilitätsübermenge liegen.
Jeder echte gemeinsame Code muss somit K <= nu(G) erfüllen, wobei nu die maximale
Matchinggröße bezeichnet. Gematchte Positionspaare und ein gleich großes
Vertex-Cover werden ausgegeben. Ein unabhängiger Prüfer braucht keinen Solver:
Er kontrolliert jede Kante, Disjunktheit, vollständige Kantenabdeckung und die
gleichen Größen. Matching liefert die Untergrenze, Cover die Obergrenze.

Zusätzlich wird vor Lock eine notwendige Wiederholungsbedingung fixiert.
B_POOLS.json partitioniert alle59 B-Einträge in quellseitig geprüfte Pools:
bekannte Synonyme werden vereinigt; ungeklärte Gleichheiten werden vorsorglich
zusammengefasst, auch wenn damit tatsächlich verschiedene Bedeutungen in einen
Pool gelangen. Diese Pools behaupten keine neuen lexikalischen Gleichheiten.
Für jeden Pool v seien b_v sämtliche B-Quellpositionen dieses Pools und a_v
sämtliche EINDEUTIGEN A-Quellpositionen mit mindestens einer erlaubten Kante
in diesen Pool. Ein global bedeutungskonstantes geteiltes Wort w muss mindestens
einen Pool mit a(w)<=a_v und b(w)<=b_v besitzen. Alle geteilten Wörter beider
Panels werden auf alle Pools geprüft. Eine leere notwendige Domain schließt
den gemeinsamen Code aus. Ein nichtleerer Pool ist kein Wörterbuchzeuge; die
übrigen Wörter dürfen denselben Quellvorrat in dieser Relaxation unabhängig
beanspruchen. Es gibt weder eine neue A-Quotientierung noch einen großen Solver.

Die beiden Kriterien werden gemeinsam vor der ersten Ausführung registriert.
Die Ergänzung entstand während der source-only Prüfung, nicht nach einem
Matchingresultat. Die Ziele und13 gemeinsamen Schreibungen waren schon bekannt;
überschlägige Überlegungen zu Wiederholungen sind Teil der offen nach Exposition
erfolgten Entwicklung. Keine blinde Vorhersage wird behauptet.

**Leere notwendige Wortdomain: REFUTED_FIXED_SHARED_CODE.**

**K > nu(G): REFUTED_FIXED_SHARED_CODE.** Keine kontextfreie Einzelwertbelegung,
auch mit unbegrenzten Aliaswörtern und völlig freier Syntax, realisiert diese
vier fixen Inventare unter dem registrierten Vergleichsvertrag.

**K <= nu(G) und alle notwendigen Domains nichtleer: NO_DECISION.** Weder gemeinsames Wörterbuch noch Satzlesung oder
Bedeutungsbestätigung gefunden. Keine automatische Erweiterung zu einem großen
Solver, neuer Atomzerlegung oder anderen Absätzen. Ein Fehler/ungeklärtes Loch
im Quellvertrag führt zu INVALID/CONTRACT_UNRESOLVED, nicht zu einer Widerlegung.

## Vollständiger Zielumfang und Unsicherheit

Exakt vier bereits exponierte komplette ZL3b-Absätze aus dem eigenen GDT928-Paket:
f107v.45–49, f111r.44–47, f76v.37–41, f80v.19–22. Vor Wortzugriff Auswahl nach
exakter Absatz-ID, Zurückweisung f84-Präfix und f116v. Alle183 Rohgruppen und
Quell-IDs müssen mit den alten vollständigen Receipts übereinstimmen. Die Literalprüfung schützt vor unklaren Wortwerten in ausgeschlossenen Zeilen,
beweist jedoch weder unbekannte Gruppengrenzen noch die Richtigkeit der
übrigen Transkription. Keine
Normalisierung, Substringanalyse, alternative Transkription oder neue Bildlektüre.

Zwei vorab festgelegte Konsequenzen verwenden dieselbe volle Quellobergrenze:

* RAW_EXACT: sämtliche exakten Rohgruppen, mit allen Unsicherheiten unverändert.
  Ein Widerspruch gilt bedingt auf dieser Rohlesung.
* LITERAL_LINES: ausschließlich Zielvorkommen aus Zeilen mit anchor_eligible
  exakt True tragen zur Mindestanforderung K bei. Trotzdem bleiben alle183
  Quellpositionen als mögliche Kapazität verfügbar. Dies ist eine zusätzliche
  konservative Unsicherheitsprüfung, keine nachträgliche Textreparatur.

Auch alle nicht geteilten Wörter erscheinen mit ihren Nullhäufigkeiten in der
Tabelle. Alle vier Absatzinhalte und die13 gemeinsamen exakten Worttypen waren
bereits im Projekt bekannt; das ist ein nach Exposition registrierter Test.
Die neue Häufigkeitsrechnung und die Quellobergrenze werden erst nach öffentlichem
Lock ausgeführt. Kein unabhängiger Holdout, kein bestätigter Pflanzenname.
Die alternativen Transkriptionen sind weiterhin andere Lesarten desselben
Manuskripts; ihre bekannten Abweichungen werden nicht als Wiederholungsstudien
bezeichnet. f84/f84r und sämtliche Reserven bleiben geschlossen.

## Reproduktion und Geltungsgrenze

SPEC.json bindet alle Quellen und vier Absätze. ENTRIES.json erhält jeden alten
Eintrag; COMPATIBILITY.json bindet alle Paarungen und ihre begründete Relaxation.
PREREG_LOCK.json bindet Programme, Methode und Quellen. run.py --self-test liest
keinen Zieltext und prüft581 kleine vollständige Graphen gegen eine exhaustive
Referenz sowie den Fall unbeschränkter Synonyme. Der Validator wird unabhängig
vom Primärprogramm geschrieben; er prüft die gesamte Rechnung und Zertifikate.

Dieser Test könnte eine gemeinsame Lesart verwerfen, bestätigt aber kein einziges
Wort. Er schließt weder Galen-Inhalt allgemein, historische medizinische Sprache,
eine kompositionelle Schrift noch kontextabhängige Werte aus. Selbst ein echter
Widerspruch rechtfertigt keinen beliebigen Kontextschalter zur Rettung. Es gibt
keine Gegenkontrolle der gesamten historischen Suche und keine Signifikanzangabe.
