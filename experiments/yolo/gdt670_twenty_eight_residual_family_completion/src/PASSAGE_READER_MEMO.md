# GDT670 blind candidate C — passage reader memo

## Hintergrund

1. Du bist ein um 1420 reisender Rezeptkopist, der fremde Werkstattzettel in brauchbare Anweisungen überträgt.
2. Du urteilst zuerst aus dem ganzen sichtbaren Absatz und erst danach aus isolierten Wortteilen.
3. Du achtest auf Zutatenlisten, Zustandsfolgen, Maße und Befehlswechsel.
4. Eine plausible Lesung darf vorläufig sein, aber sie darf keine unsichtbare Handlung erfinden.
5. Dein Qualitätsmaß ist: Könnte ein Gehilfe mit dieser Zeile konkret etwas tun oder erkennen?

## Vorgehen

Die 28 Ziele wurden in der vorgegebenen Source-Reihenfolge aus den vollständigen V46-One-Hole-Zeilen gelesen. ZL3b, IT2a und RF1b wurden über `READER_VARIANT_AUDIT.tsv` verglichen; es wurden keine Rohdaten und keine GDT670-Dateien anderer Kandidaten gelesen. Erst wurde die notwendige Zeilenfunktion bestimmt, danach eine V46-konforme Zerlegung gesucht.

Alle 28 Formen erhalten einen konkreten Default. Kompositionen benutzen ausschließlich vorhandene V46-Rollen und rekonstruieren die sichtbare ZL3b-Form. Kein Default führt Wasser, Wein, Öl, Salz, Gefäß, Krankheit oder Heilung ein.

## Nominal gegen Befehl

Die Passagefunktion trennt die wichtigsten Fälle deutlich:

- **Echte Befehle:** `ytey`, `qoiiin`, `ycthar`, `choeky`, `qokokchy`, `qetal`, `otodar`, `alsy`, `chearory` und `secheeol`. Sie tragen einen Befehls-/Referenzkopf oder eine sichtbare Abschluss-, Mess- beziehungsweise Prozesskette.
- **Nominale Stoffe oder Zustände:** `tshaiin`, `ockhoees`, `oeor`, `oschotshl`, `kchaiin`, `ka`, `shkaiin`, `cphy`, `dcheodaiin`, `otair`, `otarain`, `chekain`, `shkain`, `rtain` und `lsheedain`. In ihren Zeilen stehen sie als Inventar-, Mengen- oder Zustandskarten zwischen bereits expliziten Befehlen.
- **Grenzfälle:** `olaiiny`, `ofalsheky` und `chedol` besitzen sichtbare Prozess-/Abschlusswerte, können aber unter einem geerbten Kopf auch nominal erscheinen. Der TSV wählt jeweils den praktisch informationsreicheren Default und hält den Rivalen fest.

## Reader-Vergleich

Der Drei-Leser-Vergleich unterstützt mehrere Grenzen direkt:

- `ycthar` erscheint in IT2a als `y cthar`; dies stützt Referenzkopf plus erste Krautfraktion.
- `otarain` erscheint in IT2a und RF1b als `otar ain`; dies stützt die getrennte Stufe-II-Komponente.
- `ofalsheky` erscheint in beiden anderen Lesern als `ofal sheky`; damit ist der Blütenrohstoff-I-Ansatz vor dem bekannten Einweich-/Heiz-/Abschlussblock sichtbar.
- RF1b trennt `otodar` als `oto ar`; dies hält Fraktion I sichtbar, lässt aber `D_MEASURE` weniger sicher. Deshalb bleibt die nominale Fraktionslesung als Rivale erhalten.
- `rtain` wird in RF1b als `r tain` getrennt und stützt Wurzel plus kalte Stufe II.
- `oeor` ist in RF1b stärker zerlegt; da ZL3b und IT2a `oeor` gemeinsam halten und die Zeile eine Portionsliste ist, bleibt die kompakte Ansatzportion der Mittelstufe der Default.
- `chearory` variiert stark (`cheor ory`, `che rory`); der Default bewahrt deshalb nur die überall sichtbaren Trocken-, Mittelstufen-, Fraktions-, Portions- und Abschlusswerte und behauptet kein neues Ganzwort.

## Praktische Kernlesungen

`lsheedain` eröffnet eine klare gemessene Holzdrogenkarte: zwei Dosen vollständig eingeweichter Holzdroge, gefolgt von einer getrennten ersten eingeweichten Fraktion. `otair`, die häufigste Form, ist dagegen am besten ein nominaler Zustand: kalte zweite Drogenfraktion im Ansatz; ein zusätzlicher Kühlbefehl würde die Zeile ohne sichtbaren Kopf überladen. `qokokchy` ist das Gegenstück: Die Form steht am Zeilenende nach einer bereits heiß-mitteltrockenen Zubereitung und verlangt ausdrücklich erneutes Erhitzen, Trocknen und Abschluss.

`oschotshl` ist die unsicherste produktive Langform. Die Komposition ist formal vollständig, doch ihre natürliche Werkstattlesung bleibt schwer. Der Default behandelt sie als inventarisierbaren kalt-feuchten Holzdrogenansatz aus getrockneter Saatgutzubereitung; der Rivale hält eine ausführbare Trocken–Kühl–Feucht-Folge offen. Eine generische „Zubereitung bearbeiten“-Paraphrase wurde bewusst verworfen.

## Offene Rivalen

Die größten Restunsicherheiten sind Maß gegen Stufe bei `AIIN/AIN`, Zustand gegen geerbten Imperativ bei unpräfigierten Prozessketten und die Abschlussfunktion von terminalem `-y`. Diese Unsicherheit wird in `strongest_rival_de` ausgedrückt; sie rechtfertigt weder das Verschlucken sichtbarer Operationen noch das Ergänzen unsichtbarer Zutaten.
