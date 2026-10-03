# GDT1155 — l/m-Endkanal überträgt sich nicht unverändert auf Zeichnungsgrenzen

**NO_SUPPORTED_TRANSFER.** Die feste Vorhersage wurde tatsächlich geprüft: Der an Übergängen zum darunterliegenden Text gelernte Endkanal verschlechtert die l/m-Vorhersage unmittelbar vor Zeichnungen in allen drei Lesungen. Seine Vorhersageleistung an den gehaltenen Referenzübergängen ist dagegen positiv. Es fehlt nicht die Testkapazität; die registrierte Übertragung scheitert.

## Frage und Bezug zur Herstellung

GDT800/801 zeigen eine ausgeprägte Endpositionstendenz für m; GDT802 bewahrt zusätzlich die Neigung der genauen Wortfamilie. DIC001 zeigt Ähnlichkeit gröberer Familienprofile an Zeichnungsunterbrechungen und untereinanderliegenden Textstücken. Daraus folgt noch nicht, dass dieselbe Endformregel beide Grenzen erklärt. Hier wurde genau diese zusätzliche Folgerung geprüft. Kein neuer Decoder, keine Wortglossen, kein pauschales l=m. GDT829s fehlende wortgleiche Umbruchpaare bleiben unverändert.

## Feste Prüfung

Alle155 GDT800-Basen und ihre310 vollständigen l/m-Formen wurden unverändert übernommen. Sechs freigegebene915-Caches liefern die Rohformen, Quellen-IDs und Abstandsmarkierungen. Der Endkanal benutzt nur Textstückenden, deren nächster numerisch anschließender Prosaeintrag laut Code '+' oder '*' darunter liegt. Ein bloßes LINE_END genügt nicht: IVTFF-Textstücke sind nicht immer ganze physische Zeilen. Zeichnungsgrenzen sind nur explizite ausgerichtete DRAWING_INTERRUPTION-Trennstellen innerhalb eines Eintrags.

Für jedes Prüfblatt werden alle seine Ereignisse aus dem Training ausgeschlossen. Zusätzlich bleiben sämtliche Zeichnungsereignisse aller Blätter aus dem Training. Der feste Schätzer berücksichtigt genaue Basis sowie Abschnitt, Currier-Klasse und Hand durch die registrierte geglättete Zählhierarchie. Er vergleicht für jedes beobachtete l/m zwei unveränderte Vorhersagen: Endkanal gegen gewöhnlichen Zwischenraumkanal. Keine Wahl der Glättung oder Reparatur nach dem Ergebnis.

## Ergebnisse

Positive Bits würden den Endkanal bevorzugen; die Blattmittel gewichten jedes physische Blatt gleich.

| Lesung | Zeichnungsereignisse | Blätter | m/l vor Zeichnung | Gewinn Endkanal, Bits/Ereignis | Positive Blätter | Referenz-END-Gewinn |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b |52|35|10/42|−0,337226|9/35|+1,286564|
| IT2a |66|37|13/53|−0,349604|8/37|+1,359418|
| RF1b |53|33|10/43|−0,238105|9/33|+1,383017|

Alle drei Lesungen erfüllen die Kapazitätsbedingung von mindestens20 Zeichnungsfällen auf mindestens5 Blättern mit beiden Endungen. Keine erfüllt die feste Vorhersagebedingung. Die Lesungen sind alternative Transkriptionen desselben Manuskripts, keine drei unabhängigen Bestätigungen.

Insgesamt12015 Treffer der vollständigen Formen:10874 zugelassen,1141 unter den festen Naht-/Nachfolge-/Längenregeln ausgeschlossen. Die zugelassenen Mengen sind IT4041,ZL3266,RF3567. Alle171 lesungsabhängigen Zeichnungsfälle, einschließlich der gegenläufigen Beispiele, stehen in [CANDIDATE_TABLE.md](CANDIDATE_TABLE.md). Vollständige Hosteinträge mit Originalgruppen stehen in [WHOLE_CONTEXTS.md](WHOLE_CONTEXTS.md). EVENTS,EXCLUDED_HITS,PREDICTIONS,LEAF_GAINS und DRAWING_HOSTS bewahren sämtliche Entscheidungen, Trainingszähler und Vorhersagen.

## Wichtige positive Restinformation

Das Ergebnis bedeutet **nicht**, Zeichnungsgrenzen seien gewöhnliche Zwischenräume. Deskriptiv liegt der m-Anteil vor Zeichnungen zwischen beiden Referenzen:

| Lesung | SPACE | DRAWING | END |
|---|---:|---:|---:|
| ZL3b |150/2620 =5,7%|10/52 =19,2%|349/594 =58,8%|
| IT2a |183/3243 =5,6%|13/66 =19,7%|437/732 =59,7%|
| RF1b |149/2895 =5,1%|10/53 =18,9%|359/619 =58,0%|

Diese unbereinigten Raten sind keine zusätzliche registrierte Signifikanzprüfung. Sie bewahren jedoch eine Grenze der Interpretation: Ein schwächerer oder anders bedingter Einfluss bleibt möglich. Es wird hier kein abgeschwächter Kanal nachträglich angepasst. Der feste Endkanal ist für Zeichnungsereignisse zu stark auf m ausgerichtet. DIC001s gröberer Befund wird dadurch weder widerlegt noch zur l/m-Regel erweitert.

## Entscheidung und Grenzen

Eine einheitliche, unveränderte Behandlung beider Grenzen wird nicht in ein Lesemodell übernommen. Ein künftiges Herstellungsmodell muss die Unterschiede respektieren, statt alle sichtbaren Unterbrechungen als denselben Zustand zu behandeln. Das identifiziert weder die Bedeutung einer der Endungen noch die zugrunde liegenden Wortidentitäten; l/m-Basen sind analytische Paarungen, keine bestätigten Morpheme. Inhalt und Zeichnungen könnten gemeinsam angeordnet worden sein; keine kausale Intervention und keine Reihenfolge Text-vor-Bild/Bild-vor-Text nachgewiesen.

Die Registrierung erfolgte lokal vor neuer Extraktion und Auswertung; die öffentliche Veröffentlichung folgt danach. Vorherige Projektexposition einschließlich historischer800-Zählspalten und Prüfung des915-Schemas offengelegt. Nur179 bereits freigegebene Selektoren, keine Bilder/neuen Seiten, keine Kontakte. f84/f84r geschlossen, f116v unzugelassen, Reserven geschlossen. Physische Blattausschlüsse verhindern Trainingsüberschneidung im neuen Schätzer, machen die zuvor exponierten Quellen aber nicht zu unabhängigen Bestätigungsdaten.

Ein unabhängiger Validator rekonstruierte alle12015 Treffentscheidungen, alle10874 Vorhersagen mit Trainingszählern, sämtliche171 Zeichnungsfälle und ihre vollständigen Quellen sowie alle Blattaggregate ohne Import des Runners:15/15 Prüfgruppen PASS. Die Trennstellen wurden aus den gebundenen Rohgruppenfeldern geprüft; keine neue visuelle Begutachtung. Keine Signifikanz-, Übersetzungs- oder GDT388-Evidenzbehauptung.

Umfang dieses Arbeitsschritts: etwa15Minuten von Auswahl/Schemaprüfung bis Veröffentlichungsprüfung, innerhalb des45Minuten-Budgets. Der angeforderte Zehnstundenblock läuft weiter; dieser Einzelabschluss ist kein Abschluss des Gesamtauftrags.
