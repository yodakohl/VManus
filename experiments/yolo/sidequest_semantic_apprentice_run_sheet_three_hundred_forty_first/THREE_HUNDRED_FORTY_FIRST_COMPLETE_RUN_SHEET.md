# Vollständiger Lehrlingslaufzettel

## H1 / f10r / HAND_A_BARE

**Eingang:** Abgebildeter Wurzelteil — Bildbesitzer f10r.
**Arbeit:** 2 Aussagen, 7 Mikrogänge; Hauptprogramm `P12_BESTAND_REFERENZIEREN`.
**Ausgang:** Bemessener Wurzel-Wasseransatz mit Kurzrest.
**Weiter:** B1 (SAME_HAND_DELIVERY).

## H2 / f10r / HAND_A_BARE

**Eingang:** Laufender Auszugsansatz — Voriger Artikel unter demselben Pflanzenbild.
**Arbeit:** 3 Aussagen, 8 Mikrogänge; Hauptprogramm `P12_BESTAND_REFERENZIEREN`.
**Ausgang:** Fortgesetzter Auszugsansatz mit Zutatsollmaß.
**Weiter:** B1 (SAME_HAND_DELIVERY).

## H3 / f11r / HAND_B_Q_OPERATIONAL

**Eingang:** Abgebildetes Blütenkraut — Bildbesitzer f11r.
**Arbeit:** 4 Aussagen, 7 Mikrogänge; Hauptprogramm `P12_BESTAND_REFERENZIEREN`.
**Ausgang:** Gestandener und nachgeseihter Klarauszug.
**Weiter:** B2 (SAME_HAND_DELIVERY).

## H4 / f55v / HAND_C_S_ENTRY

**Eingang:** Abgebildetes Blattmaterial — Bildbesitzer f55v.
**Arbeit:** 4 Aussagen, 6 Mikrogänge; Hauptprogramm `P01_DOSIEREN`.
**Ausgang:** Geteilte und lang erwärmte Auszugsportion.
**Weiter:** B4 (SAME_HAND_DELIVERY).

## H5 / f56r / HAND_D_EXPANDED

**Eingang:** Abgebildeter Stängel-/Pflanzenteil — Bildbesitzer f56r.
**Arbeit:** 6 Aussagen, 11 Mikrogänge; Hauptprogramm `P03_AM_ZIEL_EINSETZEN`.
**Ausgang:** Gebundener Zutaten- und Auszugsansatz für Folgeposten.
**Weiter:** B4 (CROSS_HAND_RELAY_D_TO_C).

## B1 / f81v / HAND_A_BARE

**Eingang:** H1-Wurzelansatz und H2-Folgeansatz — Gemeinsames Behandlungsbecken.
**Arbeit:** 21 Aussagen, 37 Mikrogänge; Hauptprogramm `P06_FORTSETZEN`.
**Ausgang:** Bemessene, behandelte und überführte Beckenportionen.
**Weiter:** TERMINAL_APPLICATION_SHELF_B1 (LOCAL_SHELF_NO_DRAWN_NEXT_POINTER).

## B2 / f82r / HAND_B_Q_OPERATIONAL

**Eingang:** H3-Klarauszug und lokale Beckenposten — Mehrere f82r-Stationen.
**Arbeit:** 22 Aussagen, 40 Mikrogänge; Hauptprogramm `P10_ABZIEHEN_ABFUEHREN`.
**Ausgang:** Lang behandelte, abgesetzte und klar abgezogene Stationsportionen.
**Weiter:** TERMINAL_APPLICATION_SHELF_B2 (LOCAL_SHELF_NO_DRAWN_NEXT_POINTER).

## B3 / f83r / HAND_D_EXPANDED

**Eingang:** Lokal bereitgestellter Stationsposten — Korb, Randgefäße und verbundenes Paar.
**Arbeit:** 34 Aussagen, 56 Mikrogänge; Hauptprogramm `P07_UEBERFUEHREN`.
**Ausgang:** Überführte, bemessene und abgesetzte Gefäßportionen.
**Weiter:** TERMINAL_WORK_SHELF_B3 (LOCAL_SHELF_NO_DRAWN_NEXT_POINTER).

## B4 / f83r / HAND_C_S_ENTRY

**Eingang:** H4-Auszugportion und H5-Folgeposten — Anwendungs-/Durchlasspaar und Seitenstationen.
**Arbeit:** 16 Aussagen, 23 Mikrogänge; Hauptprogramm `P05_LANG_BEHANDELN`.
**Ausgang:** Am Ziel behandelte, durchgelassene und gesammelte Portionen.
**Weiter:** TERMINAL_APPLICATION_SHELF_B4 (LOCAL_SHELF_NO_DRAWN_NEXT_POINTER).

## B5 / f83r / HAND_D_EXPANDED

**Eingang:** Laufender Posten der linken Randstation — Linke offene Randstation.
**Arbeit:** 3 Aussagen, 6 Mikrogänge; Hauptprogramm `P07_UEBERFUEHREN`.
**Ausgang:** Überführter Folgeposten.
**Weiter:** TERMINAL_WORK_SHELF_B5 (LOCAL_SHELF_NO_DRAWN_NEXT_POINTER).

## B6 / f83r / HAND_D_EXPANDED

**Eingang:** Laufender Posten des rechten Mehrports — Rechter S-Lauf/Mehrport.
**Arbeit:** 1 Aussage, 4 Mikrogänge; Hauptprogramm `P06_FORTSETZEN`.
**Ausgang:** Fortgesetzter und zielgesetzter Mehrportposten.
**Weiter:** TERMINAL_WORK_SHELF_B6 (LOCAL_SHELF_NO_DRAWN_NEXT_POINTER).

## Tagesregel

Der Lehrling nimmt nie einen Stoffnamen aus der Kartenform allein. Eingang und
Besitzer kommen vom Bild beziehungsweise vom vorher markierten Werkstattposten.
Die Karten bestimmen Reihenfolge, Maß, Prozess, Dauer, Ziel und Abschluss. Wo kein
weiterer Bildzeiger existiert, wird das Ergebnis auf dem lokalen Arbeits- oder
Anwendungssims abgelegt statt in eine erfundene nächste Leitung geschickt.
