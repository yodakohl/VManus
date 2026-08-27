# GDT520 — Sichtbare Fugen statt freier Zerlegung

## Ergebnis

GDT519 hatte die richtigen Bestandteile, aber noch keine Antwort auf eine
einfache Schreiberfrage: Wann ist ein sichtbares Zeichen ein eigener Stamm,
und wann steckt es in der Schreibform eines größeren Pakets?

GDT520 ergänzt dafür zwei kleine Regeln:

- eine belegte kürzere Segmentierung erhält einen leichten Vorzug;
- jede sichtbare Fuge wird danach bewertet, wie oft dieselbe Zeichenpaar- und
  Vierzeichenumgebung in den alten Karten offen oder innerhalb eines
  Renderers vorkommt.

Aus den 1.558 alten Formen entstehen 7.433 konkrete Fugenstellen, 199
Zeichenpaar-Zellen und 2.037 lokale Fenster. Das ist nun eine ausführbare
Schreibregel, kein weiteres Wörterbuch aus Sonderphrasen.

## Was sich verbessert

| Deck | Modell | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme | tiefster Rang |
|---|---|---:|---:|---:|---:|---:|---:|
| vier rotierende Altgruppen | GDT519 | 1.082 | 1.319 | 1.377 | 1.418 | 2.152 | 23 |
| vier rotierende Altgruppen | GDT520 | **1.089** | **1.321** | **1.381** | 1.416 | **2.139** | **22** |
| aktuelle 159 Formen | GDT519 | 138 | 153 | 157 | 158 | 192 | 8 |
| aktuelle 159 Formen | GDT520 | **139** | **154** | **158** | 158 | **190** | 9 |

Bei den aktuellen Formen werden zwei alte Fehler richtig umgestellt und ein
alter Treffer verloren. Netto kommt ein Rang-1-Treffer hinzu; zwanzig Formen
bleiben offen.

## Der wichtige Ganzrenderer

`chekeey` wird wieder richtig als

`chek~CH+K | ee~EE | y~Y`

gelesen. Die Konkurrenz `ch~CH | e~E | k~K | ee~EE | y~Y` ist sichtbar
möglich, benötigt aber fünf statt drei lizenzierte Segmente und öffnet zwei
Fugen, die das alte Material in dieser Umgebung eher geschlossen lässt.

Das ist genau die gesuchte Mischung: `CH`, `K`, `EE` und `Y` bleiben
produktive Einzelstämme; `chek` darf zugleich eine gelernte Schreibform für
`CH+K` sein.

Auch `shckheody` wechselt richtig zu `SH+CH+K+E+O+DY`.

## Die Grenze ist jetzt sichtbar

`psheody` wechselt leider in die Gegenrichtung von
`P+SH+E+O+D_ADDR+Y` zu `P+SH+E+O+DY`. Damit zeigt gerade der Fehler etwas
Nützliches: Die sichtbare Endung `...eody` trägt in unserem Arbeitscodebuch
tatsächlich beide Kompositionen. Eine stärkere rein graphische Fugenregel
würde eine der beiden Familien nur gewaltsam ausradieren.

Der nächste sinnvolle Schritt ist deshalb nicht mehr Fugenstärke, sondern ein
kurzer **Rezeptschwanz-Kontext**: Welche vorhergehenden Komponenten lizenzieren
`O+DY`, welche `O+D_ADDR+Y`, welche `O+L` und welche `OL`? Das lässt sich auf
den vorhandenen Seiten lernen, ohne eine neue Seite zu öffnen.

## Praktischer Zustand

Die vollständige Reihenfolge bleibt:

```text
exaktes Ereignis
> bekannte Oberfläche/Rolle
> endliche Compiler-Kandidaten
> sichtbarer Stamm-Transduktor
> Segmentökonomie und Fugenlizenz
```

Die Fugen sind Arbeitsgrenzen im Renderer. Sie sind weder bestätigte
Wortgrenzen noch Laut-, Morphem- oder Klartextgrenzen.
