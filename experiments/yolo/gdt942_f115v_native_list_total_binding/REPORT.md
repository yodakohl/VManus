# GDT942 — Sichtprüfung von f115v.37–40

**Ergebnis: NO_VISUAL_LIST_TOTAL_BINDING.** Im Original stehen die kurzen Formen,
die ZL/RF als `o l r` und IT als `olr` wiedergeben, mit sichtbaren Zwischenräumen
innerhalb einer normalen Textzeile. Es gibt im untersuchten Absatz weder eine
besondere Abgrenzung als Listeneinträge noch ein separates sichtbares Mittel,
das sie gemeinsam mit dem folgenden `aiiin`-Ausdruck verbindet. Deshalb wird
hier keine Zahl und kein Wort ausgewählt. Der lokale Beweisversuch „drei Formen,
also bedeutet das folgende Wort drei“ wird eingestellt.

Das ist eine tatsächliche native Bildbeobachtung, kein unabhängiger Beleg für
die Transkription aller Zeichen. Eine implizite sprachliche Liste, Dosis oder
Gradangabe bleibt möglich. Die vorher festgelegte Sichtbarkeitsanforderung war
eine Zugangsvoraussetzung für den Zähltest, keine universelle Vorhersage jeder
Listenhypothese. Ihr Fehlen widerlegt diese breiteren Hypothesen nicht.

## Bild und vollständiger Textumfang

Quelle: [Yale/Beinecke MS408, f115v, Canvas1006275](https://collections.library.yale.edu/iiif/2/1006275/full/full/0/default.jpg).
Die unveränderte [Originaldatei](artifacts/SOURCE_F115V.jpg) ist beigefügt;
2676×3697 Pixel, 2.213.260 Bytes, SHA-256
`5700486404459fe1abfc11f6347aa0171bd651e39bcf71d594beecfb170ed8a3`.

[Ganzer Zielabsatz mit Randkontext](artifacts/PARAGRAPH_FULL.png) ·
[Detail der Zielzeile](artifacts/TARGET_LINE_DETAIL.png) ·
[Alle vier Zeilen in allen drei vorhandenen Lesungen](artifacts/FULL_PARAGRAPH.md).

Die drei Ausschnitte enthalten unveränderte Originalpixel; Koordinaten und
Hashes stehen in [CROPS.json](artifacts/CROPS.json). Unvermeidbare Fragmente
benachbarter Zeilen dienen ausschließlich der Lokalisierung. Sie wurden nicht
transkribiert oder inhaltlich ausgewertet. Die erste, verworfene Begrenzung des
später erweiterten Vollabsatzausschnitts war [380,2460,2590,2790], SHA-256
`1142a0350fbd7e53dfafc1164ff232a89cefb13dec59e4e1411857393655ee89`;
sie wurde vor Beobachtungsfixierung durch [380,2410,2590,2790] ersetzt, damit
auch die hohen Zeichen am Absatzanfang im Kontext liegen. Keine Pixelbearbeitung.

Alle vorhandenen Zielgruppen wurden unverändert übernommen: ZL39, IT34, RF37,
insgesamt110 alternative Gruppenpositionen auf **einem** Blatt. Das ist die
Abdeckung der geerbten Texte, keine Zahl neu optisch bestätigter Zeichen.
Rohgruppen und Separatorflags bleiben in [EXPECTED_GROUPS.tsv](artifacts/EXPECTED_GROUPS.tsv).

## Beobachtung nach den fünf vorab festgelegten Feldern

| Feld | Beobachtung | Status |
|---|---|---|
| Lokalisierung | Vier aufeinanderfolgende Zielzeilen; gesuchte Folge in der zweiten; kürzere letzte Zeile. | PRESENT |
| Eigene Mitgliederabgrenzung | Abstände zwischen kurzen Formen, aber keine Listenzellen, Anstriche, getrennten Eintragszeilen oder Klammer. | ABSENT |
| Separate Listen-Wert-Bindung | Folgender Ausdruck und Schlussgruppen laufen auf derselben Zeile weiter; kein eigenes Zuordnungszeichen. | ABSENT |
| Vollständiger Zielbereich | `llchs` bis `sham` sichtbar; kurze Formen nicht ein durchgehender Tintenstrich; genaue Zeichenidentität und Minimzahl bleiben ungeklärt. | PRESENT |
| Paralleles Listenlayout im Restabsatz | Übrige Zeilen bestehen ebenfalls aus horizontalen Gruppenfolgen. Randsterne gliedern Textblöcke, nicht die drei kurzen Formen einzeln. | ABSENT |

ABSENT betrifft das jeweils definierte sichtbare Merkmal. Es bedeutet weder
„keine Zwischenräume“ noch „keine sprachliche Beziehung“. Die vollständigen
Beobachtungen samt Pixelregionen und Einschränkungen sind vor der maschinellen
Auswertung in [OBSERVATIONS.json](artifacts/OBSERVATIONS.json) fixiert.

## Kandidaten und Entscheidung

| Kandidat | Vorher verlangte Konsequenz | Tatsächlicher Befund und Widerspruch | Verbleibende Mehrdeutigkeit | Unabhängige Bestätigung in diesem Test |
|---|---|---|---|---|
| Liste + Gesamtzahl | Für diesen sichtbaren Beweisweg: eigene Mitgliederabgrenzung **und** eigene Listen-Wert-Bindung. | Beide fehlen in der Beobachtung. Sichtbarer Beweisweg nicht unterstützt; kein Widerspruch gegen jede implizite Liste. | Anzahl der Referenten und Bedeutung von `aiiin` unbekannt. | 0 Blätter / 0 Bedeutungsprüfungen |
| Dosis je Eintrag | Keine eindeutige Layoutvorhersage vorregistriert. | Derselbe ganze Absatz; keine dosisspezifische Konsequenz geprüft. | Eintragszuordnung, Dosis und Einheit fehlen. | 0 / 0 |
| Grad oder einzelner zusammengesetzter Ausdruck | Keine eindeutige Layoutvorhersage vorregistriert. | Spatien allein widersprechen einer Zusammensetzung nicht. | Wortgrenze, Skala und Bedeutung offen. | 0 / 0 |

Maschinenlesbar: [CANDIDATE_DECISIONS.tsv](artifacts/CANDIDATE_DECISIONS.tsv).
Die drei semantischen Konkurrenten sind mit diesem Bildbefund **nicht
unterscheidbar**. Es wird kein Kandidat wegen bloßer Widerspruchsfreiheit gewählt.
GDT941s vier Rechen-/Vergleichskerne und GDT940s verworfene Zehnwort-Erweiterung
bleiben unverändert. Es gibt keine neue Präfixregel, keinen Decoder und keine
Transkriptionskorrektur. GDT939s Arbeitslesung bleibt eine Hypothese.

## Registrierung, Exposition und Grenzen

Lokale Registrierung: 2026-09-14 15:56:46 UTC; Bildbezug:15:57:32 UTC;
Beobachtungsfixierung nach Sichtung, vor Ergebnislauf. Die Registrierung wurde
**nicht** schon vor dem Download öffentlich gepusht. [PREREG_LOCK.json](PREREG_LOCK.json)
bindet14 Dateien; [OBSERVATION_LOCK.json](OBSERVATION_LOCK.json) bindet die
Beobachtungen und endgültigen Ausschnittdaten.

Der Textabsatz, die Leservarianten und die Idee waren aus GDT941 bekannt.
Root beobachtete als informierter Einzelbeobachter. Kein unabhängiger
Paläograph, kein zweiter Beobachter und keine unabhängige Bedeutungsprüfung.
Die andere bekannte `o l r`-Stelle auf f111v war bereits Teil der Auswahl;
sie ist kein hier zurückgehaltenes Bestätigungsblatt. Alternative Lesungen
zählen nicht als unabhängige Manuskripte. Kein unexponiertes Blatt wurde getestet.

f115v wurde vor Öffnung als letzter Bildplatz zugelassen: jetzt50 Bildschlüssel /
56 Selektoren. Nur der ganze feste Absatz37–40 wird detailliert untersucht;
Ganzseite nur zur Lokalisierung. f84/f84r bleiben geschlossen, f116v unzugelassen,
Reserven ungeöffnet. Keine Kontakte. Die historischen Vorgänger wurden in ihren
relevanten sicheren Entscheidungsteilen geprüft; die frühere f84-Erwähnung in
einem alten Bericht war kein Zugriff auf dessen Bild oder Rohtext.

Kein Zahlenwerttest, keine kalibrierte Gegenkontrolle der gesamten Suche,
keine Signifikanzbehauptung und kein score-ready Beziehungspaket.

## Reproduktion und Konsequenz

```sh
python3 experiments/yolo/gdt942_f115v_native_list_total_binding/src/run.py
python3 experiments/yolo/gdt942_f115v_native_list_total_binding/src/validate.py
```

`src/acquire.py` kann die exakt festgelegte Originalquelle beziehen; die
beigefügten Originalbytes reichen für einen Lauf ohne Netzwerk. Der Validator
prüft registrierte Hashes, Bildidentität, pixelidentische Ausschnitte, alle110
geerbten Gruppen und die Konsistenz der Entscheidung. **PASS** bedeutet keine
unabhängige visuelle oder semantische Bestätigung.

Entscheidung: Diese Stelle liefert keine Grundlage, einen Zahlenwert auszuwählen.
Kein Anschlussversuch mit angepassten Abständen, Präfixen oder Minim-Offsets.
Ein späterer Listen-/Zahlversuch braucht eine zusätzliche konkrete geschriebene
Bindung; das Zählen dieser drei Formen allein genügt nicht. Die weitere
Lesungsarbeit muss wieder Zusammenhänge in vollständigen exponierten Passagen
untersuchen. Das Bild eröffnet hier keinen neuen Bedeutungsanker.
