# GDT751 — q/Basis ist eine echte Formpaarung, aber kein besonderer Einstiegscode

## Ergebnis

Der saubere aktuelle Ganzformbestand enthält 690 Oberflächen. Genau 51 bilden
ein vollständiges Paar `qX`/`X`; zusammen besitzen sie 2.060 reader-exakte
q-Vorkommen und 1.701 reader-exakte Basisvorkommen. Die geerbten Rendererwerte
zeigen ein außerordentlich klares Muster:

- 47/51 Paare bewahren exakt dieselben HOT/COLD/DRY/MOIST-/Stufenachsen;
- 41/51 tragen `PREPARATION` nur auf der unpräfigierten Form;
- null Paare tragen `PREPARATION` nur auf der q-Form.

Das sieht zunächst wie die gesuchte Kompositionsregel aus. Es ist aber noch
kein unabhängiger Fund: Die aktuellen Karten stammen teilweise aus älteren
o-/q-Schalenmodellen. Der Kontrollbestand macht diese interne Konstruktion
sichtbar. Unter 160 anderen Ein-Zeichen-Präfixpaaren steht `PREPARATION` nur
einmal auf der Basis, aber 50-mal nur auf der Präfixform—fast vollständig bei
o-Präfixen. Die q/o-Asymmetrie ist daher ein starkes **internes
Renderermodell**, noch keine entzifferte Eigenschaft eines Voynich-Zeichens.

## Der rohe Positionstest korrigiert die starke Lesart

| Gruppe | Paare | mittlere Positionsdifferenz Präfix−Basis | früher : später | Zeilenanfangsdelta | Zeilenenddelta |
|---|---:|---:|---:|---:|---:|
| q/Basis | 51 | −0,0665 | 33:18 | +0,0074 | −0,0527 |
| gematchte Nicht-q-Kontrollen | 51 | −0,0615 | 32:18 (+1 Gleichstand) | +0,1575 | −0,0042 |
| alle Nicht-q-Kontrollen | 160 | −0,0807 | 102:57 (+1) | +0,2040 | +0,0033 |
| Nicht-q mit o-Basis | 14 | −0,1674 | 11:3 | +0,3209 | −0,0644 |

Die q-Formen liegen tatsächlich früher als ihre Basen. Derselbe Effekt ist bei
anderen vorangestellten Zeichen aber gleich groß oder stärker. Nach Entfernung
der Abschnittsmittel bleibt praktisch dasselbe Bild (q −0,0662; alle
Nicht-q −0,0803). Damit fällt die Behauptung **q sei aufgrund seiner Position
ein besonderer Eintrags- oder Feldanfangsmarker**. Das Ergebnis sagt nicht,
dass q bedeutungslos ist; es sagt, dass der bisherige Positionsbeleg keine
q-spezifische Erklärung trägt.

## Die vollständigen Paare gehören trotzdem zusammen

Zwölf verschiedene q/Basis-Paartypen stehen 44-mal unmittelbar und in beiden
Reihenfolgen nebeneinander: 24-mal q vor Basis, 20-mal Basis vor q, auf 27
Seiten. Auf 1.000 Vorkommen der jeweils selteneren Paarseite ergeben sich 35,31
direkte Kontakte. Alle 160 Nicht-q-Kontrollen erreichen 20,35, die gematchten
Kontrollen 14,00. Das ist eine schwache, aber reale Anreicherung um Faktor
1,74 gegenüber dem gesamten Kontrollbestand.

Der richtige Arbeitsstand lautet deshalb:

**`qX` und `X` sind eine produktive vollständige Formpaarung. Qualität und
Stufe dürfen innerhalb der starken Paare vorläufig erhalten bleiben. Der
Trägerwechsel `qX = ungebundenes Feld`, `X = Zubereitung` bleibt eine
modellinterne Arbeitshypothese; er ist nicht die Bedeutung des Zeichens q.**

Das ist enger und brauchbarer als sowohl „q ist bedeutungslos“ als auch „q
bedeutet Nicht-Zubereitung“. Es sagt etwas über die Relation zweier ganzer
beobachteter Wörter, ohne einen EVA-Buchstaben in ein mittelalterliches Kürzel
umzudeuten.

## Zehn konkretere `okeey`-Stellen

Die Kreuzung mit GDT750 liefert zehn Stellen, an denen alle nötigen Bedingungen
gleichzeitig vorliegen: `okeey` besitzt bereits eine lokale HOT+END-Karte,
`qokeey` ist der unmittelbare aktive Host, beide Ganzformen bewahren dieselben
Qualitäts-/Stufenachsen, und die geerbte Paarung setzt den
Zubereitungsträger nur auf `okeey`. Für diese zehn Stellen lautet die neue
explorative Arbeitslesung:

**`okeey` — heiße Zubereitung an der End-/Vollstufe.**

Beispiele:

```text
f103v.4  y cheey qokeey [okeey] lkees ol qoteedy ykeedy
          … qokeey; heiße Zubereitung an der End-/Vollstufe; …

f3r.14   chor qodair [okeey] qokeey
          … heiße Zubereitung an der End-/Vollstufe; qokeey

f81v.11  yshey qokeey [okeey] oky ykeey qoky oky lky olchy ky dsholyd
          … qokeey; heiße Zubereitung an der End-/Vollstufe; …
```

Diese zehn Karten liegen auf sieben Seiten und sind absichtlich
vorkommensgebunden. Die drei weiteren direkten `qokeey/okeey`-Kontakte ohne
GDT750-Lizenz bleiben unverändert; ebenso die vier `okeey`-Karten, deren Host
`ykeey`, `okey` oder `oteey` ist. So wird der Träger nicht rückwirkend auf jedes
gleich geschriebene Wort globalisiert.

## Konsequenz

Wir besitzen jetzt erstmals eine konkrete, vorhersagende Ganzformrelation mit
klarer Schwächemarkierung: q/Basis bewahrt meistens den Zustand, und an lokal
gebundenen Basisstellen kann der Zubereitungsträger ergänzt werden. Was noch
fehlt, ist unabhängige Satzrollen-Evidenz für die Richtung dieses
Trägerwechsels. Der nächste sinnvolle Pass nimmt deshalb die 44 direkten
Kontakte und prüft ihre vollständigen Mikrofelder gegen die bereits vorhandenen
deskriptiven und präskriptiven historischen Kanäle. Wenn die Basisformen dort
nicht wiederholt den Zubereitungs-/Objektslot besetzen, muss der Trägerwechsel
wieder fallen.

Der Validator prüft alle Paar-, Vorkommens-, Matching-, Kontakt- und
Carrierkoordinaten sowie byte-identische Neuberechnung. Der GDT388-Einlass
enthält alle 44 Relationen und bleibt ausschließlich wegen unversiegelten
formalen Zugriffs invalid und nicht score-ready. Null q-/Komponentenwerte, null
Lexeme, null neue Seiten und keine Literalidentität werden exportiert.
