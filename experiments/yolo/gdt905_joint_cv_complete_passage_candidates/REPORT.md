# GDT905 — zwei vollständige Wortlisten-Schlüssel, keine tragfähige Lesung

**CONSTRUCTIVE_CV_SEARCH_UNRESOLVED.** Zwei feste Zeichenschlüssel setzen jeweils
einen vollständigen Absatz in Einträge der unveränderten lateinischen Wortliste
um. Beide scheitern an der festgelegten Grammatik, unabhängig bestätigt.
Es entstand keine vom vollständigen Modell akzeptierte Lesung. Alle49
Absatz-/Lesungsfälle bleiben hinsichtlich des gesamten Schlüsselraums UNKNOWN;
dieser Versuch widerlegt das Schreibmodell nicht. Bestätigte Bedeutungen:0.

Die [Wort-für-Wort-Ausgaben und beobachteten Schlüssel](artifacts/LEXICAL_KEYS.md)
sind vollständig einsehbar. Die vollständigen27-Komponenten-Codebücher stehen
in [LEXICAL_KEY_EXPLANATION.json](artifacts/LEXICAL_KEY_EXPLANATION.json).
Unbeobachtete Codewerte sind ausdrücklich willkürliche Ergänzungen.

| Fundstelle | Ganze Gruppen | Mechanische Ausgabe beginnt | Vollständige Grammatik |
|---|---:|---|---|
| IT2a f103r.43–44 |16| `mihi nixo do fis rimo fixo regi fisu …` | verworfen |
| IT2a f103v.37–38 |18| `me tu sic me tu sidere feri telo …` | verworfen |

Das sind zwei unterschiedliche Schlüssel auf den beiden Seiten **desselben
physischen Blattes**, keine Übertragung eines Schlüssels auf unabhängige Blätter.
Die Ausgaben sind keine Übersetzungen. Einzelne verständliche Wörter erhalten
keinen Bedeutungsbonus. Die starke Suchauswahl und die ausschließliche
Wortlistenverträglichkeit begründen weder Latein noch diesen Schriftkanal.

## Was tatsächlich ausgeführt wurde

Anders als beim vollständigen Simon-QuelltextvergleichGDT895 war keine konkrete
historische Passage vorgegeben. Der unveränderteGDT892-Kanal und seine425561
Referenzformen sollten gemeinsam mit der festen Merkmalsgrammatik mögliche
vollständige Texte erzeugen. Die Paradigmendaten liefern erlaubte Formen und
Analysen; keine zusätzliche Bedingung verlangt, dass benachbarte Manuskriptwörter
dasselbe Lemma haben. Es wurden keine Lemma-Beziehungen rekonstruiert.

Die festgelegte Auswahl enthält41 unterschiedliche ganze Absätze auf15
physischen Blättern, mit12–24Gruppen. Daraus ergeben sich49Lesungsfälle:
41IT2a,5RF1b,3ZL3b. Der Konsens hat keinen Absatz in diesem Größenbereich.
Die Lesungen bleiben alternative Transkriptionen eines Manuskripts.

Für alle49Fälle wurden sämtliche2^20globalen Zerlegungsmasken geprüft. Insgesamt
überleben2240785Masken mit ihren jeweiligen Vokalbitmengen. Die separat geschriebene
Prüfung reproduziert diese Listen vollständig. Das ist lokale Wörterbuch-
Verträglichkeit: Unterschiedliche Wörter können dabei noch widersprüchliche
Zeichenwerte verlangen. Es ist kein gemeinsamer Schlüssel und keine Lesung.

Die anschließende Suche nach gemeinsamen Komponentenwerten bearbeitete26512
Zerlegungs-/Vokalfälle:26483 wurden abgeschlossen,29 erreichten ihr Zeitlimit.
In44Absatz-/Lesungsfällen begann diese Stufe; die letzten5 erhielten vor der
globalen Grenze keinen CSP-Lauf. Die feste Reihenfolge führte zu41IT2a- und
3RF1b-Fällen mit begonnenen Läufen;2RF1b- und alle3ZL3b-Fälle blieben in dieser
Stufe unbearbeitet. Keine gesamte Absatzsuche wurde vollständig ausgeschöpft.
Daher sind **alle49Absatzurteile UNKNOWN**, nicht49Widerlegungen.

Genau zwei in abgeschlossenen Teilfällen gefundene vollständige Belegungen
führten zum Grammatikaufruf. Beide wurden verworfen. Der nachträgliche
Erklärungslauf rekonstruiert ausschließlich diese bereits gezählten Belegungen:
alle deterministischen Suchzähler stimmen mit dem ursprünglichen Lauf überein.
Die Grammatik, Reihenfolge und Schlüsselwahl wurden dafür nicht geändert.

## Grenzen, Prüfung und Reproduktion

Die öffentliche Registrierung `bd3794ca` lag vor dem GDT905-Manuskriptzugriff.
GDT892s Kontrollstopp12+9 bleibt unverändert; ein Kontrollbestehen wird nicht
behauptet. Die jetzige Nutzung ist die ausdrücklich beauftragte explorative
Kandidatenkonstruktion. Kein gehaltenes Blatt, neues Bild oder f84/f84r wurde
geöffnet. Unberührte Daten dienten nicht zur Auswahl zwischen Schlüsseln.

Die unabhängige Prüfung kodiert alle2553366Wort/Vokal-Kombinationen selbst,
rekonstruiert sämtliche49Maskenlisten mit lokalen Wahrheitstabellen und prüft
die beiden vollständigen Wortlisten-Schlüssel durch Rückkodierung und einen
separaten Grammatikerkenner. Sie bestätigt die zwei Grammatikablehnungen.
Sie zertifiziert keine vollständige Ausschöpfung der unbekannten Schlüsselräume.
Der Root-Validator prüft zusätzlich den bewachten Quellenabzug und die Rollups.

Der Suche wurde bei06:17UTC kein weiteres Budget gegeben; die Ausgabe war
06:17:15UTC vollständig geschrieben. Die Teilfallbelege bleiben verlustfrei
komprimiert in `artifacts/CANDIDATES.json.gz`; PACKING.json bindet sowohl die
komprimierten als auch die ursprünglichen Bytes. Keine Ausgänge wurden entfernt.
`src/reproduce.py --cache-dir CACHE --work-dir WORK` führt die unveränderte
Konstruktion, Erklärung, Komprimierung und Prüfungen aus. Zeitbegrenzte Suchen
können bei Reproduktion einen anderen unvollständigen Präfix bearbeiten;
daraus entsteht keine Behauptung identischer UNKNOWN-Suchprotokolle.

Diese Runde endet ohne Auswahl eines Folgetests. Es folgt keine automatische
Vergrößerung der Suche, Wortliste oder Grammatik. Zwei überprüfbare mechanische
Schlüssel sind dokumentiert; das verlangte Ziel einer tragfähigen vollständigen
Lesung ist weiterhin nicht erreicht.
