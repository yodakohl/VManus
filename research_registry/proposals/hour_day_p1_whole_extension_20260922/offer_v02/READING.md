# V2: bedingter, typisierter Gesamtentwurf für f82r.1–9

Dieser V2-Entwurf ist ein Konstruktionvertrag, keine ausgeführte semantische
Prüfung. Die 60 alten Werte und die 12 exakten Konstruktionen des alten
80-Positionen-Kontos bleiben unverändert. Für die beiden neuen Leserzweige
werden dieselben 42 neuen ganzen Werte aus V1 verwendet. `CONSTRUCTIONS.json`
definiert vier neue, geordnete P1-Produktionen; `DERIVATIONS.json` weist jeder
der 144 geschriebenen Gruppen genau einen Terminalplatz und jeden Terminalplatz
einem Ausdruck zu. Es gibt keine Alias-, Packungs- oder
Vorkommenssinn-Regel.

Die alten Muster werden dabei nicht als freie Schablonen erweitert. Das alte
P2-Konto ist in `INHERITED_CONTRACT.json` mit allen zwölf Musterfolgen
aufgeführt; kein altes Muster wird für P1 wiederverwendet. Alte Werte sind nur
unveränderte Terminals in den vier neuen P1-Mustern. Die fünf IT-Formen
`qocseedy`, `sor`, `lchor`, `sshol` und `shecthy` bleiben unaufgelöste Zweige.

## Vertragliche Konstruktionen

`P1_FRAME_COUNT` baut aus der Folge `qosheedy/qocseedy – qokeol – daiin#1 –
shckhy – okeeor – cheey – daiin#2 – shey` einen `TemporalFrame`. Die beiden
`daiin` sind ausdrücklich verschieden benannte Argumente: `daiin#1` ist
`FRAME_UNITS=24`, `daiin#2` ist `RETURN_UNITS=24`. Beide stehen sichtbar im
Ausdruck. Die Basis des `cheey`-Nachfolgers ist in C01 noch nicht geschrieben;
sie bleibt als `U01` offen und wird nicht durch ein zukünftiges P2-Objekt ersetzt.

`P1_PHASE_DERIVATION` hat drei festgelegte Argumentfolgen. In C02 lautet sie
`dchedy, qolchedy, qokain, dy, qokeedy, qokal, lcheckhy, lched`. `dy` ist hier
ein typisierter rückwärtsweisender `THIS<Point>` und bezieht sich unmittelbar
auf das zuvor geschriebene `qokain INITIAL_POINT`; dadurch wird kein späteres
HOUR- oder DAY-Vorkommen als Antezedens entliehen. `qokal` wird aus
`qokeedy + dchedy + qokain` abgeleitet. In C05 ist die Reihenfolge
`sol, lkchedy, qokeedy, qokal, cthol, chedy, qoteedy, qokal`; die beiden
`qokal` erhalten die Quellen `qokeedy + lkchedy` beziehungsweise
`qoteedy + chedy`. In C09 ist die Reihenfolge des Schlussausdrucks
`ssholshecthy` (ZL) beziehungsweise `sshol, shecthy` (IT), dann
`qokaiin#1, chkedy, rchey, dairchey, qokaiin#2`. Die beiden RULER-Terminals
bleiben als `R_C09a` und `R_C09b` getrennte Identitäten.

`P1_RULER_SUCCESSION` verwendet drei exakte Folgen. C03 bindet `qokeey FIRST`
an die Domäne `solkaiin RULER_CYCLE` und führt zu `R_C03`; C04 nimmt einen
separaten `R_C04`, ordnet `chkeey` vor `qoky` an und leitet die Stufe aus
`chkeey + qokaiin + qoky` ab. C07 bindet `qokeey FIRST` an
`solshedy UNIT_SEQUENCE`; dort hat `cheey` erstmals eine geschriebene Basis:
`NEXT_MEMBER(base=shedy, order=solshedy)`. Die gleiche Funktion wird nicht
stillschweigend auf DAY übertragen. `qokaiin`-Vorkommen erhalten damit
Rollen- und Identitätsmarken, ohne eine nicht geschriebene Gleichheit zu
behaupten.

`P1_SCOPE_TRANSITION` verwendet C06 und C08. C06 ordnet
`sar/sor, shedy, qol, shedaiin, sheckhy, okal, sheky, qotaiin, chedol`; die
`AFTER`-Relation ist `after(previous=ruler_step, current=successor,
domain=member_sequence)`. C08 hat in ZL die Folge
`qekeey, sheedy, qokedy, lcho, r, cheey, qokey, qotal, chedy, qoteor` und in
IT die tatsächlich andere Folge
`qokeey, sheedy, qokedy, lchor, cheey, qokey, qotal, chedy, qoteor`.
ZL `qekeey` bleibt der neue `SECOND_START`; IT `qokeey` bleibt der alte
`FIRST`. `qotal` hat die erklärte Richtung
`INCLUDES(whole=qokedy DAY, included=chedy DAYLIGHT)`. ZL `r` ist ein echter
`THEREFORE`-Konnektor mit `premise=lcho` und `conclusion=successor_selection`;
die IT-Fassung hat an dieser Quellgrenze kein entsprechendes geschriebenes
`r`, und die Folgerung bleibt dort offen. Die Basis und Ordnung von C08-
`cheey` sind ebenfalls `U02` und werden nicht erfunden.

## Vollständige Zweiglektüre

C01 eröffnet aus einem vorherigen Intervall und `qokeol` den Rahmen. Die erste
24 zählt den Rahmen, die zweite 24 misst die Rückkehr; `shckhy`, `okeeor` und
`shey` sind die mitgeschriebenen Zähl- und Folgenargumente. ZL liest
`qosheedy`; IT hat dafür das unbekannte `qocseedy`. Beide Ausdrücke bleiben
formal vollständig, aber der Member-Antezedens des `cheey` ist ungebunden.

C02 setzt ein Tagessegment und eine Nachtspanne an einem
`qokain INITIAL_POINT`. Das direkt folgende `dy THIS` nimmt genau diesen Punkt
auf. Die Stunde wird als von diesem Punkt und dem Tagessegment abgeleitete
Stunde geführt und endet an Nachtgrenze und Nachtende. Das ist eine typisierte
Rückreferenz, keine Rückreferenz auf ein späteres Wort.

C03 wählt den ersten Eintrag der Ruler-Cycle-Domäne, führt über die
Nachtfolge und den Phasenwechsel zu einer eigenen Ruler-Rolle `R_C03`.
C04 nimmt `R_C04` als Eingang, ordnet einen vorherigen Member und einen
Zeitpunkt und führt ihn über `qokal` zum Zielpunkt. Die beiden C03/C04-Ruler
werden nicht ohne Bindung identifiziert.

C05 hält Kreis und Nachtbezug an derselben Stunde, leitet dort eine Phase ab,
überschreitet die Schwelle, nimmt die helle Zeit auf und erzeugt aus der
gemessenen Dauer eine zweite, ausdrücklich benannte abgeleitete Phase. C06
verbindet Segment, Member und Einheitenzahl; die Nachfolgerrelation nach
`AFTER` endet in einer Schließung. Die IT-Form `sor` bleibt dabei offen.

C07 beginnt die Startzählung am Ursprung, wählt `FIRST` aus der
Einheitenfolge und bindet den Nachfolger tatsächlich an `shedy` und
`solshedy`. `dshedy NOW` bezeichnet hier nur den deklarierten Diskursstand;
es wird keine physische Chronologie daraus abgeleitet.

C08 unterscheidet die Leserzweige vollständig. ZL setzt einen zweiten Anfang,
einen Nachtbeginn und ein `THEREFORE`; IT schreibt stattdessen den alten
`FIRST`-Wert und die unbekannte Form `lchor`, ohne das fehlende `r` zu
ersetzen. Beide Zweige führen danach zum gewählten Member, zur gerichteten
INCLUDES-Relation von DAY zu DAYLIGHT und zum Endpunkt. Der C08-Nachfolger hat
noch keine geschriebene Basis.

C09 schließt nach der Ordnungsgrenze über die Folge und die abgeleitete
Position. ZL hat ein einzelnes `ssholshecthy`; IT hat die zwei sichtbaren
Terminals `sshol` und `shecthy`. Die beiden `qokaiin`-Vorkommen bleiben
`R_C09a` und `R_C09b`; die Zuordnung zu früheren Ruler-Identitäten ist offen.

## Explizite Konsequenz und offene Knoten

B01 definiert die einzige konkrete Endpoint-Prüfung dieses Entwurfs. Mit
`S0=qokeol`, `N_frame=daiin#1=24` und `N_return=daiin#2=24` gilt formal

`E_frame = step(S0, N_frame, FRAME_UNITS)`

und

`E_return = return_to(S0, N_return, shey)`.

Die vorgeschlagene formale Konsequenz ist `E_frame == E_return`, falls beide
24-Argumente auf den in C01 geschriebenen Rahmen und dieselbe Folge bezogen
werden. Eine alternative Zuweisung verschiedener Einheiten lässt den Vergleich
offen oder ungleich; sie kann nicht durch die bloße Wiederholung des Wortes
`daiin` beseitigt werden. Das ist eine deklarierte Vergleichsbedingung, kein
Resultat einer ausgeführten Rechnung und keine Behauptung über physische
Dauer.

Die offenen Knoten sind `U01` (C01-Memberbasis), `U02` (C08-Memberbasis und
Ordnung), `U03` (`qocseedy`), `U04` (`sor`), `U05` (`lchor`), `U06` (IT-
Schlussaufspaltung `sshol/shecthy`), `U07` (ITs fehlender THEREFORE-
Voraussetzungs- und Folgerungstext) und `U08` (Bezug des formalen Endpoint-
Vergleichs zu physischer Zeit). Der Entwurf ist deshalb ein vollständiger
Terminal- und Argumentabdeckungsvertrag mit ausdrücklich ungebundenen Knoten,
keine vollständige Übersetzung, keine Quellenidentifikation und kein
semantisches oder numerisches Testergebnis.
