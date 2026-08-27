# GDT573 — die Argumente sprechen jetzt mit kurzen Rückbezügen

Status:
`PASS_22_ANAPHOR_CARDS__854_REPEAT_GROUPS__1046_LATER_ARGUMENT_MENTIONS_COVERED_BY_1043_ANAPHORS__841_CLAUSES__5122_EXACT_ROUNDTRIPS__ZERO_ROOT_CHANGE`

## Ergebnis

In 841 der 5.122 Karten wurde dieselbe bereits ausgeschriebene Argumentform
innerhalb derselben Karte zwei- bis fünfmal wiederholt. Das sind 854 getrennte
Wiederholungsgruppen und 1.046 Vollnennungen nach der jeweils ersten Nennung.
GDT573 lässt die erste Form stehen und spricht die späteren Formen als kurze
deutsche Rückbezüge aus:

```text
alt: Entnimm den laufenden Eintrag und wähle den laufenden Eintrag.
neu: Entnimm den laufenden Eintrag und wähle ihn.

alt: Ordne dieselbe Eintragseinheit zu und wähle dieselbe Eintragseinheit.
neu: Ordne dieselbe Eintragseinheit zu und wähle sie.

alt: Entnimm denselben laufenden Eintrag, lege denselben laufenden Eintrag
     fest, kennzeichne denselben laufenden Eintrag und wähle denselben
     laufenden Eintrag.
neu: Entnimm denselben laufenden Eintrag, lege ihn fest, kennzeichne ihn und
     wähle ihn.
```

Die zwanzig bekannten Register×Argument-Zellen reichen dafür vollständig aus.
Jede ist im Bestand tatsächlich benutzt. `ihn` erscheint 949-mal, `sie` 91-mal.

## Zwei kleine, aber wichtige Grenzfälle

Die schon in GDT565 lizenzierte Doppel-Y-Form wird als wirklicher Plural
behandelt:

```text
alt: Weiter: nimm die beiden Positionsposten auf und ordne die beiden
     Positionsposten zu und nimm die beiden Positionsposten auf und ordne die
     beiden Positionsposten zu.
neu: Weiter: nimm die beiden Positionsposten auf und ordne sie zu und nimm sie
     auf und ordne sie zu.
```

Eine echte Wortgrenze ist hier zwingend: `den Positionsposten` darf nicht im
Wort `beiden` beginnen. Der bereinigte Matcher trennt diese Fälle korrekt.

In drei Kräuterkarten kehren dagegen zwei verschiedene maskuline Argumente
gemeinsam wieder. `ihn und ihn` wäre zwar mechanisch rückführbar, aber als
deutscher Text unbrauchbar. Die kleine Koordinationskarte sagt deshalb `beide`:

```text
alt: Nimm den Pflanzenposten und den Arbeitswert und stelle den Pflanzenposten
     und den Arbeitswert ein.
neu: Nimm den Pflanzenposten und den Arbeitswert und stelle beide ein.
```

Damit decken 1.043 ausgesprochene Anaphern alle 1.046 späteren Vollnennungen ab.

## Was sichtbar bleibt

Außen, innen und Stufe drei werden nicht eingeebnet. Auch eine Stufenform kann
lokal pronominal werden, ihr Scope bleibt aber hörbar:

```text
... den Pflanzenposten auf Stufe drei ... ihn auf Stufe drei.
```

Jede Anapher besitzt einen vollständigen Rückkanal mit Originalfragment,
Argumentwurzel, Formklasse und Quell-/Zielspanne. Daraus entstehen alle 5.122
GDT572-Klauseln bytegenau erneut. Ereignisfolge, 793 Statementgrenzen und 30
Seiten bleiben unverändert; 162 Zustands- und 679 Nichtzustandskarten erhalten
nur diese neue Werkstattstimme. Alle 54 unabhängigen Prüfungen bestehen.

## Bedeutung für die Arbeitstheorie

Die lange deutsche Wiederholung war kein Hinweis auf lange Voynich-Wörter. Sie
war ein Artefakt unseres vollständig expliziten Renderers. Die aktuelle
Lesesprache benötigt dafür nur:

```text
20 bekannte ownergebundene Argumentformen
+ ihn/sie nach der ersten lokalen Nennung
+ eine Pluralform für das alte Y|Y
+ beide für drei gleichgeschlechtliche Zweierkoordinaten
```

Das ändert keine der neunzehn Arbeitswurzeln und bestätigt weiterhin keine
historische Übersetzung. Es macht die bestehende vollständige Arbeitstheorie
jedoch kürzer und besser lesbar.

## Nächster Arbeitsweg

Der größte verbliebene Prosarest liegt nun in doppelten Handlungen und
wiederholten Relations-/Modifikatorphrasen, etwa `an der bezeichneten Stelle
und an der bezeichneten Stelle`. Als Nächstes wird dieser Rest vollständig
inventarisiert. Nur Formen mit einer kleinen reversiblen Zähl- oder
Koordinationsregel werden verdichtet; keine neue Seite und keine neue
Wurzelbedeutung wird dafür geöffnet.
