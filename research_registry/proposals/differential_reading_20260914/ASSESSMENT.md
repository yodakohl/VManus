# IDEA237 — Erfolgsaussicht, Grenzen und notwendige nächste Lieferung

2026-09-14. Kritische Bewertung auf Nutzerwunsch, nach LANGUAGE_CORRECTION.md.
Diese Bewertung präzisiert den Arbeitsauftrag; ursprüngliche Fassungen bleiben
unverändert. Keine neue Manuskriptauswertung, kein Decoder oder Kontrollkorpus.

## Urteil

**Der Ansatz kann prinzipiell zu einer Lesung führen, ist derzeit aber nur eine
prüfbare Hypothesenfamilie. Es gibt noch kein konkret identifiziertes
Differentialverfahren und keinen positiven Bedeutungsbeleg dafür.** Eine
numerische Erfolgschance wäre unbegründet. Ein begrenzter Ausarbeitungsversuch
ist vertretbar; ein großer Decoderbau ist noch nicht gerechtfertigt.

Sein möglicher Nutzen ist konkret: Er könnte erklären, warum die gleiche
geschriebene Gruppe kontextabhängig andere Information und verschiedene Gruppen
dieselbe Information tragen. Die Daten müssten diese zusätzliche Abhängigkeit
aber verlangen oder eine gemeinsame Lesung dadurch substanziell einschränken.
Eine bloße Möglichkeit, jeden Text umzucodieren, bringt uns nicht weiter.

## Was genau unterschieden werden muss

Im einfachsten Modell ist die nächste sichtbare Gruppe x_i durch eine
Informationswahl m_i und die vorherige sichtbare Gruppe bestimmt:

    x_i = T_m_i(x_(i-1))

T ist ein gemeinsames, endliches Regelwerk. m kann unter getrennten Hypothesen
eine lautliche, grammatische oder fachliche Einheit sein; keine dieser Arten
und keine Ausgangssprache ist gegenwärtig festgelegt. Die Gleichung ist eine
Modelldefinition, kein gemessener Manuskriptbefund.

Dass so ein Kanal prinzipiell lesbar sein kann, zeigt das Gegenstück: Für vier
sichtbare Zustände und Informationswerte 0,1,2,3 sei x_i=(x_(i-1)+m_i) modulo 4.
Dann bestimmt jedes sichtbare Nachbarpaar genau m_i=(x_i-x_(i-1)) modulo 4.
Das ist ein lesbarer Beispielcode. Eine entsprechende Zustandsordnung oder
Operationsstruktur ist für Voynich damit weder gefunden noch vorausgesetzt.

**Schreiben können ist nicht dasselbe wie lesen können.** Sei T_A(x)=x und
T_B(x)=0. Bei Ausgangszustand 0 erzeugen sowohl A als auch B den Folgezustand 0.
Eine Folge von n solchen Schritten hat 2^n verschiedene Nachrichten, die alle
mit denselben zwei Regeln perfekt dieselbe sichtbare Nullfolge erzeugen.
Das ist ein mathematisches Gegenbeispiel ohne Manuskriptdaten.

Für ein beobachtetes Paar (x,y) müssen wir deshalb sämtliche im Kandidaten
zulässigen Informationswerte {m : T_m(x)=y} erhalten. Mehrere Werte sind nicht
automatisch tödlich: Eine gemeinsam geltende Grammatik oder sachliche
Verpflichtung kann sie über den ganzen Abschnitt einschränken. Eine frei
gewählte Lieblingslesung löst die Mehrdeutigkeit dagegen nicht. Die einzelne
Funktion T muss nicht selbst auf Zuständen umkehrbar sein; entscheidend ist,
ob die Nachricht bei bekanntem Vorgänger bestimmbar wird.

Auch eindeutige formale Operatoren identifizieren keine Bedeutung. Werden ihre
unbekannten Inhaltsnamen gemeinsam ausgetauscht, kann dieselbe gesamte
Schriftproduktion erhalten bleiben. Eine solche Umbenennungsmehrdeutigkeit
muss ausgewiesen werden, statt jeden Operatornamen als übersetztes Wort zu zählen.

Eine weitere Präzisierung des alten qokedy-Beispiels: Zwei verschiedene
wörtliche Editbeschreibungen beweisen nicht einmal zwei verschiedene Operatoren
im wahren Schreibverfahren. Eine gemeinsame zustandsabhängige Regel kann auf
verschiedenen Eingaben unterschiedliche Edits ausführen. Die beiden Beispiele
bleiben lediglich eine Illustration möglicher kontextabhängiger Lesung.

## Hauptprobleme und ihre Folgen

| Problem | Wie ein scheinbarer Erfolg entstehen könnte | Was eine tragfähige Fassung leisten muss |
|---|---|---|
| Beliebige Differenzdarstellung | Ein eigener Operator ersetzt jeden Übergang durch das gewünschte ganze Zielwort. | Wenige gemeinsam definierte Regeln wirken auf unterschiedliche Zustände; Literalreste, Positionen und Entscheidungen gehören vollständig zur Modellbeschreibung. Keine verschleierte Abschrift als Regelwerk. |
| Mehrdeutige Lesung | Mehrere Informationswerte führen zum gleichen beobachteten Zustand, dennoch wird nur die schönste Folge ausgegeben. | Zulässige Alternativen und ihre unterschiedlichen Aussagen erhalten; zeigen, welche gemeinsame Regel oder geschriebene Folge sie tatsächlich trennt. |
| Unbekannter Vorgänger | Jeweils das ähnlichste frühere Wort wird nachträglich als Basis gewählt. | Für eine Fassung ein fester Vorgängerbezug. Die primäre unmittelbare Nachbarschaft ist eine Hypothese; ihr Scheitern wird nicht durch unsichtbare Sprünge gerettet. |
| Unklare Informationseinheit | Dasselbe Edit gilt bei Bedarf als Laut, Präposition, Vorgang oder gar nicht geschriebener Inhalt. | Art und Granularität der Information innerhalb einer Fassung festlegen. Rivalisierende Fassungen sind erlaubt, beliebige Wechsel pro Stelle nicht. |
| Startwerte und Resets | Freie Absatzschlüssel oder Ausnahmen speichern einen großen Teil der Nachricht. | Anfangsangaben, erste Gruppen und alle Resets mitführen; keine automatische Inhaltslosigkeit der ersten Gruppe. Die übernommene Recordgliederung ist keine bestätigte Satzgliederung. |
| Isolierte Beschriftungen | Ohne Vorgänger wird spontan auf ein anderes Wörterbuch gewechselt. | Für eine spätere globale Theorie eine gemeinsame, begründete Start-/Beschriftungsregel liefern. Der erste f83r-Prosaentwurf hat dadurch noch keine globale Erklärung. Keine neuen Labels für diese Bewertung öffnen. |
| Abschrift-/Transkriptionsfehler | Jeder Widerspruch wird nachträglich zum Lesefehler erklärt. | Mit überlieferten Unsicherheiten und Varianten arbeiten; nur konkrete vorhandene Schriftbelege dürfen eine Korrektur tragen. Alternative Transkriptionen sind keine unabhängigen Texte. |
| Oberflächenregel ohne Nachricht | Kopieren, Wortbildung oder Layout erzeugen ebenfalls wiederkehrende Änderungen. | Ihre Möglichkeiten als Rivalen erhalten. Edit-Häufigkeit, Kompression und korrekte Rekonstruktion begründen allein weder Inhalt noch einen Differentialcode. |
| Geschlossene Bedeutungswelt | Ein konsistenter Ablauf lässt sich gleichzeitig als Stoffbehandlung, Körpervorgang oder ganz anderes Verfahren erzählen. | Mehrere vollständige Aussagen und ihre Bezüge konkret ausrichten; zeigen, welche Bedeutungsalternativen die beobachteten Konsequenzen noch erlauben. |
| Zu wenig verschiedenartige Belege | Ein Operator kommt oft, aber immer auf derselben Basis oder nur in derselben Formel vor. | Wiederverwendung bei unterschiedlichen Ausgangszuständen und über verschiedene Aussagen suchen. Häufigkeit ist keine unabhängige Bestätigung. |

Fehlerfortpflanzung ist modellabhängig: Bei direktem Lesen jedes Paars sichtbarer
Nachbargruppen beeinflusst eine falsch gelesene mittlere Gruppe höchstens die
zwei angrenzenden Übergänge, sofern Gruppierung und Grenzen erhalten bleiben.
Eine ausgelassene Gruppe oder andere Segmentierung betrifft auch die Zahl und
Zuordnung der Übergänge. Ein zusätzlich fortgeschriebener verborgener Zustand
kann längere Fehlerfolgen erzeugen. Keine dieser Varianten wird hier getestet;
die verbreitete pauschale Behauptung endloser Fehlerfortpflanzung wäre für das
einfache sichtbare Paarmodell falsch.

## Was als Erfolg zählt

| Stufe | Konkrete Lieferung | Bedeutung für unser Ziel |
|---|---|---|
| Ausführbarer Kandidat | Begrenztes Regelwerk, offengelegte Starts/Grenzen, vollständige Vorwärtsspur und Analyse mehrdeutiger Informationswerte. | Voraussetzung für eine Prüfung; noch kein Entzifferungsfortschritt allein durch Umcodierung. |
| Inhaltlicher Arbeitsfortschritt | Mehrere vollständige Aussagen mit gemeinsam geltenden Regeln, expliziten Lücken und wiederverwendeten Informationswerten. Konkurrierende Aussagen werden an konkreten Folgen enger. | Rechtfertigt die weitere Ausarbeitung als Hypothese. Ein passendes Wort oder eine beliebig erzählbare Geschichte genügt nicht. |
| Erste begründete Bedeutungslesung | Derselbe Informationswert trägt eine konkrete Bedeutung in mehreren unterschiedlichen Zusammenhängen; ein Austausch der Bedeutung hat benannte, überprüfbare Folgen. | Ein ausdrücklich vorläufiges Verständnis eines Ausdrucks oder einer Konstruktion. Es muss bei Differentialschrift keine kontextfreie Glosse eines einzelnen EVA-Worts sein. |
| Plausible Gesamtlesung im Arbeitsumfang | Nahezu alle Positionen funktionieren unter demselben Modell; Aussagen und Rückbezüge passen zusammen; relevante Gegenlesungen und Restlücken sind dokumentiert. | Grundlage für die vom Nutzer erst dann gewünschte spätere Reserveprüfung. Keine willkürliche Prozentgrenze ersetzt diese Beurteilung. |
| Unabhängige Bestätigung | Das eingefrorene Modell trägt später konkrete neue Folgen auf geeigneten zurückgehaltenen physischen Blättern und eine unabhängige Prüfung der behaupteten Bedeutungen. | Stärkerer Übersetzungsbefund; strukturelle Vorhersage allein bestätigt weiterhin keine Pflanzennamen. f84/f84r bleiben versiegelt. |

Ein erfolgreicher formaler Mechanismus kann also ein Baustein sein, ohne schon
das vom Nutzer verlangte Verständnis zu liefern. Umgekehrt braucht der Beginn
einer kohärenten Hypothese weder ein bestätigtes Wort noch hundertprozentige
Gewissheit. Der entscheidende Arbeitsfortschritt ist **weniger freie
Inhaltsentscheidungen bei mehr zusammenhängend erklärtem Text**.

## Was wir bereits haben und was fehlt

Vorhanden ist die bereits exponierte W92-Projektion von f83r mit sieben
Arbeitsrecords, 51 transkribierten Zeilen und 341 Gruppen. Vorhandene alternative
Transkriptionen und zugelassene Bilder können später konkrete Unsicherheiten
prüfen; diese Bewertung hat sie nicht neu geöffnet. Die reservierten Blätter
werden für die Entwicklung nicht gebraucht.

**Es fehlt vor allem ein konkreter Schreibvertrag und eine dadurch tatsächlich
eingeschränkte Inhaltsfassung.** Weder ein identifiziertes Operationsalphabet
noch eine etablierte Informationseinheit, eine Startregel oder ein Bedeutungswert
liegt schon vor. Wir brauchen nicht zuerst mehr Rechenleistung oder einen neuen
historischen Korpus. Wir brauchen einen kleinen gemeinsam lesbaren Modellfall,
der seine Entscheidungen nicht vollständig aus Wunschbedeutungen bezieht.

Im nächsten Arbeitsblock müssen deshalb gemeinsam entstehen:

1. Eine konkrete endliche Fassung für Vorgängerbezug, Operationen, Anfangsangaben
   und Informationseinheit, zunächst ohne bevorzugte Sprache.
2. Eine vollständige Ausrichtung des vorhandenen Arbeitsumfangs und ein ernsthafter
   zusammenhängender Inhaltsentwurf, einschließlich aller offenen Positionen.
3. Eine Gegenlesung, die dieselbe Oberfläche möglichst gut erklärt, sowie die
   genaue Liste der Entscheidungen, die der Text zwischen beiden trägt oder
   gerade nicht trägt. Kein erschöpfender Ausschluss aller Modelle wird behauptet.

Die bisherigen etwa 90 Minuten sind ein Arbeitscheckpoint, kein begründetes
Versprechen einer nahezu vollständigen Lesung. Danach lohnt Fortsetzung, wenn
gemeinsam angewandte Regeln neue konkrete inhaltliche Einschränkungen liefern.
Wenn nur Edit-Listen, freie Umschreibungen oder immer neue Einzelfallregeln
entstehen, stoppen wir den Ausbau dieser Fassung. Das ist kein Anlass zu einer
automatischen Decoder-, Parameter- oder Kontrollkorpus-Reparaturkette.

## Grundlage und Expositionsgrenze

Root las aktuelle Route, IDEA237, Sprachkorrektur, den einschlägigen Abschnitt
des alten Plans sowie erneut die Primärberichte
[GDT345](../../../experiments/yolo/gdt345_productive_operator_transfer/REPORT.md)
und [RTA001](../../../experiments/semantic_assumptions/results/rta001_result_report.md).
Beide verhindern, generische Transformationsleistung als neue Bedeutungsbrücke
auszugeben. Ihre alten Ergebnisse werden nicht neu bewertet oder wiederholt.
Ein begrenzter Ideenagent kritisierte unabhängig denselben Modellvertrag; keine
blinde Manuskriptbestätigung und keine externe fachkundige Person.

Die mathematischen Gegenbeispiele und Fehlergrenzen oben sind hier abgeleitete
Modellaussagen, keine neuen Voynich-Beobachtungen. Kein neuer externer Quellenabruf,
Bildzugriff oder Rohtextzugriff, keine Tests, Kontakte oder Reservenöffnung.
Keine Signifikanz und keine bestätigte Bedeutung. Dieser Bericht ergänzt die
Erfolgskriterien um **Bestimmbarkeit der Lesung**, die bloße Vorwärtsrekonstruktion
nicht garantiert.
