# GDT456 — Methode

## Question

Hängt die Fehlersicherheit von GDT455 nur an seiner absichtlich
stopp-priorisierten Nachbarauswahl, oder bleibt sie unter formbasierten,
ergebnisblinden Auswahlen bestehen?

## Inputs

- GDT441: geordneter 4.576er Strom;
- GDT454: 5.283 feste Nachbarvarianten;
- GDT455: zustandsbehafteter Stream-Treiber.

## Method

`EMPTY_RECIPE` bleibt ausgeschlossen. Sechs Regeln wählen je Quellrezept einen
nichtleeren Nachbarn, ohne die Spalten für neutrale Entscheidung, blockierte
Regel oder spätere Liveentscheidung zu lesen:

1. lexikographisch erster Nachbar;
2. lexikographisch letzter Nachbar;
3. kleinster quellengebundener SHA-256-Rang;
4. Atomlöschung zuerst;
5. Nachbartausch zuerst;
6. Klassensubstitution zuerst.

Die Paarposition jeder Aussage wird getrennt durch
`SHA256(schedule_id|statement_id) mod eligible_pairs` bestimmt. Jeder Plan
ersetzt 1.026 Karten in 513 Aussagen. Danach laufen alle 4.576 Ereignisse global
und alle 57 Besitzerbanken isoliert. Unveränderte Stopps, Burst-Rückkehr und
Bankgrenzen werden separat protokolliert.

## Decision rule and claim ceiling

Jeder Stopp muss Handlung, Argument und Scope bewahren; alle 342 isolierten
Bankläufe müssen exakt mit ihren globalen Läufen übereinstimmen. Die Auswahl
darf kein Outcome-Feld verwenden. Das Ensemble macht keine Bedeutungs-, Form-
oder Auftretensprognose.
