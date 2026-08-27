# GDT580 — Wiederaufnahme statt falscher Aktionszählung

## Ergebnis

`PASS_3_RAW_ADJACENT_RELATION_PAIRS__1_MODIFIER_RESUMPTION_OPERATOR__3_EXPLICIT_FORMS__6_WRITTEN_SLOTS__3_EVENT_CARDS__5122_EXACT_ROUNDTRIPS`.

Die drei letzten roh benachbarten Relations-/Modifierpaare besitzen jetzt eine
gemeinsame kompositionelle Stimme. Sie bedeutet nicht „führe die sichtbare
Handlung zweimal aus“, sondern „verwende denselben Eintrag unmittelbar noch
einmal“:

| Ereignis | Rohpaar | Arbeitsstimme |
|---|---|---|
| G407-E0152 | O+O | `als Ausführung; dieselbe Ausführungsangabe nochmals` |
| G407-E1846 | D_ADDR+D_ADDR | `an der D-Stelle; dieselbe Stellenangabe nochmals` |
| G515-E0379 | AL+AL | `beim vorangehenden Festlegen: zur Zielspalte; dieselbe Zielangabe nochmals` |

Das Wörterbuch wächst dabei nicht um drei Ganzwörter für OO, DD und ALAL. Eine
einzige Wiederaufnahmeregel nimmt die bereits vorhandene Basisbedeutung und
benennt deren Klasse als Ausführungs-, Stellen- oder Zielangabe. Das ist
absichtlich expliziter als die erste Fassung mit `ebenso/dort/dorthin`: Der
abschließende Proseaudit zeigte, dass jene Wörter noch wie eine Wiederholung der
Handlung klingen konnten. Jeder erste Slot besitzt weiterhin den vollständigen
Basisspan; jeder zweite Slot einen eigenen Angabe-Span und eine Expansion zurück
zur zweiten Vollphrase.

## Warum nicht einfach „zweimal“?

`zweimal an der D-Stelle` wäre verständlich. `zweimal als Ausführung` ist
bereits hölzern, und `halte ... zweimal zur Zielspalte` würde im dritten Fall
sogar die falsche Handlung hörbar machen. Das geschriebene Paar ist AL+AL, nicht
SH+SH.

Der feste GDT515-Anschluss entscheidet den schwierigen Fall. Beide AL-Slots in
G515-E0379 sind `FREE_PEER_1/2`, stehen vor SH und zeigen auf die vorherige
T/Festlegen-Handlung G515-E0378. Die neue Zeile bewahrt das:

```text
Beim vorangehenden Festlegen: zur Zielspalte;
dieselbe Zielangabe nochmals.
Halte denselben laufenden Eintrag fest;
auf Grad I;
schließe den Schritt.
```

Damit bleibt die Zielangabe nicht nur vor der sichtbaren SH-Handlung: Ihr
vorheriger T/Festlegen-Kopf wird auch hörbar benannt. Die ältere
Außen/Innen-Kontrollstimme für diesen Fall wird nicht wiederbelebt: GDT515
klassifiziert beide Slots als PLAIN peers, und GDT575 führt sie ausdrücklich
außerhalb der siebzehn Scopepaare.

## Historischer Hausverstand

Die Wahl einer kurzen Wiederaufnahme hat eine brauchbare Werkstattparallele,
ohne als Entzifferungsbeleg missverstanden zu werden. Das Kochbuch Meister
Eberhards aus dem 15. Jahrhundert verweist bei wiederverwendeten Ölverfahren
mehrfach knapp auf eine frühere Anweisung—etwa `als hie vor geschriben stett`
und `wie vor gesagt ist`—statt den ganzen Ablauf erneut auszuschreiben
([Universität Gießen, R107–R113](https://www.uni-giessen.de/de/fbz/fb05/germanistik/absprache/sprachverwendung/gloning/tx/feyl.htm)).
Unser normalisiertes `nochmals ...` übernimmt nur dieses praktische Prinzip;
es behauptet weder dieselben Wörter noch dieselbe Textgattung.

## Vollständige Ausgabe

Gegenüber GDT579 ändern sich genau drei Ereignisse, drei Aussagen und drei
Seiten: ein Nichtzustands- und zwei Zustandsereignisse. Alle 5.119 übrigen
Ereignisse bleiben bytegleich. Die Aussagen werden aus ihren festen Event-IDs
neu gebaut, und alle 5.122 Ereignisse sowie 793 Aussagen besitzen einen exakten
GDT579-Rückweg. Die 43 vorhandenen `zweimal`-Lesungen bleiben unverändert;
drei neue Wiederaufnahmen erhöhen `nochmals` von eins auf vier. Alle 57
unabhängigen Prüfungen bestehen.

Kumulativ gegen GDT574 umfasst die Arbeitsstimme nun 764 geänderte Ereignisse,
309 Aussagen und 28 Seiten. Nur ein Ereignis kommt zum kumulativen Rest hinzu,
weil die beiden anderen Zielereignisse seit GDT576 bereits eine differenzierte
Siglenstimme tragen; ihre Aussagen und Seiten waren ebenfalls schon verändert.

## Bedeutung für die Arbeitstheorie

Die Wiederholung zweier identischer Stämme muss nicht als neues Ganzwort und
nicht automatisch als Zahlenoperator gelesen werden. Für O+O, D_ADDR+D_ADDR
und AL+AL genügt dieselbe lokale Komposition:

```text
X + X  →  X, unmittelbare Wiederaufnahme von X
```

Entscheidend bleibt der Kopfanschluss. Derselbe Operator darf eine Basis
wiederaufnehmen, aber keinen Besitzer erfinden. Mit diesem Pass sind alle drei
roh benachbarten identischen Relationspaare gesprochen; die 62 unterbrochenen
Wiederholungen, alle Außen/Innen-Paare und G407-E1755 bleiben in ihren bereits
ausgearbeiteten Stimmen unangetastet.
