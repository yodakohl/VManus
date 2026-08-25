# Pass 1015 — vollständige 627-Aussagen-Kernausgabe

## Ergebnis

Alle **627 Aussagen / 3.888 laufenden Gruppen** besitzen jetzt eine kurze Lesung aus genau sechs Schichten:

> **Besitzer · Posten/Menge · Handlungskette · Relation/Adresse · Grad/Stufe · Ende**

Die 35 optisch geprüften Passagen behalten ihre manuelle Pass-1014-Fassung. Die übrigen **592** werden mechanisch aus dem 46-Zeichen-Blatt zusammengesetzt. Keine Zeile braucht dafür ein neues Spezialwort.

## Was die Bereinigung entfernt

In **255/627** alten Arbeitsübersetzungen standen noch konkrete Ausmalungen, die nach Pass 1013 nicht mehr als Wörter gelten. Die häufigsten sind:

- `BEARBEITEN`: 110 Aussagen
- `ABSETZEN`: 71 Aussagen
- `DURCHLASS`: 59 Aussagen
- `AUSZUG`: 34 Aussagen
- `BEREIT`: 19 Aussagen
- `SPUELEN`: 13 Aussagen
- `AUFFANGEN`: 12 Aussagen
- `ABTRENNEN`: 3 Aussagen
- `KUEHLEN`: 2 Aussagen
- `WAERME`: 1 Aussagen
- `FILTER_ODER_SEIHEN`: 1 Aussagen

Diese Wörter sind nicht pauschal „verboten“. Sie dürfen lokal weiterhin eine passende Ausführung beschreiben. Sie stehen aber nicht mehr im Wörterbuch und werden daher nicht mehr automatisch in jede passende Form hineingelesen.

## Die neue vollständige Lehrform

Jede TSV-Zeile enthält neben der lesbaren Fassung eine explizite Signatur, zum Beispiel:

`OWNER=... | ITEM=POSTEN | QUANTITY=MASS | ACTIONS=NEHMEN+SETZEN+GEBEN | RELATIONS=VERBINDUNG+ZIELORT | GRADES=II | END=CLOSE`

Damit kann ein Schreiber die Aussage aus dem Bildbesitzer und denselben kleinen Kernwerten erneut aufbauen. Lokale Zeichen werden als lokale Kennung mitgeführt, nicht als erfundenes neues Substantiv.

## Beispielpassagen

### P1009-S001 · f10r

> Vom gezeigten Wurzelstock den bezeichneten Posten nehmen, nach Maß setzen, halten und weitergeben; den Arbeitsgang schließen.

### P1009-S003 · f11r

> Vom gezeigten Blütenkraut einen Teil wählen, nach Maß halten, in den nächsten Arbeitsgang setzen und schließen.

### P1009-S013 · f17r

> Beim Bildbesitzer „abgebildete ganze Bluetenpflanze mit Blatt-, Blueten- und Wurzelteilen“: den Posten fortsetzen, nehmen, geben und setzen; vom bezeichneten Ausgang und im bezeichneten Lauf; mit der lokalen Kennung; schließen.

### P1009-S107 · f75r

> In der lokalen Szene „großes Bad-/Stationsblatt mit dreieckiger Insel“: den Posten fortsetzen und halten; in Grad I; schließen.

### P1009-S400 · f81v

> Danach den Posten im gemeinsamen Badfeld über den markierten Lauf führen, mehrfach im zweiten Grad setzen und halten und schließlich schließen.

### P1009-S498 · f82r

> Im unteren getrennten Becken eine Portion setzen, nach Maß in Grad I oder II halten, lokal nehmen und geben und offenlassen.

### P1009-S032 · f67r2

> Im Himmels-Namensraum „zwei getrennte Himmelsräder und Tabelle“: danach; am Ansatz; eine Portion nach Maß setzen, wählen, geben, markieren, einsetzen und nehmen; vom bezeichneten Ausgang und zum bezeichneten Ort; in Grad I; auf der bezeichneten Arbeitsstufe; mit der lokalen Kennung; bis zur sichtbaren Grenze führen.

## Was jetzt wirklich stabiler ist

- Die Wörterbuchgröße bleibt **46 Zeichen**, davon 19 portable Kerne.
- Die neun Satzschubladen bleiben unverändert: T01=102, T02=23, T03=71, T04=36, T05=15, T06=98, T07=125, T08=116, T09=41.
- Alle **566** lizenzierten Schlüsse bleiben Schlüsse; offene und bildbedingte Grenzen bleiben getrennt.
- Bildwörter stehen nur dort, wo der sichtbare Besitzer sie liefert.
- `CHK` und `C<K>H` werden überall als dieselben Handlungsatome mit anderer syntaktischer Verpackung behandelt.

## Nächste Engstelle

Nach dieser Bereinigung liegt der semantische Rest nicht mehr bei zehn angeblichen Fachstämmen, sondern bei den **19 lokalen Zeichen**. Der nächste Durchgang muss prüfen, welche davon wirklich bloße Adressen oder Renderer sind und welche sich über mehrere Besitzer hinweg zu wenigen wiederkehrenden lokalen Kategorien bündeln lassen.
