# GDT401 — Die vier gelben Fälle sind drei Übergänge

## Ergebnis

GDT400 zählte vier gelbe Fokusanschlüsse. Sichtbar sind es nur **drei
Kartenübergänge**: je einer auf f75r und f81v sowie ein f82r-Paket, in dem `EE`
und `Y` aus derselben Karte zum selben Ziel laufen.

Alle drei Übergänge benutzen dieselbe alte Maschine:

1. Ein kopfloses Paket darf genau eine Karte weit vorwärtslaufen.
2. Der erste sichtbare Handlungskopf der Zielkarte nimmt das Paket.
3. Steht dort `R` in Kopfposition, gilt die bereits gelehrte R-Kopf-Lizenz.
4. Innere Argumente der Zielkarte werden danach separat gebunden.

Das ist **keine zehnte Scope-Familie**. `R_POSITIONAL_HEAD` entscheidet, dass
`R` ein Kopf ist; `ONE_CARD_FORWARD` beziehungsweise
`Q_OT_PACKAGE_FORWARD` entscheidet die Distanz. GDT400 hatte beide Achsen in
einer Signatur verkettet und dadurch die Kombination künstlich gelb gemacht.

## Der ehrliche Rest

Der f82r-Übergang `OT+EE+Y | R+AIIN` ist strukturell grün, aber semantisch nur
als Paket zu lesen: „den nächsten Posten der zweiten Stufe mit dem angegebenen
Wert markieren“. `EE` darf daraus **nicht** zu „länger markieren“ oder
„stärker markieren“ werden. Genau diese enge Kopf-Grad-Lesart besitzt noch
keinen unabhängigen Parallelfall.

## Tragweite

- 4/4 alte Warnanschlüsse erhalten einen vorhandenen Scope-Elternweg.
- 4 Warnanschlüsse entsprechen 3 Kartenübergängen.
- 127 Vorgriffe zeigen neun verschiedene sichtbare Zielköpfe.
- 60 `R_POSITIONAL_HEAD`-Anschlüsse benutzen fünf verschiedene Scope-Lagen
  und stehen in allen vier laufenden Registern.
- Der spezielle Vorgriff auf `R` hat fünf Fokusereignisse; die vier GDT400-
  Warnungen sind daher keine isolierte Schreibpanne.

Für neue Seiten ist `focus | R+...` nun grün, wenn `R` der erste sichtbare Kopf
der unmittelbar nächsten Karte ist und keine Besitzer-/Aussagegrenze dazwischen
liegt. Ein freier Grad- oder Bedeutungsimport bleibt gelb.
