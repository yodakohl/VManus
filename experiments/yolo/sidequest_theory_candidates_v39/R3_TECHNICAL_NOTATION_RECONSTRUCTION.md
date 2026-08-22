# V39/R3 — Revision als technisches Arbeitsregister

## Auftrag und Evidenzgrenze

Ich behandle die zwölf handübergreifenden exakten Karten aus V38 als ein
Lehrdeck einer kleinen Werkstatt um 1420. Jede Karte erhält einen konkreten
Defaultwert und zwei ausdrücklich lebende Rivalen. Das ist eine kreative
Rekonstruktion, keine Entzifferung. Gelesen wurden nur die aktuelle Route, die
kompakte Sidequest-Basis, die primären V38-Artefakte und die unmittelbaren
V25-Kontexte dieser zwölf exakten Karten. Die internen Koordinaten der Karten
wurden nicht als Bedeutung ausgegeben. `f84` und `f84r` blieben versiegelt.

## Wichtigste Revision gegenüber V38

V38 machte aus fast allen zwölf Karten Bestandteile eines medizinischen
Nassprozesses. Die Ereigniskontexte erlauben diese Lesung, erzwingen sie aber
nicht. Für ein von mehreren Händen verwendetes Kernset ist ein etwas
allgemeineres technisches Vokabular ökonomischer:

```text
PARAMETER   RÜCKVERWEIS   GEGENWÄRTIGE EINHEIT   ARBEITSANSATZ
ZUSTANDSPRÜFUNG   AUSWAHL/ENTNAHME   VOLLZUG   ZIELZUWEISUNG
```

Die Bilder und seltenen Karten spezifizieren dann Pflanze, Körperstelle,
Gefäß, Öffnung oder Sonderoperation. Das gemeinsame Deck organisiert Menge,
Referenz, Charge, Zustand und Weitergabe. Die vollständigen zwölf Entscheidungen
mit je zwei Rivalen stehen in `R3_COMMON_CARD_REVISION.tsv`.

## Die zwölf konkreten Defaultwerte

1. **`daiin` — in der im Artikel festgesetzten Menge.** Nicht zwingend eine
   Arzneidosis; es kann ebenso eine Sollzahl oder unveränderte Einstellung sein.
2. **`chol` — mit dem unmittelbar vorher bereitgestellten Ansatz.** Ein
   Rückverweis auf den vorigen Input, nicht auf eine universelle Flüssigkeit.
3. **`dy` — die jetzt bearbeitete Einheit.** Portion, Posten oder Arbeitsschritt
   werden durch Register und Bild ergänzt.
4. **`dal` — an die bezeichnete Zielstelle leiten.** In einer medizinischen
   Zeile: auf die dargestellte Stelle auftragen; in einer Apparaturzeile: einer
   Öffnung, Station oder Schale zuführen.
5. **`oky` — den gegenwärtigen Posten ausführen oder in Gebrauch geben.** Das
   kann Anwendung einer Arznei, Öffnen eines Wegs oder Freigabe eines Loses
   heißen.
6. **`chor` — der gegenwärtige gebrauchsfertige Ansatz.** Im medizinischen
   Register ein Sud; neutral ein eingerichteter Arbeitsbestand.
7. **`cthy` — sobald der vorgeschriebene Arbeitszustand erreicht ist.** Eine
   Bereitschaftsschwelle, nicht der Name eines Stoffes.
8. **`char` — aus derselben laufenden Charge.** Die Rivalen sind dieselbe
   Zubereitung oder unveränderte Quelle/Einstellung.
9. **`shey` — bis die Sichtkontrolle einen klaren oder freien Durchgang zeigt.**
   Bei Flüssigkeit heißt das klar ablaufen; neutral heißt es bestandene
   Durchgangs- oder Zustandskontrolle.
10. **`cholor` — aus dem zuvor zurückgestellten Ansatz entnehmen.** Gegenüber
    `chol` enthält der Default bewusst eine Entnahme oder Übernahme.
11. **`chty` — bis zu einem gleichförmigen Arbeitszustand bearbeiten.** Im
    Arzneikontext wahrscheinlich mischen oder rühren; im Kontrollregister
    Werte oder Zustand angleichen.
12. **`otchey` — das zuletzt bezeichnete Teilstück auswählen und entnehmen.**
    Seine zwei belegten feldinitialen Stellungen sprechen für einen neuen
    Auswahlbefehl über bereits vorhandenen Bestand.

## Vollständig ausführbare Dreifeld-Lehranweisung

Die unveränderte Kartenfolge aus V38 lautet:

```text
chol daiin
|
otchey chor chty char shey
|
cholor dy cthy oky dal
```

### Technisch neutrale Werkstattanweisung

> **Feld 1.** Nimm den unmittelbar vorher bereitgestellten Ansatz in der für
> diesen Artikel festgesetzten Menge als Eingabe.
> **Feld 2.** Wähle daraus das zuletzt bezeichnete Teilstück aus. Führe es dem
> gegenwärtig gebrauchsfertigen Arbeitsansatz zu und bearbeite beides, bis der
> Zustand gleichförmig ist. Ergänze dabei nur aus derselben laufenden Charge
> und fahre fort, bis die Sichtkontrolle einen klaren oder freien Durchgang
> zeigt.
> **Feld 3.** Entnimm nun aus dem zuvor zurückgestellten Ansatz die jetzt zu
> bearbeitende Einheit. Sobald der vorgeschriebene Arbeitszustand erreicht
> ist, gib den Posten frei und leite ihn an die durch Bild oder Register
> bezeichnete Zielstelle.

### Ausführung als Kontrollliste

| Schritt | Karte | Handlung des Lehrlings | Prüfbarkeit |
|---:|---|---|---|
| 1 | `chol` | vorherigen Ansatz identifizieren | Es gibt genau einen offenen Vorgänger. |
| 2 | `daiin` | dort hinterlegte Sollmenge übernehmen | Menge wird nicht neu geschätzt. |
| 3 | `otchey` | zuletzt markiertes Teilstück auswählen | Markierung/Artikelreihenfolge entscheidet. |
| 4 | `chor` | gebrauchsfertigen Arbeitsansatz bereitstellen | Arbeitsbestand ist vorhanden. |
| 5 | `chty` | bis Gleichförmigkeit bearbeiten | keine sichtbare Trennung/Abweichung mehr |
| 6 | `char` | nötigen Nachschub nur aus derselben Charge nehmen | Quellenwechsel ist verboten. |
| 7 | `shey` | Sichtkontrolle bis freier/heller Lauf fortsetzen | beobachtbarer Prüfzustand |
| 8 | `cholor` | aus dem zurückgestellten Vorgänger entnehmen | keine neue Charge beginnen |
| 9 | `dy` | die gegenwärtige Arbeitseinheit bestimmen | genau ein Posten ist aktiv |
| 10 | `cthy` | auf den vorgeschriebenen Bereitschaftszustand warten | Freigabebedingung erfüllt |
| 11 | `oky` | aktiven Posten in Gebrauch geben | Status wechselt von bereit zu ausgeführt. |
| 12 | `dal` | an die bezeichnete Zielstelle leiten | Bild/Register liefert das Ziel. |

Damit kommt keine Karte ohne Defaultbedeutung davon. Die Anweisung ist
redundant, aber für einen Lehrling ausführbar: `chol` eröffnet einen
Vorgängerbezug, `char` verbietet einen Chargenwechsel, und `cholor` fordert
später eine neue Entnahme aus dem zurückgestellten Bestand. Gerade diese drei
ähnlichen Verweise sind in einer praktischen Werkstatt nützlich.

## Medizinische Expansion derselben Folge

Unter der führenden iatromedizinischen Seitenhypothese kann derselbe
Arbeitsablauf flüssig so expandieren:

> Nimm von der vorherigen Zubereitung die im Artikel angegebene Menge. Wähle
> den zuletzt bezeichneten Anteil des fertigen Sudes, arbeite ihn mit Material
> aus derselben Charge gleichmäßig durch und fahre fort, bis die Flüssigkeit
> klar abläuft. Nimm dann aus dem zurückgestellten Ansatz die gegenwärtige
> Portion; sobald sie gebrauchsfertig ist, wende sie an der im Bild bezeichneten
> Stelle an.

Diese medizinische Fassung ist knapper, aber sie legt drei Dinge zusätzlich
fest, die die zwölf Karten allein nicht beweisen: `chor` ist Flüssigkeit,
`shey` ist Flüssigkeitsklarheit und `dal` ist eine Körperstelle.

## Medizinische Prozessnotation gegen generisches Kontrollregister

| Beobachtung im gemeinsamen Deck | medizinische Prozessnotation | generisches Werkstatt-/Kontrollregister |
|---|---|---|
| Menge, Portion, Charge | Dosierung und Arzneiansatz | Sollmenge, Los und Arbeitsbestand |
| `chor`, `cthy`, `shey` | Sud, Gebrauchsfertigkeit, klares Ablaufen | aktiver Bestand, Freigabestatus, Sichtprüfung |
| `oky`, `dal` | Arznei anwenden, Körperstelle | Posten freigeben, Zielstation zuweisen |
| Herbal + Biological Nutzung | gemeinsames Arznei- und Badevokabular | generische Karten werden auf zwei Arbeitsregistern wiederverwendet |
| viele lokale Karten | Pflanzen, Körperteile, Zutaten, Spezialoperationen | artikel- oder registereigene Material- und Stationscodes |
| bildgestützte Ellipse | Bild liefert Pflanze/Körperstelle | Bild liefert Objekt, Leitung, Gefäß oder Zieladresse |

### Entscheidung

**Intern gewinnt das generische Kontrollregister knapp.** Es erklärt alle
zwölf gemeinsamen Karten, ohne aus jedem Nass- oder Zielwort Medizin zu machen,
und es ist für mehrere Schreiber leichter zu lernen. **Als Seiteninhalt bleibt
medizinische Prozessnotation die stärkste Expansion**, weil Pflanzenbilder und
die Biological-Apparatur die neutralen Slots plausibel mit Arzneistoff,
Flüssigkeit und Anwendung füllen.

Die beste kombinierte Theorie ist daher nicht „Medizin oder Verwaltung“,
sondern:

```text
generische Werkstatt-Kontrollgrammatik
  + medizinische lokale Inhaltskarten und Bildargumente
  = knappes iatromedizinisches Arbeitsregister
```

## Was diese Runde wirklich verbessert

Die semantische Geschlossenheit von V38 war teilweise selbst erzeugt, weil die
zwölf alten Defaults schon medizinisch gewählt waren. R3 trennt nun den
kleinsten handübergreifend lehrbaren Funktionswert von seiner medizinischen
Expansion. Besonders wichtig sind vier Korrekturen:

- `dy` ist eher **aktiver Einheitspointer** als „Portion“;
- `dal` ist eher **Zielzuweisung** als ausschließlich „auf Körperstelle
  auftragen“;
- `oky` ist eher **Vollzug/Freigabe** als ausschließlich Anwendung;
- `shey` ist eher **sichtbare Freigabeschwelle** als ausschließlich klare
  Flüssigkeit.

Diese Revision macht den Encoder einfacher zu erlernen und zugleich weniger
literarisch. Sie erklärt aber noch keine Sprache und identifiziert kein
historisches Fachwort.

## Neue diskriminierende Vorhersagen innerhalb der zehn Seiten

1. Seltene Karten unmittelbar vor `daiin` sollten eher Menge/Objektadresse als
   vollständige Handlungen liefern.
2. Nach `cthy` sollte häufiger Vollzug, Übergabe oder Abschluss folgen als eine
   neue Stoffdefinition.
3. `dal` sollte auch dort sinnvoll bleiben, wo kein menschlicher Körper als
   Ziel sichtbar ist; dann muss Bild/Register eine Station oder Öffnung liefern.
4. `chol`, `char` und `cholor` dürfen nicht frei synonym sein: Vorgängerinput,
   Quellenkonstanz und erneute Entnahme müssen unterschiedliche Folgeökologien
   besitzen.
5. Wenn die rein medizinische Rivalin stimmt, sollten die lokalen Nachbarn von
   `chor`/`shey` überwiegend Nassoperationen sein. Wenn die neutrale
   Kontrolllesung stimmt, sollten auch trockene oder rein administrative
   Schrittfolgen ohne Bedeutungsbruch vorkommen.

Diese Vorhersagen dürfen in einer späteren kreativen Runde verfolgt werden;
hier wurden sie nicht nachträglich auf weitere Karten angepasst.
