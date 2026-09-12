# GDT925 — kein vollständiges Zeilenpaar mit gleicher Wortmenge

Der vorab festgelegte Vergleich wurde tatsächlich ausgeführt. In keiner der
drei Lesungen findet sich unter den zulässigen vollständigen Prosa-Zeilen ein
Paar mit exakt derselben Wortmultimenge. Das gilt sowohl für veränderte als auch
für unveränderte Reihenfolge. Es gibt deshalb keine Kandidatenzeile, die hier
als Umstellung weiterverfolgt werden kann.

| Lesung | Prosa-Zeilen | Zulässig | Unter 2 Gruppen | Nicht ausschließlich wörtliches a–z | Unsichere Naht oder Indexlücke | Paare gleicher Wortmultimenge |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b (primär) | 3768 | 1448 | 10 | 882 | 1428 | 0 |
| IT2a | 3767 | 3177 | 11 | 42 | 537 | 0 |
| RF1b | 3768 | 1201 | 10 | 2142 | 415 | 0 |

Ausschlussgründe werden in der registrierten Reihenfolge vergeben. Mehrere
Lesungen erhöhen nicht die Zahl unabhängiger Manuskripte. Die unterschiedlichen
Zahlen zulässiger Zeilen zeigen eine erhebliche Abhängigkeit von Lesung und
Unsicherheitsnotation; ausgeschlossenes Material wird nicht für inhaltsleer erklärt.

Die [vollständige Kandidatentabelle](CANDIDATE_TABLE.md) enthält entsprechend
keine Treffer. RESULT.json bewahrt sämtliche zulässigen Zeilen-IDs und Zähler;
PAIRS.json und GROUPS.json die leeren Ergebnislisten. Die sechs unveränderten,
bereits zugelassenen GDT915-Snapshots sind im Manifest mit SHA256 gebunden.

## Durchführung und Kontrolle

Die öffentliche Registrierung im Commit74dc1f1b ging der Auswertung voraus.
Das Auswahlprogramm gruppiert nach sortierten Wortlisten mit Wiederholungen.
Ein zweites Programm importiert das erste nicht: Es rekonstruiert die zulässigen
Zeilen und vergleicht jedes gleich lange Paar direkt über Wortzählungen.
Es prüfte104204ZL-,507385IT- und68661RF-Paare, insgesamt680250, und bestätigt
alle Zähler sowie das leere Ergebnis. Zwei künstliche Beispiele kontrollieren,
dass Wortmengen mit unterschiedlichen Häufigkeiten nicht verwechselt werden.
Das ist eine unabhängige Implementationskontrolle, keine unabhängige
Manuskript- oder Bedeutungsbestätigung.

## Entscheidung und Grenzen

Die genaue Suche ist beendet. Keine kürzeren Ausschnitte, Wortlöschungen,
Normalisierungen oder gelockerten Nahtregeln werden nachgeschoben. GDT838,
GDT918 und ETR001 bleiben unverändert. IP036 ist hier ausdrücklich nicht als
semantischer Umstellungstest ausgeführt: unabhängige Zusammengehörigkeit wäre
zusätzlich nachzuweisen, selbst wenn eine Wortmenge zweimal vorkäme.

Dieser Befund besagt nicht, dass Voynich keine flexible Wortstellung,
Paraphrasen, wiederholten Inhalte oder Sprache enthält. Physische Zeilen sind
keine gesicherten Sätze; exakte Wiederholung ganzer Zeilen kann auch in einem
gewöhnlichen Text selten sein. Es wurde kein Zufallsvergleich der gesamten
Suche gerechnet und keine Signifikanz behauptet. Alle Daten waren bereits
projektweit exponiert; unabhängige Bestätigungskapazität dieses Durchgangs:0.

Bestätigte Wortbedeutungen: **0**. Keine neue Bildzulassung; f84/f84r geschlossen.
