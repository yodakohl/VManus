# GDT600 — aus der vollständigen Objektliste wird eine Grammatik

## Ergebnis

GDT600 verändert 1.108 von 2.272 Hostklauseln und 955 von 1.443
Aktionsklauseln. 298 der 313 Aussagen werden dadurch lesbarer. Trotzdem bleibt
die gesamte GDT599-Bedeutungsschicht unverändert: 1.443/1.443 Objekte,
1.443/1.443 Quellenpointer, alle 24 Q-Übergänge, alle 313 Aussagen und alle
Absätze sind identisch fortgeführt. Verbvalenz, Determinierer und
Quellen-/Ziel-/Gradrelationen sind neue explizite Arbeitshypothesen, keine
behaupteten Invarianten. Der Validator besteht 326 Prüfungen.

Die größte Verbesserung ist nicht ein einzelnes Wort, sondern eine kleine
Kompositionsgrammatik:

| Oberfläche | Fälle | neue Lesung |
|---|---:|---|
| CH-Doppelverb | 168 | entnehmen / herausnehmen / ablassen nach Objekt und Pfad |
| OK-Doppelverb | 234 | vorbereiten |
| explizit non-T-governierter Zielgrad | 485 | Vorgangsbedingung `bei Grad` |
| T-/ungebundene Rahmengrade | 54 | Einstellung auf Grad / neutrale Gradangabe |
| geordnete Modifierpakete | 378 | Modus → Herkunft/Empfänger → Grad → Ort/Bad → Pfad/Ziel |
| FRAME-Fragmente | 153 | vollständiger Imperativ |
| Q-Aktionen | 24 | Eingang zuerst, Resultat danach |
| Q-Folgebezüge | 7 | `diesen neuen Stationsansatz` |
| wiederholte Aktionen | 18 | `erneut` innerhalb desselben Arbeitsgangs |
| K mit Quelle ohne Ziel | 10 | heranführen / heranbringen |

## Konkrete Sätze

Die neue Grammatik erzeugt unter anderem:

- `Entnimm an der Arbeitsstelle über Kontakt oder Leitung eine Probe am selben Körperteil.`
- `Bereite diese Probe bei Grad II vor.`
- `Lass den Stationsansatz bei Grad I an der Arbeitsstelle entlang des Stationswegs oder des Kanals ab.`
- `Führe die Anwendungsportion der Zielstation oder dem Zielbecken über Kontakt oder Leitung zu.`
- `Halte die Badeinheit aus der Ausgangsstation oder dem Ausgangsbecken an der Arbeitsstelle im Bad.`
- `Bereite den Stationsansatz und das Stations- oder Badmaß in Anwendungsform bei Grad II an der Arbeitsstelle vor; der vorbereitete Stationsansatz gilt nun als neuer Bad- oder Stationsansatz.`
- `Halte diesen neuen Stationsansatz bei Grad II im Bad.`
- `Bringe denselben Körper erneut ein.`

Die zwei letzten Q-Folgebezüge waren vorher unsichtbar, weil ihr Zustand nicht
direkt auf die Q-Aktion zeigte, sondern über `CARRY:G407-E2468` und
`HANDOFF:G407-E3233:…` lief. Der Renderer löst diese Aliase jetzt auf, ohne den
gespeicherten Quellenpointer zu ändern.

## Was an der Theorie stärker geworden ist

Die Objektklasse wirkt nun tatsächlich kompositionell. CH bedeutet nicht mehr
den langen Satz `Entnimm oder lass … ab`, sondern realisiert eine gemeinsame
Entnahmefamilie: Portionen werden entnommen, Körper oder Einheiten
herausgenommen, Flüsse und Stationsansätze mit sichtbarem Kanal abgelassen.
K unterscheidet dagegen Bewegung zum Empfänger von Herkunft ohne Empfänger.
T und P lesen ein Ziel meist als Zweck; SH und reine Rahmen lesen es als Ort.

Auch die Gradgrammatik wurde enger. Ein direkter T-Schritt und ein ausdrücklich
T-governierter Rahmen spricht `mit Einstellung auf Grad`: hier ist der Grad ein
eingestelltes Ziel. Bei expliziten non-T-Vorgängen wird derselbe sichtbare Grad
als Arbeitsbedingung `bei Grad` gesprochen. Gemischte und ungebundene Frames
werden nicht geraten, sondern neutral als `Gradangabe` markiert.

Die sieben früher manuellen FLOW-Fälle W03–W09 sind jetzt eine einzige
CH+Kontakt/Leitung-Regel. W01, W02, W10 und W11 bleiben ehrlicherweise lokale
Entscheidungen. Ebenso zerfällt die alte Gruppe von 21 rechten Ergänzungen in
16 echte fertige rechte Quellen und fünf Rootdefault-Vorschauen.

## Was noch breit ist

Die Grammatik ist fertig genug, um wieder an Bedeutungen zu arbeiten, aber sie
ist noch keine feingliedrige Fachsprache:

- 972 der 2.272 Hosts tragen das breite Lemma `Stationsansatz`;
- 54 Aktionen beruhen weiterhin direkt auf einem Rootdefault;
- 125 Projektionen bleiben in der Reviewqueue;
- R=`Kennzeichne oder prüfe` bleibt in allen 52 Fällen absichtlich breit;
- die Wörter `Bad- oder Stationsansatz`, `Station`, `Bedingung`, `Maß` und
  `Einheit` bezeichnen Arbeitsklassen, noch keine historisch identifizierten
  Stoffe oder Gefäße;
- keine Oberfläche entscheidet allein zwischen Wasser, Wein, Öl, Salz,
  Pflanzenteil, Gefäß, Krankheit oder Körperstelle.

Der nächste sinnvolle Schritt ist deshalb keine weitere allgemeine Glättung.
Auf denselben sechs Seiten sollte die große STATION-Klasse aus sichtbarer
Herstellung, Badgebrauch, Kanalgebrauch, Q-Neubildung und Körperkontakt in
wenige vorhersagbare Untertypen zerlegt werden. Erst wenn solche Untertypen
Root×Pfad×Quelle×Folgeaktion wiederholt tragen, werden konkrete Fachwörter wie
Bad, Ansatz, Behälter, Kanal oder Flüssigkeit an feste Slots gesetzt.

## Historischer Formvergleich

Die nun sichtbare Form — Imperativ plus Objekt, Mengen-/Gradangabe, Herkunft,
Arbeitsort und Ziel — ist mit spätmittelalterlichen Rezept- und
Werkstattanweisungen vereinbar. Die bereits in GDT599 dokumentierten Vergleiche
Harley MS 2378, Durham Cosin V.iv.8 und die Harleian cookery books zeigen genau
solche kompakten Mengen- und Verfahrenskonstruktionen. Dieser Vergleich
motiviert die deutsche Werkstattoberfläche, identifiziert aber weder ein
Voynich-Wort noch den wirklichen Manuskriptinhalt.
