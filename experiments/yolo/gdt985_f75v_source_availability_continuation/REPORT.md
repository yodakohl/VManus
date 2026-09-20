# GDT985 — sheolo trägt bedingt eine Rückführung

**Unter der neuen Annahme eines einzigen weitergeführten Gegenstands und
aktueller Quellenangaben muss `sheolo` auf f75v.41 einen Wechsel von B nach A
bewirken. Die gesamte Fortsetzung .40–42 lässt diese Rolle zu. Drei verschiedene
Effekttabellen bleiben möglich; kein Wort und keine der früheren Satzfassungen
ist dadurch als Bedeutung ausgewählt.**

Der konkrete Gewinn ist eine ausgeführte Folgerung über ein bisher ungelesenes
Wort innerhalb eines größeren Zusammenhangs. Die Einschränkung entsteht aber
unter einer neuen, starken Konstruktionsthese: `ol` und `or` prüfen den aktuellen
Ort derselben Portion. Eine bloße Quellenbeschreibung, verschiedene Portionen
oder eine andere Satzstruktur würden diese Folgerung nicht tragen.

[Alle fünf vollständigen Quellzeilen je Lesung, sämtliche Wortdomänen und alle
Kandidaten](artifacts/READING_OBLIGATIONS.md) sind lesbar zusammengestellt.
Die [Kandidatentabelle](artifacts/CANDIDATE_TABLE.tsv) und
[Worttabelle](artifacts/WORD_DOMAINS.tsv) behalten alle Fälle, auch fehlende
Prüfkapazität. Die öffentliche Registrierung erfolgte in `0e84d2d1c` vor dem
Solverlauf. Die Ausgangstexte und der nachstehende kurze Zusammenhang waren
vorher bekannt; diese Arbeit wird nicht als blinde Entdeckung ausgegeben.

## Was die neue Lesung zusätzlich voraussetzt

GDT982s unveränderte ganze .39-Fassungen setzen eine Portion und zwei Orte voraus.
„Danach, einmal“ und „danach, wiederholt“ enden in B; „nicht, einmal“ endet in A.
„Nicht, wiederholt“ scheiterte bereits früher. Die beschreibende Fassung behauptet
keine ausgeführten Bewegungen.

GDT985 ergänzt für die anschließenden **34 geschriebenen Gruppen**:

- Dieselbe unteilbare Portion bleibt Gegenstand; kein verdeckter Nachschub oder
  Wechsel des Teilnehmers.
- Jede ganze Form `ol` verlangt ihre Verfügbarkeit in A, `or` in B. Die Prüfung
  selbst bewegt nichts. Das ist eine neue Syntax-/Identitätsannahme und folgt
  nicht bereits aus der alten deutschen Glosse „von“.
- `qol` und `sheedy` behalten hypothetisch Portion/Flüssigkeit und ändern den Ort
  nicht. Die übrigen **16 verschiedenen Ganzformen** erhalten je eine gemeinsame
  partielle Zweizustandsfunktion; jede Wiederholung verwendet dieselbe Tabelle.
- Jede geschriebene Gruppe wird berücksichtigt; über Zeilengrenzen läuft derselbe
  Zustand weiter. Kein stiller Transport findet am Zeilenumbruch statt.

Für jedes ungelesene Wort sind zunächst alle neun möglichen partiellen Tabellen
zugelassen. Eine undefinierte tatsächlich benötigte Anwendung scheitert. Eine
Tabelle ist nur eine Wirkung auf den hypothetischen Ort, kein vollständiger
Wortwert, kein Satzbau und kein neuer allgemeiner Decoder. GDT982, W56/W58/W59
und alle alten Wortglossen bleiben unverändert.

## Konkrete Konsequenz und vollständige Kontrolle

IT2a endet auf .41 mit `… chl or sheolo`; .42 beginnt `ol sheey …`.
Nach dem angesetzten `or` ist die Portion in B, vor dem angesetzten `ol` muss
sie in A sein. Dazwischen steht genau **sheolo**. Also muss seine Tabelle B→A
enthalten. Der vollständige Zusammenhang mit allen anderen Wiederholungen ist
erfüllbar, sowohl nach einem Eintritt aus A als auch nach einem Eintritt aus B.

| Verbleibende sheolo-Tabelle | Bei Eingang A | Bei Eingang B | Mögliche Wirkungsskizze |
|---|---|---|---|
| Code 0 | bleibt A | wird A | nach A setzen |
| Code 3 | wird B | wird A | zwischen den beiden Orten wechseln |
| Code 6 | nicht anwendbar | wird A | nur von B nach A zurückführen |

Diese Skizzen sind keine drei entzifferten Wörter. Hier wird sheolo nur mit
Eingang B gebraucht; sein Verhalten bei Eingang A bleibt unbestimmt. Eine
weltweite Vertauschung der Ortsnamen ändert den Befund nicht. „Zurück“ hätte
außerdem einen Bezugsort nötig, den das Manuskript noch nicht unabhängig bindet.

Ein zweiter, vollständigkeitshalber berichteter Zwang ist `ol shey ol` auf .41:
unter demselben Vertrag muss **shey bei Eingang A den Ort A erhalten**. Sein
Verhalten bei B bleibt ebenfalls offen. Daraus wird weder ein Stoffname noch
„gleich“, „dieses“ oder eine andere Bedeutung abgeleitet.

Alle Wortdomänen wurden gerechnet, nicht nur diese anschaulichen Brücken:
**294 Existenzfragen**, davon 208 erfüllbar und 86 unerfüllbar, keine ungelöst.
Das sind 2 Anfangszustände × (1 Gesamtfrage + 16 Wörter × 9 Tabellen + 2 Endorte).
Jede positive Frage besitzt eine vollständige gemeinsame Tabellenbelegung und
alle 35 Zustandsgrenzen. [QUERIES.json](artifacts/QUERIES.json) erhält sämtliche
Zeugen und negativen Entscheidungen. Die Wortdomänen sind Randmengen: Beliebig
zusammengestellte Werte aus verschiedenen Tabellenzeilen müssen nicht gemeinsam
passen.

`qokain` kann in beiden Eingangsklassen weiterhin jede der acht nicht völlig
undefinierten Tabellen haben. Dieser Test identifiziert also insbesondere
keine Kopula, Flüssigkeit oder Rückkehrbedeutung für dieses häufige Wort.
Auch der Endort bleibt jeweils A **oder** B. Die frühere Verzweigung ist nicht
aufgelöst.

## Alle Kandidaten und Lesungen

| Übernommene Fassung | IT2a-Konsequenz | Verbleibende Mehrdeutigkeit |
|---|---|---|
| danach + wiederholt | Fortsetzung erfüllbar; sheolo B→A nötig | Codes 0/3/6; Endort A/B |
| danach + einmal | ebenso | hier vollständig dieselbe Eingangsklasse wie wiederholt |
| nicht + einmal | ebenfalls erfüllbar; sheolo B→A nötig | Codes 0/3/6; Endort A/B |
| nicht + wiederholt | alter Widerspruch bleibt | kein neuer GDT985-Ausschluss oder Reparatur |
| Beschreibung | nicht als Prozess bewertet | keine behauptete aktuelle Position; weiterhin eigener Rivale |

ZL3b enthält den ganzen Absatz, aber alle drei Fortsetzungszeilen sind nach den
alten Quellflags nicht vollständig zulässig. Es schreibt insbesondere `o | l`
am Beginn .42. Das wird nicht zu `ol` vereinigt. RF1b liefert nur das erhaltene
Zeilenfenster, keinen im Cache markierten vollständigen Absatz. Beide erhalten
**NO_CAPACITY** für diese feste Fortsetzungsprüfung, keine negative oder positive
Bedeutungsentscheidung. Die 15 Tabellenzeilen sind fünf Hypothesen × drei
Transkriptionen eines Manuskripts, keine 15 unabhängigen Tests.

Der [Quellpacket](artifacts/SOURCE_PACKET.json) erhält alle Rohgruppen,
Quell-IDs, Abstände, Entitäten, Metadaten und Absatzflags: ZL59/IT59/RF58 Gruppen
in jeweils fünf Zeilen. .38 bleibt ungelesen; .39 behält die alten bedingten
Fassungen. Auch die neue Fortsetzung ist **keine vollständige Übersetzung**:
Eine mögliche Zustandswirkung füllt die Bedeutung eines unbekannten Wortes
nicht aus.

## Prüfung, Entscheidung und Anschluss

Ein eigenständiger endlicher Constraint-Prüfer verwendet weder Z3 noch den
Runner. Er prüft alle 294 Fragen durch Domänenreduktion und Rückwärtssuche und
konstruiert eigene positive Zuordnungen. Alle 208 gespeicherten und unabhängig
erzeugten positiven Zeugen werden direkt an jeder einzelnen Gruppe geprüft.
32 Wortdomänen, 15 Kandidatenzeilen und sämtliche Rohtexte stimmen: **PASS**.
758 kleine synthetische Fälle wurden vor Zielrechnung geprüft. Die Hauptrechnung
dauerte 4,225 Sekunden, die Gegenprüfung 1,601 Sekunden. Derselbe Autor; dies
ist keine unabhängige Bedeutungsprüfung.

**Behalten wird nur die bedingte Rolle:** Falls der ganze neue Quellen-/Identitäts-
vertrag zutrifft, muss sheolo hier den Rückweg tragen. Das kann eine gezielte
weitere Lesung anleiten. Es rechtfertigt weder `sheolo = zurück` als Wörterbuch-
eintrag noch eine Bevorzugung der Prozesslesung gegenüber der Beschreibung.
Die Voraussetzung selbst ist der stärkste offene Punkt.

Der nächste brauchbare Inhaltsschritt muss eine vollständige Konstruktion
zeigen, die Quelle, denselben Teilnehmer und Wirkung gemeinsam bindet. Ein
weiteres Vorkommen von sheolo, eine erfundene Zustandsbahn oder eine globale
Suche nach `ol X or` genügen dafür nicht. Keine automatische Erweiterung dieses
Zweizustandsmodells. Der parallel entwickelte IDEA370-Entwurf koppelt zwei
vollständige Sätze durch dieselbe Materialbeschreibung; er wird als nächstes an
seinen Primärtexten und vollständigen Absätzen beurteilt, nicht schon bestätigt.

Alle Daten waren bereits exponiert. Ein physisches Auswahlblatt, null unabhängige
Bestätigungsblätter, null bestätigte Wörter, keine Signifikanz und kein
scorefähiger Relationsbeleg. Keine neue Aufnahme, Reserveöffnung oder Kontakte;
f84/f84r/f116v bleiben geschlossen. Der globale Check behält die bekannten acht
Altfehler von GDT600/GDT953; der neue Arbeitsumfang wird separat geprüft.

Auswahl begann 00:00 UTC am 20. September; Rechnung und Gegenprüfung waren vor
00:09 UTC beendet. Der inklusive Checkpoint ist 00:40 UTC. Der Zehnstundenblock
begann am 19. September 23:05:26 UTC und läuft bis frühestens 09:05:26 UTC weiter.
