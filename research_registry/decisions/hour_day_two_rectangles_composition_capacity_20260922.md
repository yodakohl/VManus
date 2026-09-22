# Zwei Formrechtecke im eingefrorenen Stundenmodell

17:09UTC, begrenzte Prüfung ohne Zielöffnung, neue Glossen oder Ausführung.
Gelesen: CurrentRoute, Auswahlentscheidung519, GDT1015 MODEL/ganze C01/C03/C05/
C07/C10, GDT915/916, GDT998 und GDT1016. Die Bedeutungen werden dem519-Autor
nicht als Vorschläge zugeschickt. Seine unabhängige ganze Entwicklung bleibt
unverändert.

**Ergebnis: Der versuchte gemeinsame Operator liefert noch keine eingeschränkte
Bedeutung für beide fehlenden Ecken.** Das ist kein Unmöglichkeitsbeweis für
jede d/e-Komposition. Ein konkreter neuer Rahmenvertrag könnte die Lücke schließen,
würde aber zusätzliche semantische Arbeit leisten und darf nicht als aus den
alten Wortwerten erzwungene Analogie erscheinen.

## Das vollständige einschlägige alte Inventar

Die Zeilen sind wörtliche ASCII-Musterbeschreibungen, keine bewiesenen Morpheme.

| Stamm-Muster | ein e, ohne d | ein e, mit d | zwei e, ohne d | zwei e, mit d | drei e, ohne d |
|---|---|---|---|---|---|
| qok…y | qokey: im alten60-Lexikon offen | qokedy: DAY | qokeey: FIRST | qokeedy: HOUR | qokeeey: WHOLE |
| qot…y | qotey: im alten60-Lexikon offen | qotedy: ADVANCE | qoteey: COUNT_THROUGH | qoteedy: im alten60-Lexikon offen | keine alte Form |

Die anderen alten qok/qot-Anfänge sind qotedor=COMPLETE, qotal=INCLUDES,
qokal=DERIVED, qokain=INITIAL_POINT und qokaiin=RULER. Sie erfüllen nicht das
oben deklarierte exakte e^n d?-y-Muster. Sie bleiben unveränderte Wörter; aus
dem beschränkten Rechteck folgt ausdrücklich keine globale q-,k-,t-,y- oder
d-Bedeutung. Das Muster nachträglich über neue Zielwörter auszudehnen wäre ein
anderes Angebot.

Besonders `qokeeey=WHOLE` darf nicht vergessen werden. Ein bloß monotones
„zusätzliches e macht eine kleinere Einheit“ kann DAY→HOUR plausibel erzählen,
hat aber für FIRST→WHOLE gerade die entgegengesetzte Größenrichtung.
Gleichermaßen bedeutet DAY im alten C01 ein vollständiges Wiederkehrintervall,
nicht eine bereits gleich lange physische24-Stunden-Masse. Gleich lange Stunden
darf eine neue Rechenregel nicht still ergänzen.

## Ein tatsächlich versuchtes gemeinsames Modell

Der günstigste sparsame Versuch hatte zwei Operationen:

1. Ein zusätzliches e wechselt einen ausdrücklich binären Umfangsparameter
   ONE↔WHOLE. Bei einem Selektor wäre FIRST der ONE-Fall, WHOLE der Gesamtfall;
   bei einer Fortschreitoperation wäre ADVANCE ein Schritt und COUNT_THROUGH
   die Iteration über den gegebenen Umfang. Das ist eine neue Involutionsannahme,
   keine aus Wortlängen bewiesene Grammatik. Ein globaler Toggle statt einer
   monotone Verfeinerung könnte den dritten e-Schritt grundsätzlich behalten.
2. d sättigt den resultierenden Ausdruck mit einem bereits verfügbaren geordneten
   Rahmen. Es sollte aus WHOLE einen DAY und aus FIRST einen HOUR liefern, ohne
   pro Wurzel eine Ergebnistabelle zu verwenden. Dieselbe Sättigung müsste auch
   im qot-Zweig definiert sein.

Der erste Teil allein liefert noch kein volles Wort. Insbesondere darf FIRST
nicht kostenlos zu einem Ausdruck mit dem zusätzlichen Merkmal „Stunde“ werden.
Im alten vollständigen C05 steht:

`SELECT FIRST RULER START`

Die Grammatik wählt den ersten **RULER**; START wird zusätzlich als erste HOUR
des DAY gebunden. Wer d als Anwendung von FIRST auf den tatsächlich folgenden
Objekttyp definiert, erhält einen RULER, nicht HOUR. Um HOUR zu gewinnen, muss
er einen anderen impliziten Stundenrahmen wählen oder vom Herrscher zu seiner
Stunde über eine Besitzrelation wechseln. Beide wären neue Operationen/Argument-
bindungen. Eine ausgeführte Auswahl liefert ferner eine erste Stundeninstanz;
das alte HOUR ist an C03/C07/C10 ein wiederverwendbarer Stundenbegriff mit
unterschiedlichen Referenzrollen. Instanz, Einheit und Selektor dürfen dabei
nicht still gleichgesetzt werden.

Im qot-Zweig fehlt zusätzlich jeder alte nackte qotey-Wert. Daher ist nicht
einmal durch ein bekanntes vollständiges Paar gebunden, wie d auf einer
Fortschreitoperation wirkt. Ein d, das einen COUNT_THROUGH-Ausdruck an einen
Rahmen bindet, könnte eine ausführbare Rechnung, deren Ergebnis oder deren
gezählten Zeitraum liefern. Das sind verschiedene Typen und Inhaltsfolgen.
Keine davon folgt aus den zwei bekannten qot-Werten. Eine Tabelle
„bei Selektoren gib Zeitraum, bei dieser Operation gib dasselbe Verb“ wäre
eine neue geteilte Typregel mit unbewiesenem d-Inhalt, keine bereits vollständige
einheitliche Herleitung. Den letzten Fall lediglich als unbekannte Funktion zu
benennen verschiebt die freie Variable.

Auch der günstigere Versuch, **nur** den e-Wechsel als ONE/WHOLE-Umschaltung
zu benutzen und d unanalysiert zu lassen, wurde erwogen. Er würde die Darstellung
DAY=ganze Stundenfolge, HOUR=eine Stunde, FIRST=erstes Element,
WHOLE=Gesamtumfang, ADVANCE=ein Schritt und COUNT_THROUGH=Iteration über den
Gesamtumfang verlangen. Dann könnte man fehlende Ecken durch dieselbe
Umschaltung ergänzen. Das ist eine interessante gemeinsame Darstellung, aber
noch nicht dieselbe volle Denotation: HOUR bedeutet im alten Vertrag nicht
FIRST_HOUR; C03 betrifft gerade die folgenden Stunden und C10 sogar die Stunde
nach dem vollständigen Tag. FIRST bestimmt dagegen die erste Position. Man
braucht daher eine ausdrücklich typisierte Abstraktion von Stundeninstanzen zu
Einheitenarten sowie eine Herleitung, wann ONE „ein beliebiges gezähltes Glied“
und wann „das erste Glied“ bedeutet. Außerdem erhält COUNT_THROUGH seinen Umfang
erst aus den geschriebenen DAY/UNTIL-Argumenten, während ADVANCE ein einzelner
durch Stundenbeginn ausgelöster Schritt ist. Deren Fold-/Ausführungsbrücke ist
zusätzlich zum binären Umfangsparameter zu definieren. Ohne diese Brücken wäre
„ONE/WHOLE“ ein gemeinsames Etikett für drei nachträglich nebeneinandergestellte
Umbenennungen. Es wird deshalb nicht als fertiger Operator oder als erzwungene
Wortergänzung an die unabhängige Entwicklung weitergegeben.

## Konkrete Grenze und kleinster ehrlicher Zusatz

Es müsste **vor** jeder neuen Zieldeutung genau ein Argumentvertrag festliegen:
welcher alte geschriebene Rahmen d zur Verfügung steht; ob d Instanz, Einheit,
Relation oder Operation zurückgibt; und wie derselbe Vertrag auf einen
Ordinalselektor und auf eine Fortschreitoperation wirkt. Er muss C05s RULER-
Argument und C03/C07/C10s Stundenrollen gemeinsam erhalten. Ein pro Form oder
pro gewünschtem Ergebnis gewählter Rahmen ist unzulässig.

Erst ein solcher Vertrag könnte eine neue ganze Lesung wirklich einschränken:
ein nachfolgender geschriebener Argumentplatz dürfte dann beispielsweise keine
Operation verlangen, falls der vorab abgeleitete Wert zwingend ein Zeitraum
wäre. Gegenwärtig ist gerade dieser Rückgabetyp im qot-Zweig offen. Deshalb
werden weder qokey noch qoteedy mit einer neuen Bedeutung versehen und kein
Simulator, Suchlauf oder Experiment vorgeschlagen. Auch die ONE/WHOLE-Involution
wird nicht als ausgewählte Hypothese eingetragen.

GDT915 bewahrt die bekannte positive r/l-Phrasenassoziation; GDT916 etabliert
ihren Transfer auf neue Stammkombinationen gerade nicht. Beide entscheiden keine
d/e-Semantik. GDT998 widerspricht einem konkreten vollständigen additiven
Merkmalswriter, nicht allen Formrechtecken. GDT1016 zeigt den entscheidenden
Einwand gegen einen unsichtbar eingeschmuggelten Teilnehmer: Eine einstellige
Operation gewinnt keinen bestimmten Kontextteilnehmer allein aus einem
teilnehmerneutralen Eingang. Hier könnte ein ausdrücklich gelieferter Rahmen
helfen, ist aber nicht kostenlos. GDT608s gerichteter Formaufbau und notwendige
Gesamtformreste bleiben die Strukturgrundlage, kein Ersatz dieses Arguments.

Die Beurteilung betrifft das unabhängige Kompositionsangebot. Sie entscheidet
nicht über den separat entstehenden ganzen519-Entwurf, verändert keine alten
Bytes und übernimmt keine neuen Zielwortlesungen.
