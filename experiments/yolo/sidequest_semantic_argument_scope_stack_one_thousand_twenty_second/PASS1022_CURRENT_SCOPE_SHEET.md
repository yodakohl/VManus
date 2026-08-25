# Die Klammerseite für den Lehrling

Diese Seite kommt hinter die Pass-1021-Wurzeltafel. Sie ändert kein Wort. Sie
sagt nur, woran **WERT, ANTEIL, EINHEIT, POSTEN, ORT, LAUF und GRAD** hängen.

```text
BESITZER [ GANG [ PAKET [ HANDLUNG [ POSTEN / WERT / ANTEIL / EINHEIT ]
                                  [ AUSGANG / VERBINDUNG / LAUF / ZIELORT ]
                                  [ GRAD / STUFE ] ] ] ] ]
```

## Acht Handgriffe

1. Das Bild, Gefäß, die Station oder das Rad bleibt Besitzer, bis wirklich ein
   neuer Bild-/Proseblock beginnt. Ein Zeilenknick ist kein Ende.
2. `Q` eröffnet unter diesem Besitzer ein neues Paket. Lizenziertes `DY`
   schließt das Paket; der Besitzer darf weiter gelten.
3. Zuerst die ganze Karte öffnen. Zwei Handlungsköpfe sind verschachtelt:
   `CH+K+Y = NEHMEN[GEBEN[POSTEN]]`. Nach der Karte bleibt der äußere Kopf
   verfügbar.
4. `OK CH SH K S T CHD R P` sind Handlungsköpfe. Ein einzelner Kopf trägt
   seine kurzen Zusätze und bleibt für die folgende Karte offen.
5. `OT` wechselt zum nächsten Geschwistergang, `OL` führt den offenen Gang
   fort, `OS/VORBEZUG` holt den vorherigen Besitzerrahmen zurück.
6. `Y AIIN AIN OR` nehmen zuerst den nächsten passenden Kopf ihrer Karte.
   Fehlt er, gilt der offene Kopf; am Anfang darf kurz bis zum nächsten Kopf
   desselben Besitzersegments vorausgebunden werden.
7. `AR/AL` bevorzugen den Kopf links. `L/AIR` öffnen einen Verbindungsrahmen
   nach rechts. Ohne Kopf bleiben sie am sichtbaren Besitzer, nicht an einer
   erfundenen Richtung.
8. `E EE EEE IIN DA O` verändern nur die gebundene Handlung. Sie sind weder
   Dinge noch selbständige Verben und reichen nicht über `DY` oder eine echte
   Besitzergrenze.

## Zwei Sondergriffe

- Gleiche Kerne an Paketgrenze steigen eine Ebene ab:
  `OK+OR+OR+Y = SETZEN[EINHEIT außen[EINHEIT innen[POSTEN]]]`.
- Frei doppelte Dinge bleiben zwei Dinge; frei doppelte Handlungen heißen
  „nochmals“. Kein Zeichen wird als überflüssig gelöscht.

## Vier Fragen beim Lesen

```text
Welcher Besitzer? — Welches Paket? — Welcher Handlungskopf? — Welcher Zusatz?
```

Konkrete Pflanze, Gefäßstelle, Himmelssektor oder Zutatenname kommt weiterhin
aus Bild und Meisterexemplar. Die Kurzkarte liefert die wiederholbare
Arbeitsklammer.
