# GDT582 — Vollständiger konkreter Stem-Default-Pass

## Ergebnis

`PASS_15889_COMPLETE_DEFAULTS__13593_PRODUCTIVE_FUNCTION_SLOTS__109_LEARNED_CONTENT_SLOTS__42_CORE_STEMS__181_REGISTER_CELLS__80_CLASS_NAME_TYPES__4026_ALIAS_DEFAULTS__5122_EVENTS__793_STATEMENTS__744_LOCAL_CARDS__25_EVENT_SENSE_CHECKS__20_COMPLETE_PASSAGE_CHECKS__ZERO_EMPTY_DEFAULTS`

Die Grammatikpolitur trägt: Alle 15.889 geschriebenen Slots der dreißig
zugelassenen Seiten besitzen jetzt einen expliziten Arbeitsdefault. Kein Wort,
Namenskern, lokales Zeichen und keine Steuerkarte bleibt leer. Zugleich mussten
wir nicht tausende Oberflächen einzeln auswendig lernen:

| Schicht | Occurrences | Karten/Typen |
|---|---:|---:|
| produktive GDT581-`slot_value`-Klassen | 13.593 | 42 Analyseklassen |
| beobachtete Registerausformulierungen | dieselben 13.593 | 181 Zellen |
| gelernte Namensoccurrences | 107 | 80 Klasse×Kern-Typen |
| ownergebundene `LOCAL_X`-Inhalte | 2 | 2 Karten |
| reine Steuerung | 2.187 | strukturelle Defaults |
| geerbte, nicht geschriebene Werte | 4.026 | Aliasauflösungen |

99,20 % der 13.702 Inhalts-Slots benutzen damit ein produktives
Arbeitswörterbuch. Nur 0,80 % bleiben gelernt. Das ist der bislang beste
konkrete Kompromiss zwischen Durchsatz und Wiederverwendung: Eine bereits
segmentierte neue Occurrence bekannter `slot_value×register`-Klassen kann
gelesen werden, ohne dass jeder Pflanzen-, Stern- oder Drogenname gewaltsam
zerlegt wird. Eine neue Oberfläche oder Seite wird damit noch nicht geparst oder
vorhergesagt.

## Die neue Arbeitsformel

```text
kurzer Stammkern
+ registerabhängige Fachrealisierung
+ exakter GDT581-Host
+ gelernter Owner-/Namenskern, wenn ein Einzelobjekt benannt wird
```

Ein Beispiel ist `AIIN`. Global ist es nur `Maß oder Kennwert`; im Herbal-
Register wird es `Pflanzenauszug oder Arbeitsmaß`, am Ring `Positionswert`, im
Bad `Stations- oder Badmaß` und im Pharma-Register `Dosis- oder Mengenmaß`.
Damit kann eine lokale Wasser- oder Weinlesung bestehen, ohne dass eine
Sternpassage Wasser auswählen, halten oder markieren muss.

Dasselbe gilt für Handlungen. `CHD` bleibt kurz `bearbeiten/behandeln`; bei
Pflanzen oder Drogen darf es zerreiben heißen, am Ring berechnen und im Bad
behandeln. `T` bleibt `einstellen/temperieren`; erwärmen, kühlen oder trocknen
sind zusammengesetzte physische Unterlesungen, keine universelle Gleichung.

## Kompaktes Kernwörterbuch

Die vollständige 42er-Tabelle steht in
`artifacts/gdt582_42_core_stem_defaults.tsv`. Die häufigen tragenden Kerne sind:

Die 42 Einträge sind GDT581-Analyseklassen. `D_ADDR`, `CARRIER_Q`,
`LOCAL_CHAR_F` und ähnliche Einträge sind keine direkt beobachteten
Manuskriptwörter und nicht als sprachliche Wortstämme bestätigt.

| Stamm | Slots | kurzer Kern | typische konkrete Realisierung |
|---|---:|---|---|
| `Y` | 2.125 | laufendes Gut/Charge | Pflanzencharge, Ringposition, Stationsansatz, Drogencharge |
| `CH` | 1.023 | entnehmen | ausziehen, ablassen, ablesen |
| `O` | 973 | Form/Modus | Zubereitungs-, Eintrags-, Anwendungs- oder Arzneiform |
| `OK` | 961 | ansetzen/öffnen | Pflanzenansatz ansetzen, Station beschicken, Position eintragen |
| `SH` | 794 | halten/ruhen | ziehen lassen, baden, festhalten |
| `K` | 616 | zugeben/übertragen | Zutat zugeben, Station zuführen, Position zuordnen |
| `AIIN` | 535 | Maß/Kennwert | Auszug, Positionswert, Badmaß, Dosis |
| `AL` | 542 | Ziel | Zielgefäß, Zielposition, Zielstation |
| `AR` | 478 | Quelle | Ausgangsgefäß, Ausgangsposition, Ausgangsstation |
| `S` | 402 | auswählen/abtrennen | aussondern, Position wählen, umleiten |
| `T` | 384 | einstellen/temperieren | temperieren, regulieren, Position einstellen |
| `CHD` | 341 | bearbeiten/behandeln | zerreiben, behandeln, berechnen |
| `OR` | 332 | Einheit/Ansatz | Pflanzen-, Sektor-, Becken- oder Gefäßeinheit |
| `L` | 307 | Kontakt/Verbindung | Materialkontakt, Ringkontakt, Leitung, Gefäßkontakt |
| `AIN` | 262 | Teil/Portion | Pflanzenportion, Sektoranteil, Anwendungs- oder Zutatenanteil |
| `P` | 196 | einbringen/anwenden | einlegen, einsetzen, anwenden |
| `R` | 152 | kennzeichnen/prüfen | markieren, prüfen |
| `AIR` | 78 | Bahn/Weg | Verarbeitungsweg, Ringbahn, Kanal, Transferkanal |
| `E/EE/EEE` | 1.894 | Grad I/II/III | Intensitäts-, Ring-, Bad- oder Zubereitungsgrad |

Die restlichen 21 Kerne sind kurze Stufen-, Form-, Adress- und Klassenkarten:
`D_ADDR=Arbeitsstelle`, `IIN=Arbeitsstufe`, `CARRIER_Q=Neuansatz`,
`DA=zweiter Durchgang`, `LOCAL_CHAR_F=Feinform` sowie benannte Nebenstellen
und Varianten. Gerade `O`, `IIN`, `DA` und `D_ADDR` bleiben damit klein genug,
um bereits segmentierte Kompositionen wiederzuverwenden.

## Wo die gewünschten konkreten Bedeutungen jetzt liegen

Die Stoffe und Pflanzenorgane werden nicht mehr in einen häufigen universellen
Stamm gepresst. Sie sitzen in gelernten, ownergebundenen Karten:

| Begriff | konkrete Defaultkarte | Geltungsbereich |
|---|---|---|
| Wasser | `GDT582-N059`, Kern `d` | Drogen-/Zutatenname auf f88v/f89r |
| Wein | `GDT582-N061`, Kern `y` | Drogen-/Zutatenname auf f88v/f89r |
| Olivenöl | `GDT582-N056`, Kern `or` | Drogen-/Zutatenname auf f88v/f89r |
| Salz | `GDT582-N068`, Kern `s` | Drogen-/Zutatenname auf f89r |
| Wurzel | `GDT582-N076`, `dchos=Ingwerwurzel` | gelernter Zutatenname |
| Blatt | `GDT582-N079/N080`, Salbei-/Rautenblatt | gelernte Zutatennamen |
| Blüte | `GDT582-N074`, `opchor=Safranblüte` | gelernter Zutatenname |
| Samen | `GDT582-N075`, `opor=Pfefferkorn oder Samen` | gelernter Zutatenname |
| Krankheit/Beschwerde | `RUNNING:G515-E0410@2` | ownergebundener `LOCAL_X`-Inhalt |
| Heilmittel/Heilwirkung | `RUNNING:G515-E0438@2` | getrennter ownergebundener `LOCAL_X`-Inhalt |

`d`, `y`, `or`, `s` und die Pflanzenkerne sind dabei keine globalen
Voynich-Wortgleichungen. Derselbe rohe Kern kann in einer anderen
ownerbestimmten Namensklasse etwas anderes bezeichnen; beispielsweise wird `d`
in der Badstationsklasse als Ablauf gelesen. Genau diese Klasse×Kern-Trennung
ist die gesuchte Mischung aus Fachkürzel und gelerntem Ganzwort.

Auch typographisch ähnliche Werte bleiben in getrennten Namespaces: rohe
Namenskerne `dy/e/chd` sind nicht die produktiven Analyseklassen `DY/E/CHD`,
und `d/y/or/s` sind nicht automatisch `D_ADDR/Y/OR/S`.

Gefäß ist ebenfalls kein einzelner universeller Stamm. Es erscheint konkret
in Pharma als `AL=Aufnahme-/Zielgefäß`, `AR=Ausgangsgefäß`,
`L=Gefäßkontakt` und `OR=Gefäß- oder Arbeitseinheit`; in Biological werden
dieselben Relationskerne zu Zielbecken, Ausgangsbecken und Leitung. So sagt die
Komposition, welche Rolle das Gefäß spielt.

Reiben/Mahlen, Erwärmen, Kühlen, Trocknen, Einweichen und Baden sind die
bevorzugten **nächsten Unterlesungen** der kleinen Operationsstämme:

- `CHD + fester Pflanzen-/Drogenowner` → bearbeiten oder zerreiben;
- `T + Grad/Stufe` → temperieren; je nach Owner erwärmen, kühlen oder trocknen;
- `SH + physisches Gut/Form` → halten, ziehen lassen, einweichen oder baden;
- `S + Auszug/Portion` → auswählen, abtrennen, gegebenenfalls seihen/sieben.

Der aktuelle Renderer spricht an diesen Stellen noch die breiten Werte
`bearbeiten`, `temperieren`, `halten/baden` und `auswählen/abtrennen`; er
enthält noch keine automatische Objekt×Grad-Regel, die sicher zwischen Mahlen,
Erwärmen, Kühlen, Trocknen, Einweichen und Seihen entscheidet. Die Liste ist
deshalb eine konkrete Kandidatenqueue für den nächsten Pass, keine bereits
implementierte Feinübersetzung.

## Warum die einfachen Einworttheorien nicht die Basis werden

| Pack | benötigte Karten | problematische produktive Slots | Ergebnis |
|---|---:|---:|---|
| Register-Hybrid | 305 | 0 deklarierte Fremddomänen | ausgewählt |
| nur Apothekerrezept | 124 | 2.666 Himmels-Slots | als mutiger Rivale behalten |
| nur Tabelle/Position | 124 | 9.490 Nichttabellen-Slots | als Rivale behalten |
| jede Registeroberfläche lernen | 2.749 | keine Fremddomäne, aber keine Compoundprognose | nicht als Basis |

Nur der Register-Hybrid wird als vollständige Ausgabe gerendert. Die drei
Rivalenzahlen sind heuristische Domänenkosten beziehungsweise
Wörterbuchgrößen, keine Ergebnisse dreier weiterer Vollübersetzungen. Die Null
in der ersten Zeile ist ebenfalls keine Wahrheitsmessung; sie bedeutet, dass
der Adapter seine fünf vorgesehenen Domänen abdeckt. Der eigentliche Hausverstands-
Vorteil zeigt sich in den ganzen Passagen: `AIIN=Wasser`, `T=erhitzen`,
`S=seihen`, `CHD=mahlen`, `OR=Gefäß` oder `Y=Pflanzenteil` funktionieren lokal,
erzeugen aber im Ring-, Bad- oder Quellregister sofort wiederholten Unsinn.
Darum bleiben diese als lokale Ausbauten verfügbar, nicht als neue globale
Stämme.

## Ganze Passagen statt schöner Einzelwörter

Der Pass enthält 25 vollständige Ereignischecks und zwanzig vollständige
Aussagenchecks, gleichmäßig über alle fünf Register. Die zwanzig Aussagen sind:

- Quelle: G407-S002, G407-S003, G515-S042, G515-S043;
- Herbal: G407-S010, G407-S013, G407-S020, G407-S028;
- Celestial: G407-S041, G407-S045, G407-S052, G407-S061;
- Biological: G407-S082, G407-S083, G407-S086, G407-S193;
- Pharma: G407-S649, G407-S651, G407-S657, G407-S659.

Die Texte sind noch keine glatte Prosa. Sie sind aber vollständig, jeder
Ausdruck bleibt an seinem exakten Host, und alle Register bleiben unter
derselben Kompositionsregel lesbar. Die TSV-Datei
`gdt582_20_complete_passage_sense_checks.tsv` stellt alte Strukturstimme und
neue konkrete Arbeitslesung direkt nebeneinander. Ein unabhängiger manueller
Audit aller 45 Karten und der gesamten lokalen Namensschicht fand keinen
materiellen Korrekturbedarf; sein Protokoll steht in
`artifacts/GDT582_MANUAL_SENSE_AUDIT.md`.

## Reality Check

Was GDT582 wirklich erreicht:

- Es gibt keine **leeren Defaultfelder** mehr; die wirkliche Semantik der Slots
  bleibt unbekannt.
- Häufige Analyseklassen tragen kurze, wiederverwendbare Funktionen statt
  satzgroßer Fantasiebedeutungen.
- Konkrete Einzelstoffe und Pflanzenorgane haben endlich benannte Plätze.
- Die 42 Analyseklassen reichen innerhalb der festen Segmentierung
  kompositionell für 99,20 % der offenen Inhaltsoccurrences. Aktuell existieren
  jedoch nur 80 gelernte Klasse×Kern-Typen plus zwei `LOCAL_X`-Karten; die
  Kapazität für hunderte neue konkrete Begriffe auf neuen Seiten ist noch nicht
  getestet.
- Die komplette Dreißig-Seiten-Ausgabe lässt sich jetzt als einheitliche
  Arbeitsübersetzung lesen und gegen künftige Seiten halten.

Was noch nicht erreicht ist: Wasser, Wein, Salz oder eine Handlung sind nicht
entziffert. Die Zuordnungen sind die beste gegenwärtige Arbeitstheorie. Ihr
Wert liegt darin, dass sie vollständig, kompakt, konkret, passagefähig und
leicht ersetzbar ist.

## Nächster sinnvoller Schritt

GDT582 beendet den ersten konkreten Fülldurchgang. Als nächstes sollte nicht
noch einmal die Grammatik poliert werden. Stattdessen werden die 80 gelernten
Klasse×Kern-Karten und die stärksten physischen Unterlesungen nacheinander in
der vollständigen Ausgabe verbessert: zuerst Wasser/Wein/Öl/Salz und
Pflanzenorgane, dann die Verbübergänge CHD/T/SH/S, danach Krankheit/Heilmittel.
Eine neue Seite muss dafür noch nicht geöffnet werden.

## Claim ceiling

GDT582 veröffentlicht eine vollständige explorative Arbeitsübersetzung und ein
innerhalb der festen GDT581-Segmentierung kompositionelles Hauscodebuch für die
gegenwärtigen dreißig Seiten. Es
bestätigt kein Lexem, keinen Klartext, keine Sprache, kein historisches
Codebuch, keine Gattung und keine objektive Stoff-, Pflanzen-, Krankheits- oder
Verfahrensidentität und enthält keinen Held-out-Test oder Parser für neue
Oberflächen/Seiten. Ein Default bleibt stehen, bis eine Passage ihn unmöglich
macht oder ein besserer Wert mehr Komposition mit weniger Sonderregeln liefert.
