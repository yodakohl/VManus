# Pass 1011 — manuelle optische Passageprüfung

## Ziel

Pass 1011 prüft die laufende Werkstattübersetzung nicht mit einem neuen
Zählmodell, sondern mit zwei absichtlich verschiedenen Augenpaaren. Ein
norditalienischer Kräuter- und Apothekenschreiber um 1420 las vierzehn
Passagen auf sieben Kräuterseiten. Ein Badehausmeister und technischer
Zeichner derselben Zeit las einundzwanzig andere Passagen auf fünf
Biological-Seiten. Beide betrachteten die jeweils erlaubten Yale-Bilder
einzeln in Originaldetail. Ihre Seitensätze überschneiden sich nicht.

Der Test ist einfach: Passt der übersetzte Arbeitsgang zum gezeichneten
Gegenstand, oder erfindet er Gefäß, Richtung, Wärme, Filter, Produkt oder eine
Verbindung, die dort nicht vorhanden ist?

## Ergebnis

Die 35 manuell gelesenen Passagen verteilen sich so:

- 4 `STRONG_FIT`;
- 15 `PLAUSIBLE`;
- 14 `STRAINED`;
- 2 `IMAGE_CONTRADICTION`.

Alle 35 erhalten eine knappere Bildfassung. Die übrigen 592 Aussagen werden
unverändert aus Pass 1010 übernommen. Damit liegt wieder eine vollständige
627-Aussagen-Ausgabe vor; es wird keine ungeprüfte Passage stillschweigend als
optisch bestätigt markiert.

## Was gut funktioniert

Das Grundgerüst überlebt und wird sogar anschaulicher:

> sichtbarer Besitzer oder sichtbare Station → Teil/Posten wählen → Menge oder
> Grad einstellen → lokal bearbeiten/halten/weitergeben → offenlassen oder
> schließen

Auf den Kräuterseiten tragen die Bilder vor allem **Pflanzenbesitz und
Pflanzenteile**. Besonders gut sitzen die Wurzelkrone und runden Kronenstücke
auf f13r, die drei großen Materialzonen Wurzel–Blattmasse–Doldenkopf auf f55v
und die unterschiedlichen Kopfzustände auf f56r.

Auf den Biological-Seiten tragen die Bilder **lokale Becken-, Kontakt-,
Behälter- und Anschlussvarianten**. Der beste einzelne Treffer ist
`P1009-S419` auf f81v: Ein gebogener Randweg berührt tatsächlich das große
gemeinsame Badfeld. Durchgeben, aufnehmen/halten, absetzen und schließen passt
hier als lokaler Arbeitsgang; nur Einlass gegen Auslass bleibt offen.

## Was wir zu weit ausgebaut hatten

Die Kräuterübersetzung hatte stille Pflanzenbilder wiederholt zu vollständigen
Apparategeschichten aufgeblasen. f11r zeigt keinen Sud, kein Auswringen, keine
Stehzeit, kein Sieb, keinen Klarlauf und keine Kühlstelle. f17r und f18r zeigen
keine Rohre, Quellen, Durchlässe oder Ziele. Solche Inhalte können in einem
Kräutertext stehen, werden aber vom Bild nicht geliefert. Die bessere Fassung
nennt dort Teil, Maß, Folgegang, Bearbeitung und Weitergabe.

Die Biological-Übersetzung hatte einen echten Anschluss häufig sofort als
gerichteten Transport gelesen. Das ist zu viel: Ein Strich belegt zunächst
nur Kontakt oder Verbindung. Pfeile fehlen fast überall. Ebenso sind Wärme,
Filtertuch, Klarheit und Gebrauchsbereitschaft nicht automatisch sichtbare
Eigenschaften der gezeichneten Station.

## Zwei direkte Bildwidersprüche

`P1009-S400` beschrieb f81v als Folge mehrerer Becken. Das Bild zeigt aber ein
einziges gemeinsam umrandetes zweireihiges Badfeld. Die reparierte Lesung
lautet:

> Im gemeinsamen zweireihigen Badfeld den Posten innerhalb derselben Anlage
> länger halten, an einer weiteren Position fortsetzen und schließlich
> absetzen; den Teilgang schließen.

`P1009-S498` verband auf f82r ein vorheriges Becken mit einer nächsten Station.
Der untere grüne Mehrfigurenpool ist jedoch eine eigene Bildgruppe und besitzt
keine sichtbare Leitung zum mittleren horizontalen Apparat. Die reparierte
Lesung lautet:

> Im unteren gemeinsamen Becken eine Portion aufnehmen, nach Maß halten oder
> absetzen, den Gang markieren und offenlassen.

## Neue gemeinsame Schreibregel

Für die nächste Werkstattfassung gelten acht kurze Regeln:

1. Das Bild liefert zuerst den Besitzer, nicht den vollständigen Satz.
2. Sichtbare Pflanzenorgane dürfen als auswählbare Teile dienen; genaue Arten
   oder Produkte nicht.
3. Ein Anschluss bedeutet Verbindung, nicht automatisch Richtung.
4. Eine gemeinsame Umrandung bleibt ein gemeinsames Becken, auch wenn mehrere
   Figuren darin stehen.
5. Eine getrennte Bildgruppe setzt den lokalen Besitzer zurück; Nähe allein
   baut keine Pipeline.
6. Grad, Menge und Abschluss dürfen aus dem Text kommen, auch wenn sie nicht
   gezeichnet sind.
7. Wärme, Filter, Klarheit, Quelle, Ziel und Produktname werden nur bildlich
   behauptet, wenn ein sichtbares Merkmal sie trägt.
8. Unsichtbare, aber textlich mögliche Vorgänge werden neutral als
   Bearbeitung, Halten, Weitergabe oder Folgegang formuliert.

## Beste gegenwärtige Gesamtlesung

Die stärkste Arbeitsfassung ist nun einfacher als vor der Bildprüfung. Die
Kräuterseiten sind illustrierte Materialartikel. Die Biological-Seiten sind
Kataloge lokaler Bade-, Kontakt-, Behälter- und Anschlussvarianten, nicht ein
einziges Wasserwerk. Der Text steuert Posten, Menge, Grad, Wiederholung und
Abschluss; die Zeichnung liefert den konkreten Besitzer und manchmal eine
wirkliche lokale Verbindung.

Das passt zu einer kleinen Werkstatt mit mehreren Schreibern: Sie lernen eine
kompakte Prozessnotation und benutzen die vorgezeichnete Seite als stillen
Sachträger. Sie müssen weder für jede Pflanzenzeile ein unsichtbares Labor noch
für jede Biological-Seite ein verborgenes Rohrnetz memorieren.

## Artefakte

- `HERBAL_APOTHECARY_OPTICAL_AUDIT.tsv`: 14 einzelne Kräuterprüfungen;
- `BATHHOUSE_DRAUGHTSMAN_OPTICAL_AUDIT.tsv`: 21 einzelne technische
  Prüfungen;
- `PASS1011_COMBINED_OPTICAL_AUDIT.tsv`: gemeinsame normalisierte Prüftabelle;
- `PASS1011_627_OPTICALLY_REPAIRED_STATEMENTS.tsv`: vollständige Ausgabe;
- `PASS1011_PAGE_SUMMARY.tsv`: kompakte Seitenbilanz;
- `build_pass1011.py` und `validate_pass1011.py`: reproduzierbarer Zusammenbau
  und Konsistenzprüfung.

Dies bleibt eine kreative Arbeitsübersetzung. Der optische Check sagt, welche
Formulierungen zur Zeichnung passen; er beweist keine einzelne
Voynich-Wortbedeutung.
