# GDT443 method

## Question

Welche der 52 neutralen `CLOSE:NO_ACTIVE_ACTION`-Kandidaten werden durch einen
sichtbar geerbten Handlungskopf gerettet, und macht es einen Unterschied, ob
der Aussage-Scope weiterläuft oder neu beginnt?

## Inputs

- GDT442s 269-Stop-Audit, daraus die 52 reinen Schlusskontextfälle;
- GDT441s ausführbarer Faktorleser und neun Handlungsköpfe;
- GDT441s aktuelle 4.576-Ereignis-Ausgabe für reale Gegenkontrollen.

## Method

Jedes der 52 Rezepte wird mit jedem der neun Handlungsköpfe zweimal geprüft:

1. `OWNER_SCOPE_RESET__SEMANTIC_HEAD_CARRIED`: Der Besitzerbank trägt den Kopf
   weiter, aber eine neue Aussage beginnt. Fokusatome fallen auf Besitzer oder
   ihre Kartenregel zurück; `DY` schließt den getragenen Kopf.
2. `STATEMENT_SCOPE_INHERITED__SAME_HEAD`: Derselbe Kopf ist auch im laufenden
   Aussage-Scope aktiv. Fokusatome binden deshalb direkt an ihn, sofern ihre
   alte Selectorregel das verlangt.

Das ergibt 52×9×2 = 936 Zellen. Grün, Gelb und Stop stammen direkt aus GDT441;
kein Rezept wird wegen seines derzeitigen Beobachtungsstatus bevorzugt.
Anschließend werden alle realen Vorkommen der sechs bereits beobachteten
Rezepte aus der aktuellen Ausgabe gezogen.

## Decision rule and claim ceiling

Ein eingehender Kopf darf nur die fehlende Kontextstelle besetzen. Er darf
keine neue Fokus-Kante, Paarregel oder Bedeutung erzeugen. Ein Stop bleibt
stehen. Die Matrix liest nur einen bereits sichtbaren Kandidaten und erzeugt
weder Oberfläche noch Vorkommen.
