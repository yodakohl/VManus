# GDT961 — sämtliche direkten Zeichenbausteine geprüft, kein Pflanzenlexikon

Der vollständige Bausteinvergleich liefert **keine einzige der88 Kombinationen,
in der sämtliche Pflanzen bereits einen passenden lesbaren Marker besitzen**.
58 Fälle widersprechen sogar der großzügigen Ergänzung unbekannter Gruppen;
30 ZL3b-Fälle bleiben nur als unvollständige Möglichkeit bestehen. Alle48 IT2a-
Fälle widersprechen. RF1b hat weiterhin keine eigenen Absatzgrenzen.

Ein lokaler Treffer ist vollständig dokumentiert: `tc` und `tch` passen im
registrierten Ausschnitt lesbarer Wörter zu sieben geforderten Mugwort-Absätzen
auf f113r. Eine zusätzliche alphabetische Rohgruppe in Absatz14 enthält beide
Zeichenfolgen jedoch ebenfalls. Deshalb wird auch dieser Teiltreffer **nicht als
Pflanzenname übernommen**. Die Zahlen des registrierten Tests bleiben unverändert;
der Rohdatengegenbefund wird davon getrennt ausgewiesen.

## Was vollständig geprüft wurde

Die öffentliche Registrierung **6ee992cc4** enthält alle2904 konkreten
[Quellenvorhersagen](artifacts/PREDICTIONS.tsv) vor der Bausteinauszählung. Die22
vollständigen15-Absatz-Folgen, beide Richtungen und beide32/34-Pflanzenmodelle
stammen unverändert aus GDT960. Alle Daten waren schon exponiert.

Für jedes dort bekannte Wort wurden sämtliche nichtleeren zusammenhängenden
Zeichenfolgen erfasst: ein Zeichen, interne Stücke, Anfänge, Enden und vollständige
Wörter. Kein Decoder, kein gewählter Wortstamm und keine neue Präfixregel.
Es entstanden31251 Baustein/Fenster-Paare mit6608 verschiedenen Zeichenfolgen.
Ihre6008 unterschiedlichen Absatzmasken sind samt allen gleich vorhersagenden
Stücken in [IDENTICAL_COMPONENT_PREDICTIONS](artifacts/IDENTICAL_COMPONENT_PREDICTIONS.json.gz)
festgehalten. Die [vollständige Maskentabelle](artifacts/COMPONENT_MASKS.tsv.gz)
enthält auch alle ausgeschlossenen Stücke; die
[2904 vollständigen Pflanzen-Domänen](artifacts/PLANT_COMPONENT_DOMAINS.json.gz)
und [88 Kandidatenfälle](artifacts/CANDIDATE_TABLE.tsv) erlauben die Nachprüfung.

|Edition|Fälle|alle lesbaren Namensdomänen vorhanden|auch obere Möglichkeit widersprochen|nur obere Möglichkeit|
|---|---:|---:|---:|---:|
|ZL3b|40|0|10|30|
|IT2a|48|0|48|0|

Dies ist ein notwendiger Verteilungstest: Auch nichtleere Einzeldomänen würden
kein gemeinsam lesbares Lexikon beweisen. Unterschiedliche Pflanzen können
überlappende Stücke desselben Wortes beanspruchen. Solche gemeinsamen
semantischen Zuordnungen wurden nicht als gelöste Gesamtlesung ausgegeben.
2672 einzelne Pflanzen-Domänen haben eine beobachtete passende Maske,89 nur eine
Ergänzungsmöglichkeit,143 gar keine. Viele Quellenpflanzen stehen nur in einer
Zeile; passende seltene Stücke identifizieren sie deshalb nicht.

## Der konkrete Teiltreffer und seine Gegenstelle

In ZL3b, f113r.1–44, ursprüngliche Quellenreihenfolge, besitzen `tc` und `tch`
dieselbe Maske1/4/5/7/8/10/15. Beide Quellenmodelle zählen diesen einen physischen
Befund; es sind keine zwei Bestätigungen. Bekannte Träger sind:

|Relativer Absatz|Vollständige Trägerwörter|
|---|---|
|1|otchechy|
|4|otchedy|
|5|kotchy|
|7|otchdy|
|8|otchod; tchoar|
|10|chtchol; tcheody; tchey; tchol|
|15|otchedy; tcheor|

Die Stücke sind mit dieser Verteilung nicht unterscheidbar. Für Perwinkle passt
im Pflanzenidentitätsmodell zusätzlich `tcho` zu8/10; für Trifoile passen
`oteed`, `oteedy`, `sar`, `teed`, `teedy` zu10/12. Das Gesamtmodell besitzt aber
schon hier **keinen bekannten Marker für Mandrake und Succory**, in beiden
Quellenmodellen. Keine dieser Teilzuordnungen wird als Übersetzung angenommen.

Der nach dem Ergebnis ergänzte [vollständige Rohgruppenaudit](artifacts/OBSERVED_MATCH_RAW_AUDIT.tsv)
prüft alle alphabetischen Träger aller gefundenen Mugwort-Stücke in dieser Folge.
Er zeigt die entscheidende zusätzliche Stelle:

|Edition|Stelle|Rohgruppe|Linke Grenze|Relativer Absatz|Quellenanforderung|
|---|---|---|---|---:|---|
|ZL3b|f113r.40, G011|tchey|UNCERTAIN_SMALL_SPACE|14|keine Mugwort-Nennung|
|IT2a|f113r.40, G010|qotchey|DEFINITE_SPACE|14|keine Mugwort-Nennung|

Im registrierten konservativen Vergleich galt die ZL-Gruppe wegen ihrer
Wortgrenze vollständig als unbekannt. Für eine Zeichenfolge **innerhalb** von
`tchey` löscht die unsichere linke Wortgrenze die sichtbaren Buchstaben jedoch
nicht. Das erklärt den scheinbaren7/7-Treffer, ohne die Zählregel nachträglich
zu verändern. IT2a hat dieselben15 Absatzgrenzen, enthält die zusätzliche Stelle
bereits in der bekannten Maske und widerspricht dem Marker direkt. Diese
Fassungen sind Lesungsrivalen desselben Blattes, keine unabhängigen Folien.

## Entscheidung und tatsächliche Reichweite

Kein Pflanzenmarker wird übernommen. Die direkte Behauptung `tc` oder `tch`
trage kontextunabhängig die Mugwort-Nennung ist durch die alphabetische
Gegenstelle unbrauchbar. Die58 registrierten Widersprüche schließen innerhalb
ihrer jeweiligen Folge sämtliche geprüften direkten Zeichenmarker aus. Die30
oberen Fälle liefern weiterhin keine beobachtete vollständige Lesung.

Der Ausdruck „Baustein“ meint hier ausschließlich einen Marker, der bei jedem
rohen Enthaltensein einer Zeichenfolge gilt. Eine Grammatik, die gleiche
Buchstaben je nach Segmentierung oder Kontext verschieden auswertet, wurde
nicht geprüft. Der Versuch erschöpft daher weder alle Morphemhypothesen noch
GDT608s konkreten BPE-Parser. Dessen fehlende Bedeutungsbestätigung wäre auch
kein Verbot, ihn künftig als ausdrücklich spekulative Darstellung zu prüfen.
GDT960 sowie alle früheren Regeln, Quellen und Nicht-Eindeutigkeitsbefunde
bleiben unverändert. Keine weitere ausgewählte Stückverlängerung zur Rettung
dieses lokalen Pflanzenmodells.

Der [separat implementierte Validator](artifacts/VALIDATION.json) meldet PASS
für Masken, Quellenvorhersagen, sämtliche Domänen, Falltabellen und Rohdiagnostik.
Das ist keine Bedeutungsprüfung. Fünf exponierte physische Blätter, null
unabhängige Bestätigungsblätter je Kandidat. Keine neue Seite, kein Bild, kein
Decoder; Reserven, f84/f84r und f116v blieben geschlossen. Keine Gegenkontrolle
der gesamten Suche, keine Signifikanzbehauptung. Bestätigte Voynichwörter:0.
