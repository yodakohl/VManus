# Zwei Inhaltsfolgen der ganzen Pulverlesung

2026-09-22. **Bedingte Ableitungen aus dem eingefrorenen V2-Entwurf, keine neue Wortbedeutung und kein unabhängiger Test.** Die ganze deutsche Arbeitsfassung und beide V2-Verläufe wurden gelesen. Keine neue RAW-Karte: Die folgenden Folgerungen präzisieren das vorhandene Modell und seine erhaltenen Rivalen, statt diese unter einem neuen Namen erneut vorzuschlagen.

## 1. Das letzte Sieben übernimmt Eigenschaften, bestimmt aber einen Ausgang

Für den vollständigen f21r-Absatz gilt im Modell Q>0. Nach der ersten Trennung stehen der grobe Anteil C mit c>0 und der feine Pulveranteil P mit p≥Q getrennt bereit; M=c+p. Die Folgerung für .12 hängt an der ganzen geschriebenen Vorgeschichte:

1. `.9 RINSE ... UNTIL CLEAN` setzt CLEAN am Pflanzenpatienten B, nicht am zuletzt genannten Wasser. Der Modellvertrag erhält den gewünschten Pflanzenfeststoff und gestattet die Entfernung fremden Schmutzes.
2. `.10 DRY` trocknet denselben B erneut nach dem Spülen. Im V2-Handkonto hat B danach kein zurückgehaltenes Wasser und trägt DRY/CLEAN. Das ist der relevante zweite Trockenschritt; ein altes DRY-Flag aus .8 darf nicht über die Wasserzugabe hinweg als Beweis dienen.
3. Mahlen und Trennen liefern C und P. P ist der feine Zweig; CLEAN und der im Handkonto angesetzte trockene Zustand werden unter der allgemeinen Erhaltungsregel übernommen. Nachfolgendes Aufbewahren, Abdecken und getrenntes Lagern von C erzeugt kein anderes P und verunreinigt es im idealisierten Vertrag nicht.
4. `.12 RETRIEVE POWDER` wählt dieses vorhandene P. Das unmittelbar folgende SIEVE erzeugt den ausgewählten Ausgang U und gegebenenfalls den disjunkten Rest V. UNTIL bindet an **U**, nicht rückwirkend an die gesamte Eingangsmenge P und nicht an das bloß beschriebene Anfangsziel.

Damit gilt bedingt:

| Größe/Eigenschaft | Eingang P vor dem letzten SIEVE | Ausgewählter Ausgang U |
|---|---|---|
| Herkunft | ursprüngliche Wurzelcharge A | dieselbe Herkunft A |
| Feinheit | FINE | FINE übernommen |
| Reinheit | CLEAN aus dem früheren Spülen, bei erhaltener Reinheit | CLEAN übernommen |
| Trockenziel | zweiter DRY-Schritt und danach keine erneute Wasserzufuhr | soll das ursprüngliche DRY-Ziel erfüllen; siehe Einschränkung unten |
| Feststoffmasse | p≥Q, nicht notwendig Q | genau Q durch die gebundene Ausgangsanforderung |
| Weiterer Rest | noch Teil des Eingangs P | V=p−Q, nur bei positivem Betrag ein Materialknoten |

Der Gehalt von „bis das Pulver fein und gereinigt ist und Q umfasst“ ist hier also kein Beleg, dass das letzte Sieben erstmals Feinheit oder Reinheit erzeugt. Die neue mengenmäßige Festlegung betrifft den **ausgewählten Ausgang**. P darf bereits Q groß sein; dann ist V=0 zulässig. Daraus folgt weder, dass SIEVE nutzlos wäre, noch dass UNTIL falsch wäre oder der geschriebene Arbeitsschritt entfallen dürfte. Der Vertrag behauptet keine notwendige strikte Verbesserung aller Endprädikate und keinen zwingend positiven Siebrest. Insbesondere wird kein neuer WHILE-/DO-UNTIL-Simulator eingeführt.

Die DRY-Grenze bleibt ausdrücklich erhalten: Die formale Rücknahme eines DRY_STATE-Prädikats bei erneutem Befeuchten ist im Entwurf nicht vollständig spezifiziert. Der zweite DRY-Schritt und das spätere Fehlen einer Wasserzufuhr machen die beabsichtigte trockene Zielbindung nachvollziehbar; diese Notiz ergänzt aber keine fehlende allgemeine Aktualisierungsregel und behauptet keine vollständige maschinelle Ableitung des Zielprädikats. Ebenso sind tatsächlicher Trocknungserfolg und physikalische Prozessparameter ungemessen.

**Unterscheidbarer Inhaltsanspruch:** Eine Paraphrase, die erst das letzte Sieben als hergeleiteten Ursprung von CLEAN behandelt, oder die Q schon der gesamten ursprünglichen Wurzelcharge beziehungsweise zwingend P zuweist, gibt diese ganze V2-Lesung nicht korrekt wieder. Der Stoff- und Eigenschaftspfad, nicht ein neues Wort, begründet diese Grenze. Er bevorzugt keine der vier erhaltenen Fassungen: Ihr f21r-Verlauf ist identisch.

## 2. CARRY und FRESH verbinden die erste Vorbereitung mit verschiedenen Produkten

Die andere Konsequenz betrifft den vollständigen f32v-Absatz und die **Herkunft der später bearbeiteten Feststoffe**, nicht allein ihre Gesamtmasse.

Unter CARRY+ADD ist die anfängliche Wurzelcharge A nach Zerkleinern, Trocknen im Schatten über Nacht und gleichmäßigem Durchmischen derselbe vorbereitete Bestand B. Die erschöpfende .8-Bestandslesung bindet seine Komponenten als C:2Q und P:Q; damit N=3Q. Danach gilt:

```
A → vorbereitetes B → C → F:Q und G:Q
                  └→ P → Feststoff der Paste T:Q
```

Alle drei am Ende erhaltenen Pflanzenfeststoffprodukte stammen vollständig aus A. F und G entstehen über den groben Zweig, der Pastenfeststoff über den schon vorher abgetrennten feinen Zweig P. Die Arbeit an C verbraucht P nicht. Wasser und Öl für T sind ausdrücklich zusätzliche, getrennt bilanzierte Stoffe; die Herkunftsaussage betrifft den Pflanzenfeststoff. TWO_EQUAL_PORTIONS ändert diese Gesamtquellenzugehörigkeit nicht, lässt aber die einzelnen C1/C2-Beiträge zu F/G offen.

Unter der vollständigen FRESH_INPUT_LISTS-Rivalenregel werden dagegen zwei neue Pflanzenzufuhren angenommen: E:3Q an der unmarkierten .8-Liste und P′:Q an der .10-Liste. Die Pfade sind:

```
A → vorbereitetes B:N → bleibt unbenutzt vorhanden
neues E:3Q → C → F:Q und G:Q
          └→ altes P:Q → bleibt unbenutzt vorhanden
neues P′:Q → Feststoff der Paste T:Q
```

Somit erreicht **kein Pflanzenfeststoff aus der anfänglichen Charge A** die später ausdrücklich sortierten Produkte F/G oder die Paste T. Die anfänglich geschriebenen Vorbereitungsarbeiten haben weiterhin den Gegenstand B; sie werden nicht gelöscht. Sie liefern in dieser Rivalenfassung jedoch weder den sortierten groben Zweig noch die spätere Pulverzutat. Aus dem anfänglichen Trocknen darf daher auch keine durch diesen Schritt begründete Vorbehandlung von E oder P′ abgeleitet werden. Das behauptet nicht, dass neu zugeführte Ware nass oder unvorbereitet sein müsse; ihre eigene Vorgeschichte ist damit lediglich nicht diese geschriebene Anfangsvorbereitung.

**Unterscheidbarer Inhaltsanspruch:** „Die am Anfang vorbereitete Wurzel wird später zu den beiden aufbewahrten Produkten und zur Pastenzutat“ gehört zu CARRY, nicht zu FRESH. Beide Fassungen bleiben mit ihren bisherigen Voraussetzungen erhalten. Die geschlossen gelesene Passage verlangt nicht, jeden Vorrat zu verbrauchen; die unbenutzten B/P sind deshalb kein neuer Fehler von FRESH. Diese kausale Unterscheidung ist keine unabhängige Beobachtung und kein Beleg zugunsten von CARRY.

## Umfang und unveränderte Grenzen

Die Ableitungen benutzen ausschließlich die festen ganzen f21r/f32v-Lesungen, ihre Material- und Referenzregeln und ihre bereits vorhandenen Rivalen. Kein gezielter neuer Absatz, Zensus, Decoder, Experiment oder Bedeutungswechsel. Die Quellen-/Leserunsicherheiten und 65+15 ausdrücklich hypothetischen Werte bleiben bestehen. Die f4r-Fortsetzung bleibt unvollständig; 514s Kapazitätsauswahl, 515s zusätzliche Schnittannahme und 517s notwendige Schreibkonflikte werden weder erneut getestet noch repariert.

Gebundene Hauptdateien:

- Deutsche vollständige Arbeitslesung: `raw370_german_whole_working_reading_20260922.md`, SHA256 `966e4e28eaba4588e58cfe6516dc9c7627e84e66eab24d341015d145f8190f30`.
- V2-Vertrag: `raw370_powder_partition_v2_material_contract_20260922.json`, SHA256 `7676250faf7adabc2fd240635a520852c65c2d7a2f8070fb82717351a8ab6d78`.
- V2-Handkonten: `raw370_powder_partition_v2_material_contract_20260922.md`, SHA256 `c90de002dde795dc35502e7d32692515459859e49e323fc51865b7fcf4110a61`.
- V1-Lexikon/ganze Zuordnungen: `raw370_two_paragraph_powder_partition_offer_20260922.json`, SHA256 `4654afe0414d85f431371c799df6189b73b2cd4ace6adfc7eae833a51bf837da`.

Route, Rezeptkontext, begrenzte Registry-/Duplikatsuche sowie die genannten V2-/f4r-/517-Primärgrenzen wurden gelesen. Keine Registry-Mutation und keine Änderung einer gebundenen Vorlage. Null bestätigte Wörter.
