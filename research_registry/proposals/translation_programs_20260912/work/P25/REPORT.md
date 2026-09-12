# P25 — Definitionen gegenüber Zutatenlisten

2026-09-12. **Der konkrete Zwei-Fraktionen-Entwurf ist als Zutatenliste formulierbar; eine Begriffsdefinition oder Hierarchie ist damit nicht identifiziert.** Vollständiger erster Durchgang: vier HERB4-Absätze, 145 Gruppen, neun Ganzwortannahmen an 34 Positionen; 111 Gruppen offen. Zusätzlich alle 15 dokumentierten f88r-Beschriftungen / 16 Gruppen geprüft: null exakte Wortübertragungen.

Die vollständig ausgerichteten Fassungen [D](READING_D.md) und [L](READING_L.md) verwenden dieselben Inhaltskandidaten. [CHAPTER.md](CHAPTER.md) enthält alle vier Glossareinträge, die vollständigen Listenrivalen auf Hypothesenebene und den sechs Knoten umfassenden Begriffsbaum. Es ist keine nahezu vollständige Übersetzung entstanden.

## Was die konkreten Konsequenzen entscheiden

| Konsequenz | Definition D | Liste L |
|---|---|---|
| f17r: cthy chor shor | drei Klassifikationen desselben Gegenstands | drei Listenposten |
| f21r: shol chol shol | feucht/trocken/feucht am selben Gegenstand: zwei Wechselkonflikte | dieselben zwei Konflikte am selben Posten |
| f21r: spätere chor chol | weiterer Gegenkontrast zum noch feuchten Gesamtgegenstand | neuer Blütenposten, kein Gegenkontrast zum alten Posten |
| f32v: chocthy daiin cthaiin daiin | derselbe homogene Gegenstand fein III und grob III: Konflikt | feine Fraktion, drei Portionen; grobe Fraktion, drei Portionen |
| f29v: wiederholtes chol | wiederholte gleiche Eigenschaft, kein Konflikt | wiederholte Eigenschaft am jeweiligen Posten, kein Konflikt |

Vier protokollierte Konfliktpaare bei D, zwei bei L. Diese sind abhängig: die drei D-Feucht/Trocken-Kontraste auf f21r gehören zu einer einzigen widersprüchlichen Eigenschaftsfolge, nicht zu drei unabhängigen Widerlegungen. Die vierte D-Kollision ist fein/grob auf f32v. Alle Endpunkte stehen in [CONTRADICTIONS.tsv](CONTRADICTIONS.tsv). L besitzt zusätzlich eine ungebundene Feuchte auf f17r.4:2. Keine Fassung ist widerspruchsfrei.

Der brauchbare Arbeitsentwurf lautet unter den ausdrücklich angenommenen Werten:

> f32v.9: … feine Fraktion: drei Portionen; grobe Fraktion: drei Portionen.

Damit sind zwei verschiedene Eingaben mit derselben Menge ausdrückbar. Es ist keine neue Entdeckung der zwei Kopf/Wert-Felder: diese waren bereits GDT809 bekannt. Neu ist die gemeinsame konkrete Fraktionsdeutung innerhalb der vier ganzen Lesungen. Dass chocthy fein oder cthaiin grob bedeutet und daiin drei, folgt nicht daraus. Ein Vertauschen von fein/grob lässt diesen Test unverändert; auch andere zwei Fraktionsarten könnten denselben Bau erfüllen. Eine Mengen- gegenüber Gradbedeutung ist nicht ausgewählt.

## Alle Grenzen bleiben sichtbar
Vier von acht daiin werden unmittelbar an Klassen-/Qualitätsfelder gebunden; vier bleiben in BEIDEN Fassungen offen: f32v.8:2, .8:3, .8:5 und f29v.1:11. Das Doppel wird nicht addiert oder weggelassen. [VALUE_FIELDS.tsv](VALUE_FIELDS.tsv) gibt jede Stelle aus. ZL/IT gegen RF-Wortgrenzen auf f32v.8 bleiben ungelöst; kein allgemeines cth-Morphem wird abgeleitet.

Alle sechs Paare der vier Einträge unterscheiden sich in den gewählten Klassen-/Qualitätsmengen; [ALL_ENTRY_PAIRS.tsv](ALL_ENTRY_PAIRS.tsv) benennt die Unterschiede. Das identifiziert keine Definition: Listen verschiedener Zusammensetzung unterscheiden sich ebenso. Es fehlt eine geschriebene Beziehung, die eine Klasseninklusion statt Mitvorkommen verlangt. Der Baum hat fünf verfasste Kanten. Drei besitzen gemeinsame Absatzbelege, zwei keine. [TREE_EDGES.tsv](TREE_EDGES.tsv) bindet jede an sämtliche konkrete Kinderstellen und verfügbare Elternstellen; Mitvorkommen ist ausdrücklich kein Relationsbeweis.

[ALL_LABEL_GROUPS.tsv](ALL_LABEL_GROUPS.tsv) enthält jede f88r-Beschriftungsgruppe. Keine entspricht einem der neun Wörter. Das ist fehlende exakte Anschlusskapazität, keine Widerlegung der Klassenhypothese. Keine Nachbarschaft, Formähnlichkeit oder fremde Labelgruppe wurde als Ersatz herangezogen. Die osal/oral- und otor am/otoram-Alternativen bleiben offen; keine Transkriptionsänderung.

## Entscheidung
Die strenge homogene Definition D zurückstellen. **L als konkrete partielle Darstellungsform weiterführen**, insbesondere die zwei Fraktionsposten. Sie trägt geringere Bindungskosten, löst aber die f21r-Folge nicht. Keine bestätigte Zutat, Klasse, Pflanzenart oder Zahl. Eine zusammengesetzte Definition könnte dieselben Teile enthalten und bleibt gegenüber L unentschieden. Die feine/grobe Benennung ist nicht richtungsidentifiziert. Keine Eindeutigkeit aus dem konfliktärmeren Renderer ableiten.

Quellen: P11s bereits abgegrenzter HERB4-Input und GDT811s zuvor veröffentlichter f88r-Abschnitt, Hashbindungen in INPUT.json. GDT768/809/888/913 primär geprüft; die älteren Glyphen- und Namensmodelle bleiben unverändert. [DECISION.md](DECISION.md) wurde nach deklarierter Projektexposition, vor Berechnung geschrieben. Keine Reserveseite oder neue Abbildung, keine Kontakte; f84/f84r geschlossen. Unabhängige Bedeutungsbestätigungskapazität null, keine Signifikanzbehauptung oder scorefähige Bild-Text-Relation.

Reproduktion: `python3 research_registry/proposals/translation_programs_20260912/work/P25/build.py`, dann `python3 research_registry/proposals/translation_programs_20260912/work/P25/validate.py`. Der Rücklesevalidator prüft Quellhashes, alle Gruppen, sämtliche Konfliktendpunkte und Wertadjazenzen sowie alle Beschriftungsgruppen; keine Bedeutungswahrheit.

Nächster Kandidat zur Auswahlprüfung: P18. Gleiche Wortannahmen bei verschiedenen vollständigen Satzgliederungen können zeigen, ob eine geschriebene Grenze die verbleibenden Bindungskonflikte erklärt. Keine nachträgliche Einzelstellengrenze in P25 einfügen.
