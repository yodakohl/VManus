# GDT737 — Transfer auf 120 zurückgehaltene Körper

## Ergebnis

Der starke Teil von GDT736 überträgt sich, der überangepasste Teil nicht.

Auf 120 vorher nicht verwendeten gemeinsamen Restkörpern stehen H1/H2 in
199 von 328 Fällen am Zeilenanfang, H3/H4 nur in 24 von 483. Das ergibt eine
Odds Ratio von **29,50**; im reader-exakten Rest sogar **36,78**. Die mittlere
Reihenfolge ist wieder H1 (0,148), H2 (0,325), H4 (0,575), H3 (0,665). H1 ist
98/147-mal echter Absatzanfang, H2 nur 3/181-mal. Damit dürfen die vier Köpfe
als register- und positionsabhängige Recordklassen weiterverwendet werden.

Das vollständige 2x2 der Körperaffinitäten fällt dagegen durch den in GDT736
selbst festgelegten Transfer-Test:

1. H2-H3: 0,915
2. H3-H4: 0,199
3. H1-H4: 0,157
4. H2-H4: 0,147
5. H1-H2: 0,059
6. H1-H3: 0,052

H1-H4 hätte zusammen mit H2-H3 unter den beiden stärksten raw-count-Paaren
bleiben müssen. Es landet nur auf Rang 3, reader-exakt sogar auf Rang 4. Die
frühere semantische „Cluster A“-Übertragung wird deshalb auf die 24
Trainingskörper zurückgeschnitten. H2-H3 bleibt ein partieller Lead, ist aber
stark von `ain` abhängig: ohne `ain` sinkt der Kosinus auf 0,620, ohne
`ain|o|kar` auf 0,522. Eine gemeinsame Bedeutung folgt daraus nicht.

## Was an den vier Kopfrollen bleibt

- H1: an echtem Absatzanfang Absatz-/Recordöffner; sonst nur H1-Ganzform oder
  lokale Ausnahme.
- H2: zeileninitial Posten-/Untereintragsform; intern oder final ein
  registerabhängiges Feld beziehungsweise Ganzwort.
- H3: überwiegend interner oder abschließender Bezug; initial nicht automatisch
  umdeuten.
- H4: überwiegend internes Feld; initial eine Ganzform-/Registerausnahme.

Das sind strukturelle Rollen, keine Wörter. Beispiele wie `sary` (nur 1/7
initial, 5/7 final), `so`, `skaiin`, `lcheol`, `lchor` und `lsheody` verhindern
einen universellen Kopf-Renderer. Unter 95 Körpern mit beiden Stellungsachsen
liegen 72 in der erwarteten Richtung, 19 umgekehrt und vier gleich. Nur die
kleine Sektion C kehrt den Abschnittsmittelwert um.

## Die wichtige Renderer-Reparatur

Von 273 held Formen besitzen 82 eine geerbte V99R7-Ganzwortkarte. **80 dieser
82 Karten enthalten noch direkt die inzwischen verworfenen Kopfpatienten
Pulver, Samen/Saat, Wurzel oder Holz.** Sie werden nicht stillschweigend
weiterverwendet, sondern explizit quarantänisiert. Dazu gehören etwa:

- `sain`: alt „Samen, Charge II“;
- `lain`: alt „Drogenholz, Charge II“;
- `lkaiin`: alt „Holzdroge, heiß auf Stufe III“;
- `pcheol`: alt „getrockneter Pulverstoff“.

Nur `solaiin` → „drei Portionen Salz“ und `sols` → „fertige Salzspecies“
enthalten keinen alten Kopfpatienten und bleiben als schwache aktuelle
Ganzwort-Arbeitswerte erhalten. Auch sie sind keine bestätigten Übersetzungen.

Die ausführbare Reihenfolge lautet jetzt:

1. sauberes, aktuelles exaktes Ganzwort;
2. tatsächlich beobachtete Register- und Positionsrolle;
3. unbekannt.

Damit überschreibt ein alter Scheinwert wie `paiin = Pulver, Charge III` nicht
mehr die korrigierte Analyse, wenn `paiin` selbst als Körper in `spaiin` oder
`lpaiin` erscheint.

## Konkrete Bedeutungsarbeit bleibt erhalten

Der Pass verwirft die konkreten Kandidaten nicht. Er hält für alle 120 Körper
eine eigene Rolle mit Confidence, positiver Evidenz und Gegenbeleg fest. Drei
bleiben ehrlich `UNKNOWN` (`chr`, `oiir`, `oiis`), sechs sind nur strukturell;
für die übrigen bleiben konkrete Kandidaten erhalten. Das stärkste Muster ist
eine familieninterne Zustandsmatrix:

- Hitze: `ky` Grundform, `key` Form I, `keey` Form II;
- trockenes Ergebnis: `chdy` Grundform, `chedy` Form I, `cheedy` Form II;
- feuchtes Ergebnis: `shdy` Grundform, `shedy` Form I, `sheedy` Form II;
- Wertleiter: `ain`, `aiin`, `aiiin` als II, III, IV, bei weiterhin offener
  Dimension.

Daraus entstehen verständliche aggressive Kandidaten wie:

- `sain`: „Posten: Ordinal-/Wertstufe II“;
- `lain`: „internes Feld: Ordinal-/Wertstufe II“;
- `lkar`: „internes Feld: erhitzte Teil-/Fraktionsstufe I“;
- `rkar`: „erhitzte Teil-/Fraktionsstufe I; interner/später Bezug“;
- `pcheol`: „Eintrag: Trockenmaterial“.

Sie stehen bewusst in einer eigenen Kandidatenspalte und erhalten noch keine
automatische Renderer-Lizenz. So bleibt die konkrete Arbeit verfügbar, ohne
aus einem Ganzwort unbemerkt eine freie Stammübersetzung zu machen.

## Korrigiertes Gesamtmodell

Die einfachste verbleibende Architektur ist eine Mischung aus Recordmarkern,
internen Fachfeldern, gelernten Ganzformen und gebundenen Körperfeldern. Das
passt zur bereits in GDT735 belegten spätmittelalterlichen Mischarchitektur aus
Lemma, Rubrik/Hierarchie, Fachkürzel und Ganzwort besser als ein starres
Viercode-Wörterbuch.

GDT736 wird nicht verworfen. Seine Stellungsachse wird auf 120 weitere Körper
ausgedehnt; seine komplette Affinitätssemantik wird dort zurückgenommen. Der
nächste sinnvolle Schritt ist ein occurrence-gated Test der stärksten
Zustands- und Wertmatrizen in exakten Nachbarrahmen. Dafür ist kein neuer
Voynich-Seitenzugriff nötig.

## Grenze

GDT737 identifiziert kein Voynich-Wort, keine Lautung, keine historische
Abkürzungsexpansion und keinen Klartext. EVA p/s/r/l sind weiterhin moderne
Transkriptionslabels. Die 120 Körperkandidaten sind eine explizite
Arbeitstheorie, nicht freie Komponenten oder bestätigte Lexeme.
