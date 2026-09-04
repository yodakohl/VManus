# GDT788 — `dal` bleibt ein brauchbares Ganzwort, aber noch kein frei einsetzbarer Bedeutungsrest

## Ergebnis

Der aktuelle beste Arbeitswert bleibt:

```text
dal = Material I, abgemessen
```

Er gilt für das vollständige Wort `dal`, nicht automatisch für jedes Wort, das
auf denselben drei EVA-Zeichen endet. Das ist der entscheidende Unterschied
dieser Runde. Die Formenfamilie ist real und groß: **107 rohe `*dal`-Formen mit
415 Token**, davon **80 Formen und 304 Token reader-exakt**. Das nackte `dal`
allein besitzt 147 exakte Vorkommen auf 58 physischen Folios.

Auch das kontrollierte Raster ist vollständig. Zehn verschiedene linke Ganze
besitzen jede der vier Formen `Xal/Xdal/Xar/Xdar`; alle **40 Zellen** kommen
mindestens zweimal auf mindestens zwei Folios vor. Formal ist das viel stärker
als eine zufällige Handvoll ähnlich geschriebener Wörter.

Trotzdem trägt die konkrete Bedeutung nicht gleichmäßig. Der strengere
Familienvergleich sagt `Xdal` aus den drei Schwesterwörtern voraus:

```text
SHIFT = Xal + Xdar - Xar
```

Er schlägt `Xal` und ein unabhängig nach Form ausgewähltes Ganzwort zugleich
nur bei **2/10** Reihen. Der günstigere direkte Versuch

```text
CORE = Xal + dal - al
```

schafft **4/10**. Das ist ein interessanter Teiltreffer, aber keine Regel, mit
der wir die restlichen sechs Reihen sicher lesen könnten. Die Arbeitsentscheidung
lautet daher:

```text
FORM:       starke al/dal/ar/dar-Oberflächenfamilie
dal:        Material I, abgemessen             [eigenes Ganzwort]
Xdal:       konkrete formgebundene Ganzwortkarten
TRANSFER:   WHOLE_ONLY
d:          nicht automatisch „abmessen“
al:         nicht automatisch „Material“
EXPORT:     kein freier dal-Rest
```

Das Ergebnis lässt keine Oberfläche leer. Für alle 107 Formen stehen konkrete,
austauschbare Arbeitswerte mit Konfidenz, positiver Evidenz, Gegenbeleg und zwei
semantischen Rivalen bereit. Es sind **37 gezielte Karten**, **46 exakte
Singleton-Fallbacks** und **24 raw-only Fallbacks**. Die gemeinsamen
Material-/Messanzeigen sind ein einziger explorativer Familienprior, nicht 107
unabhängige Entzifferungen.

## Was die zehn Reihen tatsächlich sagen

Alle Werte sind Profilähnlichkeiten, keine Wahrscheinlichkeiten.

| Sicht | SHIFT | CORE | `Xal` | gelerntes Ganzwort | SHIFT/CORE schlagen beide |
|---|---:|---:|---:|---:|---:|
| Vollprofil | .718 | .729 | .710 | .703 | 2/10 · 4/10 |
| nur Struktur | .827 | .824 | .839 | .826 | 3/10 · 3/10 |
| ohne Register | .720 | .747 | .713 | .716 | 2/10 · 5/10 |
| nur Bedeutungsumfeld | .317 | .396 | .250 | .260 | 2/8 · 2/8 |

Der CORE-Mittelwert ist der beste Einzelwert. Er darf aber nicht mit einem
breiten Treffer verwechselt werden: Seine Gewinne liegen je nach Sicht in
verschiedenen Reihen. Im entscheidenden Bedeutungsumfeld sind zwei Reihen
komplett `NA`, und CORE schlägt beide Kontrollen nur zweimal. Eine robuste
Komponente müsste ihre Wirkung über deutlich mehr X-Kontexte behalten.

| X | Ziel | exakte Token/Folios | SHIFT | CORE | `Xal` | gelernt | Gewinner gegen beide |
|---|---|---:|---:|---:|---:|---:|---|
| `ch` | `chdal` | 13/11 | .771 | .721 | .802 | .605 | keiner |
| `che` | `chedal` | 15/7 | .730 | .768 | .718 | .633 | beide Modelle |
| `o` | `odal` | 11/10 | .876 | .689 | .591 | .751 | SHIFT |
| `oke` | `okedal` | 2/2 | .679 | .769 | .720 | .851 | keiner |
| `ol` | `oldal` | 2/2 | .524 | .641 | .591 | .624 | CORE |
| `ote` | `otedal` | 3/3 | .795 | .770 | .772 | .807 | keiner |
| `qo` | `qodal` | 6/6 | .637 | .696 | .606 | .645 | CORE |
| `qoke` | `qokedal` | 2/2 | .739 | .761 | .821 | .696 | keiner |
| `sh` | `shdal` | 3/3 | .674 | .707 | .709 | .651 | keiner |
| `she` | `shedal` | 7/3 | .754 | .769 | .766 | .762 | CORE |

`che` ist die einzige Reihe, in der beide Transfermodelle beide Kontrollen
schlagen. SHIFT gewinnt zusätzlich bei `o`; CORE bei `ol`, `qo` und `she`.
Das ergibt keine gemeinsame trockene, feuchte, erhitzte oder gekühlte Schale.

## Die wichtige Leakage-Korrektur

Ein früher Pilot sah etwas freundlicher aus, hatte aber einen schlechten
Ganzwortvergleich: Formen wie `chtal`, `cheeal` oder `chedar` konnten als
scheinbar unabhängige Spender zurückkehren, obwohl sie bereits zur getesteten
AL/DAL-Linie gehörten. GDT788 schließt jetzt aus dem Bedeutungsumfeld aus:

- 742 rohe Oberflächen aus dem gesamten `al/dal/ar/dar`-Endungsverbund;
- 172 GDT754-Provenienzformen;
- 82 GDT737-Quarantäneformen;
- 55 Karten mit GDT653/654/655/711/764-Linie.

Die Vereinigungsmenge hat **996 Oberflächen**. Vom 46er-GDT746-Kontrollpool
bleiben 32 wirklich unabhängige Ganzwörter. Nach dieser Korrektur stimmen der
eingebaute Lauf und ein unabhängig geschriebener Replay bis auf 1e-12 überein.

Der exakte Endungsverbund innerhalb des zugelassenen Korpus umfasst insgesamt
568 Oberflächen und 3.110 Vorkommen:

| längste Endung | Oberflächen | exakte Token |
|---|---:|---:|
| `dal` | 80 | 304 |
| `dar` | 92 | 395 |
| nur `al` | 171 | 1.063 |
| nur `ar` | 225 | 1.348 |

Damit kann alte Familienprosa den Test nicht mehr über Nachbarfelder heimlich
bestätigen.

## Ist der gemeinsame Kern „Menge“, „Material“ oder „Teil“?

Die direkte Achsenprüfung gibt darauf noch kein Ja. Für jede X-Reihe wird
verglichen, ob der Schritt `al→dal` dieselbe Umgebungsänderung erzeugt wie
`ar→dar`.

- **AMOUNT:** Bei Radius 1 haben 0/8 informative Reihen denselben nichtnull
  gerichteten D-Effekt; bei Radius 3 nur 2/9. Der mittlere gemeinsame D-Effekt
  ist winzig (+.019 beziehungsweise +.015; Vorzeichenflip p=.563/.848).
- **MATERIAL:** 0/8 beziehungsweise 4/9 Reihen laufen gleichgerichtet. Der
  erwartete AL-vor-AR-Trägerkontrast ist sogar leicht negativ und instabil
  (-.039/-.018; p=.531/.727).
- **PART:** Keine informative Reihe liefert in beiden Trägern denselben
  nichtnull D-Effekt. Auch der auf AR ausgerichtete Trägerkontrast ist negativ
  (-.100/-.074; p=.250/.234).
- **VALUE:** Je fünf von zehn Reihen teilen nur die Richtung; der gemeinsame
  Effekt liegt praktisch bei null (+.009/-.009).

Ein positiver AMOUNT-Difference-in-Differences-Mittelwert ist vorhanden, wird
aber wesentlich von `ol` getragen und bedeutet gerade keine breite
Familienübereinstimmung. Das Raster erlaubt deshalb weiterhin drei brauchbare
Arbeitsszenarien: gemessener Materialeintrag, Mengen-/Wertfeld oder gelernter
technischer Ganzname. Keines gewinnt als universelle Komponente.

## Schreibgrenzen: viel getrenntes `dal`, aber kein innerer Beweis

Im Korpus stehen **185** rohe Folgen `X dal`. **115** davon bewahren beide
Wörter und ihre Reihenfolge in allen drei aktuellen Lesern. Das bestätigt,
dass `dal` ein sehr reales eigenständiges Wort ist.

Nur vier linke Ganze kommen sowohl getrennt als auch in einer anderen Stelle
fusioniert vor:

```text
cheo  chol  ol  y
```

Das zeigt Grenzbeweglichkeit. Es zeigt nicht, dass die fusionierte Form an der
gleichen Stelle als `X + dal` gelesen werden muss. Unter allen 304 exakten
`*dal`-Vorkommen gibt es **keinen** gleichlokalen aktuellen `X|dal`-Split.
Stolfi findet bei 47 erreichbaren längeren Zielvorkommen 47 fusionierte und
null gesplittete Lesungen. Der einzige aktuelle Alternativsplit
`qokeeodal → qokeeo dal` ist raw-only und nicht reader-exakt.

Die 115 getrennten Spannen bestehen den formalen Packet-Validator als
Erfassungsdaten, bleiben aber absichtlich nicht score-ready: Es handelt sich um
Textreihenfolge, nicht um unabhängige Bildgeometrie oder semantische Evidenz.

## Konkrete Arbeitskarten

Die wichtigsten Karten lauten jetzt:

| Form | bevorzugter Arbeitswert | Konfidenz* | stärkste Rivalen |
|---|---|---:|---|
| `dal` | **Material I, abgemessen** | 72 | Rohdrogenposten · Mengen-/Wertfeld I |
| `chdal` | trockenes Material I, abgemessen; Anfangsstufe | 64 | trockener Drogenposten · Trockenfeld |
| `chedal` | trockenes Material I, abgemessen; Mittelstufe | 66 | eingedickter Drogenposten · Trockenfeld |
| `shdal` | feuchtes Material I, abgemessen; Anfangsstufe | 46 | eingeweichter Drogenposten · Feuchtefeld |
| `shedal` | feuchtes Material I, abgemessen; Mittelstufe | 46 | mazerierter Drogenposten · Feuchtefeld |
| `odal` | Materialansatz I, abgemessen | 52 | Ansatzportion I · fertige Zubereitung I |
| `qodal` | abgemessener Materialposten I | 48 | Ansatzportion I · Mengen-/Wertfeld I |
| `saldal` | abgemessene Rohdroge | 60 | benannte Drogenform · Rohsalz |
| `cheodal` | trockenes Ansatzmaterial I, abgemessen | 44 | Arzneiextrakt · Trocken-/Mengenfeld |
| `qokeedal` | erhitztes Material I, abgemessen; Endstufe | 40 | Arzneizubereitung · Wärme-/Endfeld |
| `otedal` | gekühltes Material I, abgemessen; Mittelstufe | 38 | Arzneiextrakt · Kälte-/Mittelstufe |
| `ydal` | Materialposten I, Grundform, abgemessen | 34 | Drogenposten · Material-/Formfeld |

\*Die 0–100-Werte sind redaktionelle Evidenzgewichte, keine Wahrscheinlichkeiten.

Die 46 exakten unaufgelösten Singletons erhalten knapp `Materialposten I`;
ihre beiden sichtbaren Rivalen sind `Material I, abgemessen` und
`Mengen-/Wertfeld I`. Die 24 übrigen raw-only Fallbacks erhalten dieselbe
Arbeitsanzeige, aber nur Konfidenz 12 und keine Renderer-Lizenz. Jede Karte ist
explizit ersetzbar.

Ein fokussiertes Beispiel zeigt den beabsichtigten Nutzen ohne künstlichen
Fließtext:

```text
f87r.11  psheodshy · dal · shee · saldal · shol · aldy

Arbeitsanzeige am Ziel:
psheodshy · dal · shee · ⟦saldal = abgemessene Rohdroge⟧ · shol · aldy
```

Das ist konkreter als „Arbeitsgut bearbeiten“, ohne die unbekannten Nachbarn
mit generischem Satzkitt zu übermalen.

## Historische Passform und Grenze

Die vorhandenen Vergleichsquellen um 1400–1420 zeigen genau die grundsätzlich
mögliche Architektur: gelernte Drogennamen können neben gebundenen Feldern für
trocken/feucht, heiß/kalt, Grad, Pflanzenteil, Zahl und Rezeptmenge stehen.
Damit ist ein dichtes Raster plus Ganzwörter historisch plausibel. Keine Quelle
identifiziert aber EVA `dal`, `d` oder `al` mit einem lateinischen Wort, einer
Maßeinheit oder einem Lautwert.

GDT788 bestätigt deshalb kein Lexem und keine Substanz. Es liefert etwas
Nützlicheres für die nächste Runde: eine saubere Trennung zwischen dem starken
eigenständigen Wort `dal`, einem echten formalen Raster und den nur teilweise
haltenden Bedeutungsanzeigen.

## Nächster Hebel

Als nächstes folgt `ar` mit demselben Protokoll, danach `ol`. Für `ar` ist die
konkrete Frage schärfer: Bleibt die bisherige Ganzwortrolle **Anteil/Fraktion**
über mehrere linke Familien stabiler als `dal`, oder zerfällt auch sie in
gelernte Ganze? Die 996er Leakage-Maske und der bereinigte Kontrollpool werden
unverändert übernommen.

GDT788 verwendet keine neue Seite, kein Bild, keine OCR oder Transkription;
`f84/f84r` bleiben gesperrt. Es exportiert keinen EVA-Teilstring und erteilt
keine neue globale Renderer-Lizenz.
