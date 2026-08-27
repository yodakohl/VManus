# GDT546 — Methode

## Question

Lassen sich GDT543s 81 Fragmentkarten und GDT545s vier qualifizierte
Sekundärbrücken in einen einzigen ausführbaren Reader kompilieren, der jede
bekannte Oberfläche vollständig liest, alle Stützkanäle getrennt zeigt und
für unbekannte Oberflächen keine ähnliche Karte erfindet?

## Inputs

- GDT543: 81 Fragmentkarten, 93 gerichtete Ausbauarme und 16 wiederkehrende
  Hauptstammfamilien;
- GDT544: die 16 Karten mit Kontext- und/oder Andockkantenwarnung;
- GDT545: vier Sekundärbrücken und zwölf nicht reparierte Defaults.

Alle Quellen stammen aus den bereits zugelassenen dreißig Seiten. GDT546 liest
keine Manuskripttranskription und keine neue Seite.

## Method

1. Die 81 GDT543-Karten werden ausschließlich über ihre exakte Oberfläche
   indiziert. Rezept, Bedeutungszeilen, Hauptstamm, Kontext und Stützklasse
   werden unverändert übernommen.
2. Jeder der 93 linken/rechten Ausbauarme wird auf die entsprechende
   Oberfläche und Seite zurückgespielt. Sichtbares Affix, Kanaltyp,
   Rezeptvariante und Andockkante bleiben getrennte Felder.
3. Für die 16 alten Warnkarten wird der ursprüngliche Grund eingetragen. Die
   vier GDT545-Brücken werden als zweite Herleitung ergänzt; die übrigen zwölf
   werden als vollständige, aber explizit ungestützte Defaults markiert.
4. Die Anzeige erzeugt zwei verschiedene Spuren: eine Rezeptformel
   `Ausbau + [Hauptstamm] + Ausbau` und eine sichtbare Form. Keine der beiden
   ersetzt die deutsche Arbeitslesung.
5. `read_fragment.py` akzeptiert nur einen der 81 exakten Schlüssel. Eine
   unbekannte Form liefert `STOP_UNKNOWN_FRAGMENT_SURFACE` und erbt weder per
   Editdistanz noch per Teilstring eine Bedeutung.
6. Der unabhängige Validator spielt alle Quellfelder, Formeln, Arm-Joins,
   Familienzahlen, Brücken, Defaults und drei CLI-Wege zurück und prüft einen
   byteidentischen Generator-Neulauf.

## Decision rule and claim ceiling

Der Reader gilt als kompiliert, wenn genau 81 eindeutige Schlüssel alle
GDT543-Karten abdecken, alle 93 Arme zurückgespielt werden, die 16 Warnkarten
exakt in vier Sekundärbrücken und zwölf Defaults zerfallen, jede Karte beide
deutschen Lesespalten behält und ein unbekannter Schlüssel sicher stoppt.

Das ist eine ausführbare Arbeitsausgabe, keine unabhängige Bestätigung der
deutschen Bedeutungen. Sichtbare Containment, alte Andockkanten und
Kontextgleichheit sind verschiedene Stützkanäle. GDT546 etabliert weder
Klartext noch Sprache, Lautwerte, historische Codebuchidentität, neue
Wortbedeutungen oder eine Regel für unbekannte Oberflächen.
