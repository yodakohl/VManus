# Integriertes Lehrlingsmanual: Prosa und Himmelsinstrumente

## Teil I: Herbal-/Bio-Prosa

Die Prosa benutzt die zwanzig Rollen und zwölf Regeln der 93. Runde.
Sie erzeugt 116 Aussagen und 381 sichtbare Gruppen.

- **OWNER_SELECT** — sichtbaren Seiten-/Szenenbesitzer setzen
- **PART_SELECT** — Pflanzenteil oder örtlichen Gegenstand wählen
- **MATERIAL_ADD** — Medium, Portion oder Zusatz zugeben
- **MEASURE** — Sollmaß oder Stufe eintragen
- **SET** — laufenden Arbeitsposten ansetzen
- **CUT_CRUSH** — Pflanzenstoff zerteilen oder zerstoßen
- **GRADE** — kurze, längere oder volle Stufe setzen
- **HEAT** — wärmen oder temperieren
- **SETTLE** — ruhen oder absetzen
- **PASS_STRAIN** — durchlassen, auswringen oder seihen
- **WASH** — waschen oder spülen
- **DRAIN** — örtlich abführen oder ausgießen
- **COLLECT_STORE** — sammeln, auffangen oder verwahren
- **TARGET** — örtliche Zielstelle setzen
- **TRANSFER** — Posten umsetzen
- **CONTINUE** — Folge oder Fortsetzung markieren
- **READY** — Bereitschaft prüfen
- **USE_APPLY** — Mittel gebrauchen oder äußerlich anwenden
- **FASTEN** — örtlich befestigen
- **CLOSE** — lokalen Schritt schließen

## Teil II: Astro-Diagramme

- **OPEN_INSTRUMENT** — aktives Rad, Paneel oder Rosetteninstrument öffnen
- **SELECT_NAMESPACE** — nur den örtlichen Namensraum dieses Teilbilds laden
- **SELECT_LOCAL_SLOT** — sichtbaren lokalen Sektor-, Stern- oder Feldplatz wählen
- **COPY_OPAQUE_GROUPS** — alle Gruppen dieses Platzes in gegebener lokaler Folge kopieren
- **READ_WITH_LOCAL_KEY** — Wert nur mit dem Meisterschlüssel dieses Namensraums lesen
- **RESET_AT_NAMESPACE_CHANGE** — beim Rad-/Paneel-/Rosettenwechsel vollständig neu beginnen
- **PRESERVE_NO_ORIENTATION** — keinen Startpunkt, Drehsinn oder Rang ergänzen
- **NO_CROSSPAGE_JOIN** — keinen Schlüssel zwischen A1, A2 und A3 übertragen

Der Astro-Schreiber bildet keine Sätze aus den Prosa-Primitiven. Er arbeitet
wie mit einem lokalen Nomenklator: Instrument öffnen, Namensraum setzen, Platz
zeigen, Gruppen kopieren und nur im örtlichen Schlüssel lesen. Bei jedem sichtbaren
Teilbildwechsel wird neu begonnen. Keine Richtung und kein Seitenjoin werden gelernt.

## Gemeinsamer Werkstattkern

Beide Systeme teilen nur Besitzerwahl, exakte Kartentreue, lokale Namensräume und
Handrenderer. Die Prosa kombiniert Operationen; Astro kopiert Adressen. Gerade diese
Trennung macht ein gemeinsames Mehrschreiberbuch einfacher statt komplizierter.
