# GDT452 — Methode

## Question

Bleibt der laufende Leser nach jedem GDT448-Kontextstopp nicht nur formal
unverändert, sondern kann er auch die tatsächlich folgende Quellkarte lesen?

## Inputs

- 61.878 GDT448-Kontextproben;
- der 4.576-Ereignis-Strom aus GDT441;
- der integrierte GDT451-Aufnahmebefehl.

## Method

Die 5.911 gestoppten Probezeilen werden auf ihre 6.008 wirklichen
Ereignisvorkommen expandiert. Für jedes Vorkommen:

1. Zielnachbar im wirklichen Handlung-, Argument- und Aussagekontext eingeben;
2. `STOP` und unveränderten Zustand verlangen;
3. die nächste Karte derselben Aussage und desselben Besitzers aus dem echten
   Strom übernehmen;
4. sie mit dem erhaltenen Zustand und ihrem echten Ein-Karten-Ausblick lesen;
5. bei einem weiteren Stopp prüfen, ob es eine berechtigte abhängige
   Schlusskaskade ist und ob die nächste Aussage wieder einsetzt.

Ereignisse am Ende ihrer Aussage besitzen keine direkte Folgekarte und werden
separat als `NO_FOLLOWING_CARD` gezählt, nicht als Fehler.

## Decision rule and claim ceiling

Jeder Erststopp muss zustandserhaltend sein. Eine folgende Karte soll lesen,
außer sie verlangt genau den Handlungskopf, den die verworfene Karte hätte
setzen müssen; ein solcher zweiter Stopp muss spätestens an der nächsten
Aussage wieder synchronisieren.

Der Test ändert keine Bedeutung und erzeugt weder Oberfläche noch Auftreten.
