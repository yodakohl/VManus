# GDT728 — die geerbte Dosis-Sprache ist in vier reale Rollen zerlegt

## Ergebnis

GDT728 besteht. Das vollständige Wörterbuch enthält 60 geerbte globale
Ganzwortreadings mit Dosiswortlaut an zusammen 293 Vorkommen. Der explizite
Dispatch ergibt:

| Rolle | Ganzformen | Vorkommen | Arbeitsbedeutung |
|---|---:|---:|---|
| `PORTION` | 55 | 217 | zählbare oder bearbeitete Arbeitsmenge |
| `TEIL` | 1 | 1 | relativer Anteil (`dolas`) |
| `MASS` | 1 | 4 | exakte Abguss-Messform (`doly`) |
| `WERT` | 3 | 71 | offene Zubereitungswertstufe (`odan/odain/odaiin`) |
| `HOLD` | 0 | 0 | in dieser explorativen Runde nicht nötig |

In beiden semantischen Wörterbuchfeldern verschwinden je 61 Dosis-Tokens.
Die Evidenzprosa wird nicht bereinigt, weil dort die frühere Hypothese als
Gegenbeleg oder Lineageinformation stehen darf.

## Konkrete Verbesserungen

Die neue Ausgabe sagt beispielsweise:

```text
chedain       zwei Portionen bis zur Mittelstufe getrockneter Droge
chdain        zwei Portionen Trockendroge
ddor          eine Portion abmessen
dolas         Drogenstoff anteilig abmessen
doly          ein Maß Abguss
odaiin        Zubereitung, Wertstufe III
kodaiin       drei Portionen erhitzter Zubereitung
deey          die letzte Portion abmessen
```

Damit wird der Unterschied sichtbar, den `Dosis` zuvor verdeckt hat: ein
Arbeitsanteil ist nicht automatisch eine therapeutische Gabe, ein relativer
Teil ist keine Portion, ein ausdrücklich lizenzierter Messkopf darf `Maß`
heißen, und ein offener Wertkopf darf nicht zur Menge umgedeutet werden.

## Warum das kein globaler Wortstammexport ist

Die 60 Entscheidungen sind exakte Ganzwortkarten. GDT627s freie `d`-Reihe
bleibt eine Wertreihe, deren Sachachse der sichtbare Kopf auswählt. Besonders
`odan/odain/odaiin` werden deshalb gerade nicht zu ein/zwei/drei Portionen.
Auch `doly=Maß` und `dolas=Teil` gelten nur für diese vollständigen
Whitespace-Formen. `d`, `dain`, `daiin`, `dol` oder `a` gewinnen null neue
Relation- oder Komponentenpunkte.

## Historischer Plausibilitätsrahmen

Zeitnahe Rezeptregister unterscheiden tatsächlich relative Teile und konkrete
Einheiten: Theodoricus teilt eine Unze Material in drei Teile, während
mittelbairische Feuerwerksrezepte des frühen 15. Jahrhunderts `lott` und das
*Liber de coquina* Unzen nennen
([Mulomedicina](https://d-nb.info/1279095032/34),
[GNM Hs 1481a](https://kdih.badw.de/datenbank/handschrift/39/2/5),
[Liber de coquina](https://corpus.atliteg.org/opera/liber-de-coquina-a/93)).
Ein pharmakologischer Überblick trennt Zutatenmengen, Herstellung,
Verabreichung und Dosierung ausdrücklich
([NCBI Bookshelf](https://www.ncbi.nlm.nih.gov/books/NBK606146/)).
Das macht den Renderer historisch natürlicher; es identifiziert kein einziges
Voynich-Wort.

## Stabilität

- alle 1.586 Wörterbuchreadings behalten Score, Confidence, positive Evidenz
  und Gegenbeleg;
- alle 324 aktiven V99-Readings sind vollständig bytegleich;
- alle 1.202 nicht betroffenen globalen Readings sind vollständig bytegleich;
- der 51-Zeilen-Reader und vier weitere aktive Reader-Artefakte sind bytegleich;
- Scope, Exportrechte, Struktur-Tags und Komponentenwerte ändern sich nicht.

Das kanonische Komplettwörterbuch ist jetzt
`artifacts/V99R2_COMPLETE_WORD_CONFIDENCE.tsv`.

## Nächster Zug

Als Nächstes sollen die übrigen geerbten römischen `Portion I–IV`-,
`Menge/Klasse`- und `Grad-/Maßwert`-Formulierungen inventarisiert werden. Das
Ziel ist derselbe Kopfdispatch ohne neue Seiten: sichtbarer Stoffkopf zu
cardinaler Menge, Qualitätskopf zu Grad, nackter Kopf zu Wert und nur ein
expliziter Einheitenkopf zu Maß.
