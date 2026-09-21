# GDT1024: zwei vollständige projizierte Absätze mit festen Musikbedeutungen

Der neue 33-Gruppen-Absatz ist mit dem bisherigen vollständigen 62-Gruppen-Absatz
unter allen zwölf festgelegten Aufführungsbedingungen vereinbar. Alle 53 alten
Wortwerte, vierzehn alten Satzkonstruktionen und Teilnehmerregeln bleiben genau
erhalten. Das ergibt eine **95-Gruppen-Arbeitshypothese**, keine bestätigte
Musikübersetzung. Tatsächlich kommen nur sechs alte Worttypen an neun neuen
Positionen wieder; für den Rest wurden 18 neue Bedeutungen und sechs neue
Konstruktionen angenommen.

[Alle 95 Positionen](artifacts/ALL_POSITIONS.tsv),
[sechs wiederverwendete Wörter mit beiden Kontexten](artifacts/REUSED_WORDS.tsv),
[alle 60 Modellfälle](artifacts/CANDIDATES.tsv),
[öffentliche Vorhersagen](artifacts/PREDICTIONS.tsv),
[vollständige neue Bindungen](artifacts/GRAPHS.json),
[alle Klauselergebnisse](artifacts/ROWS.json).

## Vollständige neue Arbeitslesung

Die beiden projizierten Absätze f83r.25–30 und .31–44 werden als Angaben zur
selben Aufführung gedeutet. Der bisherige volle Text steht unverändert im
[GDT1022-Bericht](../gdt1022_rota_complete_persistent_performance/REPORT.md).
Der vollständige neue Vorspann lautet unter den geratenen Bedeutungen:

1. Zum anfänglichen Zeitpunkt setzt der einzige beginnende Kanonsänger zusammen
   mit beiden Begleitstimmen ein.
2. Zu diesem Zeitpunkt schweigen die übrigen, noch nicht eingetretenen Kanonsänger.
   Der einzige Beginner ist der führende Sänger derselben, anschließend beschriebenen Aufführung.
3. Nochmals dieser Einsatz am Anfang: Die erste, dann die andere Begleitstimme beginnt dort.
4. Die obere Begleitstimme hat eine Schlusspause; ihr erster Beginn fällt mit dem
   führenden Sänger zusammen. Sie behält ihren eigenen Wiederholungsablauf.
5. Die untere Begleitstimme pausiert im Inneren, hat keine Schlusspause, beginnt
   unmittelbar erneut und behält ihren eigenen Wiederholungsablauf.
6. Begleitstimmen und Kanonsänger sind beim Anfang zwei verschiedene Gruppen;
   die noch nicht eingetretenen Kanonsänger schweigen.

Der neue Entwurf erläutert weitgehend den bereits angenommenen Aufführungsbeginn.
Der Rückgriff auf dieselbe Aufführung, die Wiederaufnahme desselben Einsatzes,
der Cursor über die zwei Begleitstimmen und mehrere Synonyme sind ausdrücklich
neue Annahmen. Kein zweiter Leiter, keine neue Melodie und kein Ersatz der alten
Wortbedeutung werden zur Ausführung ergänzt.

## Was tatsächlich geprüft wurde

| Modell | kohärent | widersprochen | konkrete Konsequenz |
|---|---:|---:|---|
| Feste gemeinsame Lesung | 12 | 0 | Beide Absätze beschränken dieselben Rollen und vollständigen Abläufe |
| COMPANIONS als Begleitstimmen | 0 | 12 | Verändert die alte Rollengruppe und verletzt die ausdrücklich geforderte Trennung |
| Jede Erwähnung führt den Einsatz neu aus | 0 | 12 | Bei der vierten Aktion würde R0 zum zweiten Mal erstmals einsetzen |
| Beide Iteratoraufrufe liefern U | 0 | 12 | U,U verbraucht die geforderte geordnete Liste U,L nicht vollständig |
| Bei jedem Hauptmelodiebeginn gemeinsamer Neubeginn | 9 | 3 | C0/C1/C3 vereinbar, C2 widerspricht; beim Zeitpunkt144 hat der23er-Zyklus Phase6 |

Alle 60 vorher registrierten Ergebniserwartungen stimmen. Die drei widersprochenen
Fälle des letzten Modells sind die drei Sängerzahlen bei C2. Das wählt keine
historische Rhythmusvariante: Die eigentliche Lesung fordert nur den gemeinsamen
ersten Beginn und bleibt mit allen vier Varianten vereinbar.

Die doppelte Wortfolge `shckhedy shckhedy` erhält denselben angenommenen Operator
START_NEXT_PES: erster Aufruf U, zweiter L, Cursor danach erschöpft. Das ist ein
expliziter kontextabhängiger Verweis, keine zwei verschiedenen Wortglossen. Auch
die beiden `chedy`-Erwähnungen des neuen Absatzes behalten ENTER; das neue `dain`
behauptet ausdrücklich die Wiederaufnahme desselben ersten Ereignisses.
Ohne diese neue Satzannahme wäre das keine gelöste Ereignisbindung.

Die Gegenmodelle sind genaue Diagnosen dieser Festlegungen. Statische Rollen-
und Aufzählungswidersprüche wurden nicht als vollständige alternative Aufführungen
ausgegeben. Beim doppelten Einsatz stoppt die notwendige Vorprüfung am ersten
bereits aktiven Ereignis. Das U,U-Modell lässt die alte Elternvorschrift, die L
beginnen lässt, bestehen; sein Fehler ist die neue unvollständige Aufzählung,
nicht ein behauptetes Fehlen von L in der unveränderten alten Aufführung.

## Der wirkliche Transkriptionsgegenfall bleibt bestehen

IT f83r.29 beginnt mit `solchedy`. Dieses Wort bedeutet im **festen hypothetischen**
alten Wörterbuch EACH_ROTA_SINGER, also jeden Kanonsänger. Die neue Konstruktion
fordert dort `salchedy` mit der neu angenommenen Bedeutung LOWER_PES_REFERENCE.
Der unveränderte Parser verwirft die IT-Zeile deshalb. Es gibt keine Zulassung
einer anderen Schreibung, einer neuen Wortbedeutung oder einer Ersatzkonstruktion.

Zusätzlich wurde die bedingte Inhaltsfolge offengelegt: Würde man den geschriebenen
IT-Quantor auf die nachfolgenden Eigenschaften anwenden, erhielte jeder Kanonsänger
„keine Schlusspause“. Seine fest zugeordnete Hauptmelodie endet aber mit einer
Pause. Alle zwölf bedingten Fälle widersprechen dieser Eigenschaft. Das ist keine
vollständige IT-Auslegung; die feste neue Grammatik scheitert bereits zuvor.
[Alle bedingten Fälle](artifacts/CONDITIONAL_IT.json).

Vier diplomatische ZL-Formen bleiben ungebunden: `salche'dy`, `saii@208;`,
`[?:s]cheol`, `so[r:s]`. Die beiden ZL-Absätze haben zusammen95Gruppen;
IT markiert .25–44 als einen92-Gruppen-Absatz mit weiteren Zusammenschlüssen
und unbekannten Formen. Alle betroffenen Zeilen stehen im
[vollständigen Variantenbefund](artifacts/DIPLOMATIC_SCOPE.json).
Es gibt keine diplomatisch vollständige oder mehrfach unabhängig bestätigte Lesung.

## Evidenzgrenze und Entscheidung

Die ursprünglichen vollständigen zwölf Aufführungsspuren wurden unverändert
als gebundene Daten benutzt. Ein unabhängiger Codepfad hat sie erneut vollständig
arithmetisch erzeugt und die alten Verpflichtungen geprüft. Vorwärts-/Rückwärts-
Erkennung, feste Rollen, einmalige erste Ereignisse und neue Relationen stimmen
überein. Die Anzahl verglichener Intervalle steht in
[INDEPENDENT.json](artifacts/INDEPENDENT.json); sie ist Softwareumfang, keine Zahl
neuer Manuskriptbeobachtungen. Beide Prüfer haben denselben Autor.

Die Registrierung `318a70ed4` war öffentlich vor der Ausführung am2026-09-21
um05:01:49UTC. Kein gesperrter wissenschaftlicher Inhalt wurde danach verändert.
Die 30 erfundenen Modellfälle, zwölf Pausengegenfälle, sechs ausgelassenen Terminals
und Cursorerschöpfung wurden vorher geprüft. Ein erster synthetischer Aufruf
benutzte für den alten Prüfer ungeeignete U/L-Namen; das erfundene Beispiel wurde
vor Registrierung an dessen unveränderte Schnittstelle angepasst. Kein Zielergebnis
und kein wissenschaftlicher Vertrag wurde damit repariert.

Alle71 gemeinsamen Wortwerte bleiben unbestätigt, einschließlich der53 alten.
Nur sechs davon erhielten einen zweiten hypothetisch gebundenen Kontext; das
sind nicht53übertragene Bedeutungen. Beide Absätze und die Quelle waren bereits
exponiert und liegen auf demselben physischen Blatt. **Unabhängige
Bedeutungsbestätigungskapazität0, bestätigte Wörter0.** Keine geeignete
Gegenkontrolle der gesamten Suche, keine Signifikanzbehauptung. Quellidentität,
Musikbezug und die vier extern eingesetzten Noten-/Signalreferenten bleiben Annahmen.

Die spezifische gemeinsame Lesung erhalten; keine alten Wörter umdeuten und keine
passende Rhythmusquelle auswählen. Der nächste gehaltvolle Ausbau sollte einen
vollständigen anderen Kontext mit mehr wiederverwendetem Wortschatz versuchen.
Eine weitere freie Umschreibung desselben Beginns wäre schwache Zusatzinformation.
GDT970, GDT947, GDT940 und alternative Wörterbücher bleiben unverändert.
Keine neuen Seiten, Bilder, Kontakte oder Reserven; f84/f84r und f116v geschlossen.
