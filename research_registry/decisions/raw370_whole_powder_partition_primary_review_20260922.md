# RAW370 Pulverpaar: unabhängige Primärkritik der eingefrorenen Fassung

2026-09-22. Gegenstand ist ausschließlich `development_v1_frozen_for_primary_review`,
Freeze 12:35:52 UTC. Keine Änderung am Angebot, kein Decoder, keine neue
Zielauswahl, keine Bilder, Quellen, Reserven oder Kontakte. Null bestätigte Wörter.

**Ergebnis:** Die vollständige CARRY-Lesung enthält keinen hier nachgewiesenen
zwingenden Mengenwiderspruch. Die idempotente Mengenrivalin widerspricht dagegen
wirklich ihrem unverändert übernommenen lokalen Teilungsvertrag. Die f21r-
Wiederaufnahme ist unter den angebotenen endlichen Typbindungen konsistent;
„zuletzt wurde Grobes gelagert“ widerlegt sie nicht. Zwei Auslegungslücken bleiben:
die vollständige Typkompatibilität von POWDER und grobem Mahlgut sowie die
Nachbedingung von GRIND auf wasserhaltiger Paste. Beide sind von einem bewiesenen
Widerspruch zu unterscheiden. ADD wird gegenüber FRESH oder TWO_EQUAL_PORTIONS
nicht ausgewählt.

## Umfang und mechanische Vollständigkeit

Gelesen wurden die vollständige [Vorlage](../proposals/raw370_two_paragraph_powder_partition_offer_20260922.md),
deren [JSON](../proposals/raw370_two_paragraph_powder_partition_offer_20260922.json)
und das darin gebundene [Quellenpaket](../proposals/raw370_whole_paragraph_source_packet_20260922.json).
Die zuvor separat geprüften P14/P05/W44/W94/W96 und GDT812/GDT1000 bleiben
Primärgrenzen, keine geerbten Wortbeweise.

- Angebot-JSON SHA256: `4654afe0414d85f431371c799df6189b73b2cd4ace6adfc7eae833a51bf837da`.
- Quellenpaket SHA256: `d35fb71297447b47c1111d6eeac85455d27fff8b8d24b228ee0058cdf4078b98`;
  stimmt mit dem Angebotsbinding überein.
- Alle 238 Positionszuordnungen stimmen in Rohform, ID, Gruppenindex und beiden
  Separatorfeldern mit diesem Paket überein. Jede Bedeutungszuordnung stimmt
  mit dem deklarierten Ganzformeintrag oder ausdrücklich angebotenen Alias überein.
- ZL: 82 Gruppen, 65 verschiedene Rohformen, 56 Singletons; die 65 Lexikoneinträge
  sind genau die vorkommenden Formen. IT: 78/61/52; RF: 78/62/53. Alle ausgewiesenen
  Formhäufigkeiten stimmen. Dies prüft das gebundene Paket, keine erneute
  Rekonstruktion des älteren Gesamtkorpus und keine palaeographische Richtigkeit.
- Alle 18 angebotenen Produktionen wurden gegen die zehn vollständigen
  Klauselfolgen gelesen. Es sind manuell festgelegte Schemata und Klauselbäume,
  kein Nachweis einer eindeutigen Rohtextgrammatik. Die sechs Kompositionsangebote
  und 15 Alternativformannahmen sind zusätzliche, offen ausgewiesene Hypothesen.

Die folgende Tabelle deckt sämtliche 82 ZL-Positionen ab. Positionsangaben sind
zeilenlokal und einsbasiert. Regelnummern C1–C14 bezeichnen hier die Reihenfolge
von `shared_construction_contract`; die übrigen IDs sind die Originalproduktionen.

| Ganze Zeile / alle Positionen | Prüfung von Besitzer, Operation und Mengenrolle |
|---|---|
| f21r.8:1–8 | I1 bindet ACQUIRE ROOT FRESH; A1 DRY/CRUSH; G1 bindet `cthodaiin oty` als Ziel POWDER Q DRY_STATE. Kein verfügbares Q wird erzeugt. Der Zielbesitzer ist die Herkunftscharge, nicht ein zweiter Vorrat. |
| f21r.9:1–9 | A2/G2: WATER ist Spülmedium, CLEAN gilt dem Pflanzenpatienten. T1/A1 hält PLANT_MATERIAL beim laufenden Träger. Das zuletzt genannte Wasser übernimmt nicht automatisch die Patientenrolle. |
| f21r.10:1–9 | A1 DRY IN_SUN, GRIND COARSELY; P1 ordnet COARSE_PART und FINE_PART zwei disjunkten Zweigen zu. Neues Trocknen nach dem Spülen ist ausdrücklich vorhanden. Keine Menge Q wird hier nochmals eingeführt. |
| f21r.11:1–9 | K1 wählt erst Fein-, dann Grobzweig. COVER und K2 STORE_SEPARATELY RESIDUE betreffen nach C8/C10 den Grobzweig. Beide Zweige bleiben im Bestand; KEEP/COVER sind keine Materialherstellung. |
| f21r.12:1–8 | R2 RETRIEVE POWDER und anschließend G2 SIEVE UNTIL POWDER FINE Q CLEAN. Das zweite POWDER ist die ausgewählte Ausgangsfraktion; keine volle Kopie des Eingangs. Der frühere Zielgegenstand ist kein zulässiger Vorrat. Typfrage unten. |
| f32v.7:1–10 | I1 ROOT; A1 CRUSH, DRY OVERNIGHT IN_SHADE, T1/A1 THOROUGHLY MIX EVENLY PREPARED_BULK. `dain` ist THOROUGHLY. Keine geschriebene oder unabhängig gemessene Anfangsmenge 3Q. |
| f32v.8:1–9 | P2/N1/N2: `otchol daiin daiin` hat einen Besitzer C, `ctho daiin` den disjunkten Besitzer P. C=2Q und P=Q beschreiben in CARRY erschöpfend B. R1 LIFT_OUT DEFINITE COARSE_FRACTION macht C aktiv, ohne P zu verbrauchen. |
| f32v.9:1–7 | P3 verbindet SORT WITH_SIEVE KEEP mit FIBRES Q und GRANULES Q. Konstruktion und C9, nicht die zwei verschiedenen Substantive allein, setzen zwei disjunkte, erschöpfende Produkte des aktiven C. |
| f32v.10:1–10 | J1: WATER und OIL sind erlaubte erstmalige Hilfsstoffzufuhren. POWDER FINE Q nimmt P wieder auf. C wurde in F/G überführt; diese sind ausdrücklich keine Pulveraliase. N3 PASTE ONE PORTION zählt eine Charge, nicht Q Gesamtmasse. |
| f32v.11:1–3 | M1 WITH_MEDIUM WATER GRIND bindet das bereits enthaltene Wasser im aktiven Produkt. Keine zweite Wasserzufuhr. Die unqualifizierte GRIND-Nachbedingung in C6 bedarf der unten abgegrenzten Auslegung. |

## Echte Konsequenzen, Annahmen und verbleibende Alternativen

**f21r.12:2: jüngster kompatibler Bestand.** C8 bezeichnet FINE_PART/FINE
ausdrücklich als Pulverzweig und COARSE_PART/COARSE/RESIDUE als Grobzweig. C11/R2
verlangt den jüngsten verfügbaren *kompatiblen* Bestand. Bei Anwendung der
angebotenen endlichen Kind-/Teilbindungen ohne zusätzliche Untertypkanten ist
P der verfügbare Pulverbestand. C ist zuletzt aktiv und erwähnt, passt aber
nicht schon deshalb zu POWDER. Unter dieser Lesart ist die Rückbindung eindeutig
und erfordert keine neue lokale Ausnahmeregel.

Die Vorlage schreibt allerdings keine vollständige Kompatibilitätsmatrix aus.
Disjunkte Bestände sind logisch nicht dasselbe wie disjunkte Materialtypen.
Falls POWDER auch grobes Mahlgut einschließen soll, kann C zusätzlich passen;
dann wählt die jüngste-passende-Regel gerade C. Ein anschließendes Sieben könnte
eine feine Teilfraktion von C liefern, während der früher aufgehobene Feinanteil
unbenutzt bleibt. Damit wäre die behauptete Herkunft aus dem *früheren* Feinast
nicht erzwungen. Diese zusätzliche Typannahme wird hier weder eingeführt noch
als Tatsache über POWDER ausgegeben. Der Befund lautet **konsistente angebotene
Typbindung, keine unabhängig gesicherte semantische Eindeutigkeit**, nicht
„der Text muss den Grobanteil meinen“.

**f21r.8:7 gegenüber .12:5–8:** G1 und G2 unterscheiden prospektives Ziel und
realen Ausgang. Die Mengenidentität Q benötigt keinen Massentransport zwischen
den beiden Absätzen. Mit einem positiven aufbewahrten Grobzweig und ohne neue
Pflanzenfeststoffzufuhr muss die f21r-Ausgangsmasse größer als Q sein. Das ist
eine bedingte Eingangsanforderung. Es gibt hier ebenso wenig einen geschriebenen
Anfangswert 3Q wie auf f32v.7. Ein möglicherweise verbleibender Rest des letzten
Siebens darf nicht zugleich als volle Eingangscharge mitgezählt werden.

**f32v.8:2–3 gegenüber .9:4–7:** Der wirkliche lokale Widerspruch betrifft
REITERATED_QUANTITY_ASSERTION. Bei unverändertem Besitzer C und unveränderten
P3/C9-Ausgängen verlangt sie C=Q und C=F+G mit F=G=Q. Q>0 macht dies unmöglich.
Auch nichtnegative Verluste helfen nicht: Q=2Q+L. Dafür sind keine Anfangszahl,
keine .10-Rückbindung und keine W94-Masseidentität erforderlich. Unverzichtbar
bleiben das gemeinsame Q, derselbe C-Eingang, zwei disjunkte Produkte, kein
weiterer Feststoffeingang und die erhaltenen Produktmengen.

Die globale 2Q→3Q-Fassung verlangt zusätzlich den erschöpfenden Anfangsbestand,
fehlende spätere Feststoffzufuhr und drei disjunkt fortbestehende Endanteile.
Sie ist daher kein unabhängiger zweiter Manuskriptbeweis. Unter ADD werden
3Q erst aus C=2Q und P=Q abgeleitet. Dass exakt drei Endanteile Q erhalten
bleiben, setzt in diesem Intervall Nullverlust voraus. Der Entwurf legt das
offen; die Bilanz bestätigt diese Verlusteigenschaft nicht empirisch.

**f32v.11 / C6 und M1:** C6 lautet unqualifiziert, CRUSH/GRIND erzeuge einen
vorbereiteten Feststoffbestand mit grobem und pulvrigem Teilmaterial. M1/C13
fordert beim letzten GRIND Wasser als bereits enthaltenes Medium der Paste.
Aus „dry matter is conserved“ folgt kein DRY_STATE und kein Entfernen des
Wassers. Ein zwingender Übergang Paste→trockenes Schüttgut ist deshalb nicht
belegt. Offen bleibt, ob C6 beim Bearbeiten der Paste nur deren Feststoffanteil
unterteilt oder zugleich die Typ-/Bestandsstruktur des ganzen Produkts ersetzt.
Die Vorlage gibt keinen vollständig getrennten Zustandsübergang für Matrix,
Wasserkomponente und Feststoffteil an. Eine feuchte Matrix mit erhaltener
Wasserkomponente ist eine konsistente Auslegung, aber hier kein nachgetragener
Standard. Diese Lücke betrifft die genaue Endzustandsbeschreibung; sie beseitigt
nicht den bereits auf .9 entstehenden lokalen Rivalenwiderspruch.

| Vollständige Fassung | Mindestannahmen und tatsächlicher Ausgang |
|---|---|
| CARRY + ADD | Gemeinsames positives Feststoff-Q; erschöpfende disjunkte Bestandsbeschreibung; feste Teilungs- und Referenzrollen; keine neue Feststoffzufuhr; verlustfreie Weiterverarbeitung. Bedingt konsistent, aber nach Kenntnis der Texte konstruiert. |
| REITERATED_QUANTITY_ASSERTION | Gleiche C/F/G-Besitzer und Teilungsregeln; nur der Doppelrun behauptet Q zweimal. Lokal unmöglich. Entfall von Disjunktheit, gemeinsame Produktbeschreibung, andere Eingänge oder zusätzliche Zufuhr wären andere Verträge. P14 ist nicht mitwiderlegt. |
| FRESH_INPUT_LISTS | Unmarkierte Einganglisten liefern frische Portionen; explizite Rückbindungen und Produktausgänge bleiben gleich. .8 lässt die alte vorbereitete Charge unbenutzt; .10 führt weiteres Pulver Q zu und lässt .8-P bestehen. Kohärent mit zusätzlichem Vorrat und anderen Restbeständen. Kein geschriebenes ALL/NOTHING-LEFT schließt das aus. |
| TWO_EQUAL_PORTIONS | Zwei grobe Einzelportionen Q+Q werden als kollektiver Grobzweig geführt. Gleiche Gesamtbilanz wie ADD. Kein späteres Wort nimmt eine ursprüngliche Einzelportion gesondert wieder auf; die Masse unterscheidet diese Fassungen nicht. |

## Forschungsentscheidung

Die Vollständigkeit macht die Hypothese prüfbar und legt einen tatsächlichen
bedingten Ausschluss fest. Sie begründet keine semantische Vorzugswahl aus
der Zahl der passenden Gleichungen. Das Angebot verwendet viele einmalige
Werte, manuell gewählte Klauselgrenzen, starke Typ-/Eigentümerbindungen und
ein idealisiertes Materialkonto. Ein weiterer positiver Simulatorlauf unter
genau diesen Annahmen würde die Wortbedeutungen nicht zusätzlich einschränken.

Vor einer festen Ausführung wären die beiden benannten Auslegungslücken als
Version oder Addendum ausdrücklich zu entscheiden; diese Kritik repariert
sie nicht. Keine neue Typmatrix, kein allgemeiner Parser und keine weitere
Zielsuche folgen automatisch. Alte Quellen-/Zahlenstopps bleiben unverändert;
alternative Transkriptionen bestätigen weder Werte noch Grammatik unabhängig.
