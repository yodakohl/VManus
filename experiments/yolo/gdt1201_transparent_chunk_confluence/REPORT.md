# GDT1201 — mehrere Zerlegungen dürfen denselben Inhalt haben

**Die kleine Konstruktion erhält ihre vollständigen symbolischen Nachrichten,
obwohl viele Ausgaben auf mehrere Arten gruppiert werden können.** Ein eindeutiger
Zerlegungsbaum ist keine notwendige Voraussetzung eines eindeutig lesbaren Codes.
Das präzisiert die1200-Handregel; es ist kein neuer Manuskriptbefund und keine
statistisch passende Voynich-Rekonstruktion.

## Die Regel aus Sicht des Schreibers

Lerne wenige Grundzeichenfolgen. Größere vertraute Gruppen darfst du zusätzlich
als Ganzes erkennen. Ihr Inhalt bleibt aber genau die Folge ihrer Bestandteile.
Ein größerer Block erhält hier ausdrücklich KEINEN neuen eigenen Inhaltswert.
Das ändert die Art, wie man beim Lesen gruppiert, nicht die geschriebene Länge.
Es handelt sich um gelernte Gruppen, nicht um neue verkürzende Schriftzeichen.

Im künstlichen Beispiel ergeben die folgenden drei Wege dieselbe Quellfolge:

| Sichtbare Gruppierung beim Lesen | Vollständig expandierter Inhalt |
|---|---|
| ol + ol + dy | U3, U3, U5 |
| olol + dy | U3, U3, U5 |
| ol + oldy | U3, U3, U5 |

Auch das ganze ololdy kann als transparenter Block gelernt werden. Der Inhalt
bleibt identisch. Entsprechend funktioniert dal+dal+dy, dal+daldy und
daldal+dy. daldy, daly und dalor bleiben verschiedene Zeichenfolgen und Inhalte
im künstlichen Code. Es wird nicht das ganze daldy zweimal geschrieben und
eine Hälfte gelöscht: daldy+daldy wäre eine andere Quellfolge.

U0..U6 sind uninterpretiert. Keine davon bezeichnet Wasser, Pflanze, Handlung,
Zahl oder ein deutsches/lateinisches Wort. Die sieben ausdrücklich erfundenen
Zuordnungen dal/al/ch/ol/y/dy/or dienen nur dem Handbeispiel und werden NICHT
als primitive Einheiten oder Bedeutungen des Manuskripts übernommen. Kein
Voynichwort wird durch die Wahl dieser Tabelle erklärt oder übersetzt.

## Warum die Konstruktion funktioniert

Die sieben kurzen Codes und die drei bezahlten Strukturcodes sind prefix-frei:
kein primitiver Code ist der Anfang eines anderen. Deshalb lässt sich ihre
Verkettung eindeutig in primitive Quellzeichen zurücklesen. Jeder gelernte
Block wird exakt durch dieselbe Verkettung seiner primitiven Inhalte geschrieben.

Ersetze in einer beliebigen erlaubten größeren Zerlegung jeden Block durch
seine primitive Definition. Die Ausgabe ändert sich dabei nicht. Alle Wege
enden deshalb bei derselben eindeutigen primitiven Folge. Das beweist die
Eigenschaft für beliebig lange endliche Nachrichten, nicht nur die Beispiele.
Zyklen, Löschungen und neue Ganzwortwerte sind nicht Teil dieses Beweises.
Bei einem kontextabhängigen Schreiber müsste ein Block zusätzlich genau die
Ausgabe UND Zustandsänderung seiner Teilregeln erhalten; dies wurde hier nicht
als neuer zustandsabhängiger Vollschreiber implementiert.

Die endliche Softwareprobe zählt alle2801Quellfolgen bis Länge4 über den sieben
Quellzeichen.2112haben mehrere erlaubte Zerlegungen; alle behalten genau eine
expandierte Nachricht. Die Zahl ist ein Konsistenzcheck eines konstruierten
Beispiels, kein empirischer Erfolg an2801Voynichwörtern. Code, Tabelle,
Lehrbeispiele und separat geschriebener Vorwärts-DP-Validator sind gespeichert.
Die Validierung bestätigt die kleine Konstruktion; gleicher Autor, kein Blindtest.

## Die Gegenfälle gehen nicht verloren

1. Erhält olol zusätzlich einen NEUEN unabhängigen Wert, entstehen unter der
   gleichen Schreibung zwei verschiedene Nachrichten. Längster Treffer zuerst
   wählt dann lediglich eine davon; es kann nicht beide Eingänge zurückgewinnen.
2. Zwei Wörter sind nicht automatisch ein einziges Wort. Die künstliche Quelle
   U3/WORD_BREAK/U3 wird anders geschrieben als U3/U3. Entfernt man die Grenze,
   kollidieren sie. Die wechselnden Abstände aus1198/1199 werden dadurch nicht
   als semantisch beliebig erklärt.
3. OPEN/U0/CLOSE/U1 und U0/OPEN/U1/CLOSE behalten unterschiedliche Klammerung.
   Wenn die Klammern entfernt werden, fällt beides zu U0/U1 zusammen.
4. U0/U0 bleibt von U0 verschieden. Keine Wiederholung wird als Schmuck gelöscht.

Das Beispiel bezahlt solche Struktur mit m,p,f als künstlichen Zusatzcodes.
Diese Werte sind KEINE vorgeschlagenen Voynichwerte. Ihr Platz, Zeichenaufwand
und Häufigkeit wären bei einem Vollschreiber mitzuzählen. Die zehn Struktur-
beispiele prüfen Grenzen, Reihenfolge und Klammerung, keine historische Grammatik.

## Was daraus folgt — und was noch fehlt

1200s Doppelungsreihen und genaue Häufigkeiten bleiben unverändert. Die dort
beschriebene Informationskollision gilt bedingt, wenn ol und olol unabhängig
belegte verschiedene Inhalte tragen sollen. Solche unterschiedlichen Werte
haben wir nicht. Ein selbständig geschriebenes olol beweist sie ebenfalls nicht.
Wir brauchen deshalb vor der nächsten Konstruktion nicht erst zwingend eine
native Entscheidung zwischen allen denkbaren Zerlegungsbäumen.

Die bevorzugte ENTWURFSBEDINGUNG lautet jetzt: bekannte Teile und gelernte
Gruppen dürfen nebeneinander bestehen, sofern ihre erklärten Inhalte und
Strukturen zusammenpassen. Eigenständige Ganzwerte bleiben möglich, benötigen
aber ihre eigene unterscheidende Schreib-/Kontextregel. Das beweist weder eine
natürliche Sprache noch die hier frei gewählten primitiven Grenzen.

Das Beispiel enthält10primitive Codes und20optionale gelernte Gruppen. Es
sendet symbolische Nachrichten; es ist noch kein vollständiger inhaltlicher
Schreiber für die vorhandenen historischen Quelltexte. Es erzeugt keine
passende Wortverteilung allein dadurch, dass es rücklesbar ist.1174s zehn
statistisch gescheiterte Schreiber zeigen diese Unterscheidung schon;1175s
Wörterbuchkosten und1193s2130Einträge/zusätzliche Formfehler bleiben offen.
Keine neue Bedeutung oder globale Statistikpassung wird behauptet.

Eine nächste schlichte Kandidatenklasse wäre Wortkörper mit stabilen Teilwerten
und höchstens zwei Anfangsvarianten. Vor Zeichentabellen wäre ihre günstigste
notwendige Wortvielfalt/Konzentration aus GANZEN Quellwörtern zu begrenzen.
Das ist noch kein ausgewählter oder ausgeführter Test:1180s V2-Quellkontext,
1196s Fragment-/Aliasgrenzen und1197s ungetestete Buchstabengedächtnisse müssen
bei Auswahl auseinandergehalten werden. Kein unveränderter alter Fehler wird
als neue Idee oder automatischer Folgeversuch wiederholt.

## Protokoll

Vertrag lokal12:43:07UTC vor Implementierung und Ausführung gebunden, nach
Vorbereitung seit12:30:27UTC. Erwarteter mathematischer Konstruktionsbefund;
keine empirische Hypothesenbestätigung. Keine neue Quelle, native Wortabfrage,
Bildprüfung, Reserve, f84/f84r/f116v oder Relationserfassung.616s ursprüngliches
UNSAT bleibt erhalten; seine späteren Diagnosen werden nicht übernommen.
995s konditionale Rückgewinnung macht aus diesem Beispiel keinen nativen Decoder.
1201ändert weder1200s Daten noch dessen eingefrorene Entscheidung.

Reproduzierbarer lokaler Konstruktionscheckpoint nach Live-Route. Keine
Veröffentlichung, keine menschliche Benutzbarkeitsmessung, keine laufende
Hintergrundforschung. Der tatsächliche Zeitabschluss steht im vorhandenen Dossier.
