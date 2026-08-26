# GDT488 — Methode

## Question

Erzeugt genau eine gelockerte GDT486-Rahmenbedingung einen zweiten lokalen
Kontrastweg für `EINSTELLEN` oder `HALTEN`, ohne Komponenten oder Lesungen zu
ändern?

## Inputs

- GDT485: 135 flüssige Records und ihre 183 exakten Eventrückprojektionen;
- GDT486: 48 gleiche-Register-Minimalpaare und 29 Kontrastregeln;
- GDT487: dreizehn wiederkehrende lokale Kontrastkanten;
- GDT428: 104 exakte Aktionsersatzrahmen.

## Method

Zwei getrennte Lockerungen werden vollständig enumeriert:

1. **Register-only:** Zwei Records dürfen aus verschiedenen Registern stammen.
   Aktive Modellfolge, lesbare Satzklasse, Eventgrenzform, Komponentenlänge,
   Komponentenpositionen und alle bis auf eine funktionale Komponente müssen
   exakt gleich bleiben. Namensslots bleiben an derselben Position.
2. **Eventprojektion:** Einzelne GDT485-Events werden ohne ihren größeren
   Recordrahmen verglichen. Register, aktives Eventmodell, Separatorfolge,
   Komponentenlänge und alle bis auf eine funktionale Komponente bleiben
   exakt gleich. Bereits in GDT486 enthaltene Recordpaare werden als Schatten
   markiert und nicht als neu gezählt.
3. Nur Paare mit `EINSTELLEN` oder `HALTEN` an einer Wechselseite werden
   behalten. Beide deutschen Bedeutungsmarker müssen in den festen Lesungen
   sichtbar sein.
4. Eine neue Kante schließt den alten Singleton nur, wenn sie zusammen mit
   wiederkehrenden GDT487-Kanten einen zweiten Weg zwischen seinen Endpunkten
   erzeugt.
5. Alle lokalen `EINSTELLEN`-Events werden zusätzlich inventarisiert. Ihr
   Rezept wird nur durch Ersetzen von `T` mit `@ACTION` gegen die exakten
   GDT428-T/R-Rahmen gehalten; dies ist Trägerunterstützung, kein neuer lokaler
   Ersatzkontrast.

## Decision rule and claim ceiling

Eine Lockerung ist nur zulässig, wenn exakt die benannte Bedingung fällt. Ein
Eventpaar gilt nicht als neu, wenn seine beiden Records schon ein
GDT486-Minimalpaar bilden. Fehlende `EINSTELLEN`-Paare werden als lokale
Kapazitätsgrenze ausgegeben und nicht durch analog gebildete Partner ersetzt.

GDT488 ordnet feste Arbeitslesungen neu; es bestätigt sie nicht unabhängig und
darf keine Bedeutung, Formulierung, Modellfolge, Recordgrenze, Oberfläche,
Rezeptfolge, Event- oder Seitenzuordnung ändern.
