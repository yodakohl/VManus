# GDT566 — erstmals eine vollständige aktuelle 30-Seiten-Arbeitsausgabe

Status:
`PASS_COMPLETE_5122_EVENT__793_STATEMENT__30_PAGE_WORKING_EDITION__1656_GENERATED_STATE__3466_OWNER_CONTEXT_NONSTATE__ZERO_REST`

## Ergebnis

Die bisher getrennten Übersetzungsstände sind jetzt in einer einzigen Ausgabe
zusammengeführt:

```text
1.656 Zustandskarten  → GDT565-Generator
3.082 alte Nichtzustandskarten → GDT416-Kontext
  384 neue Nichtzustandskarten → GDT539-Kontext
──────────────────────────────────────────────
5.122 Karten / 793 Aussagen / 30 Seiten
```

Es bleibt keine laufende Karte und keine Aussage ohne Arbeitslesung. Die 30
Seiten enthalten 28 Seiten mit laufender Prosa; `f69v` und `f70v` bleiben als
die beiden bereits zugelassenen Seiten ohne laufende Ereignisse sichtbar.

## Was sich tatsächlich geändert hat

Für die 1.656 Zustandskarten wird nun die kleine, ownerfreie GDT565-Zeile
verwendet. Für alle 3.466 übrigen Karten wird nichts neu formuliert: Ihre
GDT416/GDT539-Klausel wird bytegleich übernommen. Deshalb besitzt jede Karte
zwei explizite Kanäle:

- die ausgewählte aktuelle Arbeitslesung;
- die vollständige ownergebundene Kontrolllesung.

Bei allen Nichtzustandskarten sind beide Kanäle gleich. Bei allen Zustandskarten
sind sie verschieden. So kann die flüssigere Ausgabe benutzt werden, ohne die
ältere Kontextinformation zu verlieren.

## Aussagen statt isolierter Wörter

Die Karten bilden 793 Aussagen:

```text
247 vollständig aus Zustandskarten       280 Karten
528 gemischte Aussagen                  4.768 Karten
 18 Aussagen ohne Zustandskarte            74 Karten
──────────────────────────────────────────────────
793 Aussagen                            5.122 Karten
```

775 Aussagen enthalten mindestens eine generierte Zustandszeile. Parallel
rekonstruiert der Kontrollkanal 715/715 alte und 78/78 neue Quellaussagen
bytegleich. Damit ist die Ausgabe nicht bloß eine Konkordanz einzelner
Mikrophrasen, sondern ein lückenloses lesbares Arbeitsbuch.

## Zehn offen sichtbare Reparaturen

Zwischen GDT515s Navigationssnapshot und den späteren Kontextausgaben änderten
sich genau zehn Rezeptlesungen. Zwei davon sind Zustandskarten, acht
Nichtzustandskarten. GDT566 versteckt diese Stellen nicht: Beide Rezepte und die
endgültig verwendete Leseschicht stehen in einem eigenen Zehn-Karten-Deck.

Die einzige redaktionelle Glättung aus GDT565 bleibt ebenfalls benannt:
`G407-E1000` sagt jetzt „die beiden Posten“ statt „den Posten und den Posten“.
Sie ändert keine Wurzel und kein Rezept.

## Was wir dadurch gewonnen haben

Vor GDT566 lagen die aktuellen Bedeutungen in mehreren Generationen und
Teilausgaben. Jetzt existiert ein einzelner, vollständig durchsuchbarer Text,
an dem wir Satzanschlüsse und wiederkehrende Arbeitsabläufe untersuchen können.
Der nächste sinnvolle Pass ist daher kein weiteres Wörterbuchraten, sondern ein
gezieltes Anschluss-Audit: Wo stoßen generierte Zustandszeilen und
ownergebundene Nichtzustandszeilen innerhalb derselben Aussage hart oder
widersprüchlich aufeinander? Solche Stellen können dann mit kleinen
Satzbrücken geglättet werden, ohne eine Bedeutung umzudeuten.

## Grenze

„Vollständig“ bedeutet vollständig innerhalb der aktuellen 30-Seiten-
Arbeitsbasis. Es bedeutet nicht, dass das Voynich-Manuskript historisch
entziffert wäre. Keine neue Seite, Form, Wurzel oder Bedeutung wurde ergänzt.
Alle 45 unabhängigen Prüfungen bestehen.
