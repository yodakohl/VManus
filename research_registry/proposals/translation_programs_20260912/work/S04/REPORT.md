# S04 — Wiederholung mit Abbruchbedingung

**Die zwei benachbarten qoteedy-Stellen auf f83r.7:9–10 können unter den festen Hypothesen null oder zwei zusätzliche Einfüllungen verlangen.** Wird der schon behauptete Zielzustand vorher geprüft, ist kein Durchgang nötig. Wird erst nach einem Durchgang geprüft, erfolgt an jeder Stelle eine zusätzliche Einfüllung. Beide Fassungen hinterlassen denselben angenommenen Füllzustand. Die später gelesenen Zustandsinformationen entscheiden sie nicht.

Alle341Gruppen/51Zeilen/sieben Records stehen in drei vollständigen Fassungen. Acht Ganzwortannahmen betreffen72Positionen,269bleiben offen. Die ursprüngliche P15-„erneut“-Lesung bleibt unverändert; sie ist durch diesen Versuch weder repariert noch bestätigt.

## Ganze Lesungen und feste Bedeutungskosten

Gemeinsam aus dem P15-R-Kern: shedy=Flüssigkeit A, lchedy=Zusatzstoff C, qokaiin=Gefäß B, chedy=erwärme, qokeedy=fülle ein, qokeey=laufendes Einfüllen, qokedy=ist eingefüllt. Letztes Material und letztes Gefäß im Record bestimmen das Paar. Gleiche Form bedeutet dabei nur unter der gesetzten lokalen Identitätsannahme denselben Teilnehmer. Die neuen qoteedy-Fassungen lauten:

- [N](READING_N.md): genau ein Einfülldurchgang, ohne die P15-Voraussetzung eines schon früher abgeschlossenen Durchgangs. Das ist eine ausdrücklich andere Einmal-Hypothese, nicht das gerettete Wort „erneut“.
- [PRE](READING_PRE.md): Prüfe zuerst den Zielzustand; führe den festen Einfüllkörper nur bei nicht erfüllter Bedingung aus.
- [POST](READING_POST.md): Führe einen Einfüllkörper aus; prüfe anschließend den Zielzustand.

PRE/POST benötigen zusätzlich eine vorherige geschriebene qokedy-Stelle für genau dasselbe Material-/Gefäßpaar. Eine Aussage über C ersetzt keine Bedingung für A. Fehlende Bedingung ist nicht gleich unerfüllt. Eine ungebundene Stelle erzeugt keinen versteckten Durchgang.

Der Einfüllkörper qokeedy setzt in diesem stark vereinfachten Modell den Zielzustand sofort. Damit gäbe es höchstens einen Durchgang pro gültigem Aufruf, nicht eine erkannte beliebig lange Arbeitsschleife. „Bis“ und die Übernahme dieses Körpers sind angesetzte Ganzwortsemantik, keine gelesenen Teilzeichen oder unabhängige Definitionssyntax. Ein laufender Vorgang qokeey ist kein Abschluss und negiert auch keinen früher erreichten Füllzustand. Erwärmen ändert den Füllstatus nicht.

## Sämtliche fünf qoteedy-Stellen

| Stelle | Material/Gefäß | Passende geschriebene Bedingung | N | PRE | POST |
|---|---|---|---|---|---|
| .2:7 | A/B | keine | 1 Durchgang | Bedingung fehlt | Bedingung fehlt |
| .5:9 | A/B | keine; früheres qokedy .4:3 betrifft C/B | 1 Durchgang | Bedingung fehlt | Bedingung fehlt |
| .7:9 | C/B | qokedy .7:8, bereits eingefüllt | 1 Durchgang | 0 Durchgänge | 1 Durchgang |
| .7:10 | C/B | dasselbe qokedy .7:8 | 1 Durchgang | 0 Durchgänge | 1 Durchgang |
| .20:2 | C, Gefäß fehlt | nicht bindbar | Teilnehmer fehlen | Teilnehmer fehlen | Teilnehmer fehlen |

[Alle Aufrufe und direkten Vergleichsspalten](ALL_CALL_COMPARISONS.tsv). PREs null bei fehlender Bedingung bedeutet „nicht ausgeführt, weil unauflösbar“, nicht erfolgreiches Überspringen. Nur die zwei SKIP_SATISFIED-Stellen sind echte Nullausführungen innerhalb des Modells.

N erzeugt vier zusätzliche Körper, POST zwei, PRE keinen. Daneben haben alle Fassungen dieselben zwei vollständig gebundenen geschriebenen qokeedy-Einfüllungen. Die anderen vier qokeedy-Stellen bleiben wegen fehlender Teilnehmer ungebunden. Unterschiedliche Anforderungen an Bedingungen machen die Ausführungszahlen ungeeignet für einen direkten Qualitätsvergleich.

## Konkreter Ablauf und nachfolgende Aussage

Auf .7:8 wird hypothetisch behauptet: „C ist in B eingefüllt.“ PRE liest danach zweimal eine Kontrolle mit erfülltem Ziel und führt nichts aus. POST liest zwei weitere Einfüllungen von C in B. Beide geschriebenen qoteedy-Vorkommen bleiben im Text und in der Ausführungstabelle; es wird kein Schriftwort entfernt, wenn sein bedingter Körper nullmal ausgeführt wird.

Die nachfolgende Erwärmung chedy .8:5 betrifft unter derselben Teilnehmerregel C. In PRE ist dessen Füllstatus durch qokedy .7:8 behauptet, in POST durch den letzten zusätzlichen Körper .7:10 hergestellt. **Die Herkunft der Zustandsannahme ist verschieden, ihr Inhalt ist gleich.** Eine gelesene Materialmenge, Füllhöhe, Zeit oder sonstige Wirkung, die diese zusätzlichen Handlungen unterscheiden würde, ist nicht vorhanden. Überfüllung wird nicht ohne Mengen- oder Kapazitätsangabe erfunden.

[Alle27Zustandsvergleiche](ALL_STATE_COMPARISONS.tsv) umfassen die13qokedy-Behauptungen und14Erwärmungsstellen. Sie besitzen keine unterschiedliche PRE-/POST-Zustandsangabe. Viele haben kein vollständiges Material-/Gefäßpaar; gleiche Ungebundenheit ist kein bestätigter Zustand. Insbesondere folgt im selben Record auf die beiden gültigen Aufrufe keine weitere gebundene qokedy-Behauptung. Der spätere Erwärmungsbezug ist keine unabhängige Messung des Füllzustands.

## Welche Wiederholungsfrage ungeprüft bleibt

Beide gültigen Bedingungen stammen aus derselben unmittelbar vorausgehenden Schriftstelle und sind bereits wahr. Es gibt **null geschriebene falsche Startbedingungen** und damit keine Kapazität für mehrere erfolglose Durchgänge, eine Terminierungsprüfung oder eine empirisch bestimmte Iterationszahl. Dass der angesetzte Körper sein Ziel in einem Schritt erreicht, folgt aus der Modelldefinition.

Damit ist die Behauptung „qoteedy bezeichnet eine Schleife“ nicht bestätigt. Der konkrete neue Befund des Lesungsvergleichs ist die Unterscheidung von geschriebenen Kontrollstellen und ausgeführten Handlungen: zwei gleiche Formen müssen in einer bedingten Lesung nicht zwei zusätzliche Stoffoperationen bedeuten. Ob eine solche bedingte Lesung hier richtig ist, bleibt offen. Aus der Doppelung allein wird kein Zahlwort und keine Wiederholungsbedeutung gewonnen.

## Entscheidung

PRE/POST als explizite, anhand der gelesenen Füllzustände ununterscheidbare Ablaufhypothesen aufbewahren; keine auswählen. Die beiden fehlenden Bedingungen und das fehlende Gefäß bleiben bestehen. N bleibt eine andere Einmal-Lesung ohne Wiederholungsvoraussetzung. Kein Ersatzmarker, anderer Körper oder neuer Bereich wird nachträglich gesucht, um eine echte Mehrfachschleife zu erzeugen.

P15s strikter „erneut“-Befund, P16s statische Bedingungen und P26s feste Zweischrittkarte bleiben unverändert. GDT574s ältere Zählstimmen und GDT557s formale Fortsetzungsrollen sind keine Bedeutungsbelege für diese Wörter. Das gesamte Arbeitsmaterial und die motivierende Doppelung waren exponiert. Keine nahezu vollständige Lesung bei269offenen Gruppen; keine Reservetests, neuen Seiten/Bilder oder Kontakte. f84/f84r geschlossen. Bestätigte Wortbedeutungen0, unabhängige Bestätigungskapazität0, keine Signifikanz oder scorefähige Relationsevidenz.

[DECISION.md](DECISION.md) lag vor dem Lauf vor; IDEA000177 wurde registriert. Reproduktion aus Repositorywurzel: `python3 research_registry/proposals/translation_programs_20260912/work/S04/build.py`, danach entsprechend `validate.py`. Die unabhängige Präfixrekonstruktion prüft alle126Ereigniszeilen,15Aufrufzeilen und27Zustandsvergleiche. PASS bestätigt Datentreue und feste Konsequenzen, keine Übersetzung.
