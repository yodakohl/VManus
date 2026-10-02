# GDT1143 — vollständiger Lesungsversuch, keine vollständige Lesung

**PARTIAL_LEXICAL_ACCOUNT_NO_COMPLETE_READING.** Der registrierte Versuch wurde ausgeführt: ein eingefrorener Kern, ein manueller Entwurf für den gesamten f25v-Absatz und eine vollständige Zuordnungstabelle aller drei Transkriptionen liegen vor. Die flüssige englische Fassung ist das beabsichtigte Modell; sie folgt noch nicht aus den angegebenen Wortwerten und Satzregeln. Kein Voynichwort ist damit übersetzt.

## Konkreter Kandidat und tatsächliches Ergebnis

Der Kandidat übernimmt versuchsweise die Grundfassung von Pseudo-Apuleius CXIII: Pflanze unter einem Kissen bei Fieber; Anwendung bei störenden Augenhaaren; Standort; Hilfe für einen durch Sommerhitze geschwächten Hasen; daraus eine Namensbegründung. Die alternative Fressvariante wurde nicht eingemischt. Die historische Quelle wurde weder als Vorlage von f25v noch als Beweis einer Tier- oder Pflanzenart ausgewählt.

Vor dem ganzen Entwurf wurden18Wortwerte und4Regeln eingefroren. Danach kamen25ausdrücklich gezählte Ganzwortwerte hinzu, ohne den Kern zu ändern. `daiin` bezeichnet darin versuchsweise immer dieselbe Pflanze; die Doppelung wird als Thema plus Wiederaufnahme behandelt. Das ist eine bezahlte Hypothese, keine aus den Häufigkeiten gewonnene Bedeutung.

| Lesung | Erhaltene Rohgruppen | Mit geratenem Kernwert | Mit geratenem Zusatzwert | Explizit unbekannt |
|---|---:|---:|---:|---:|
| IT2a |57|30|26|1|
| ZL3b |60|29|22|9|
| RF1b |59|27|20|12|
| Gesamt |176|86|68|22|

154zugeordnete Vorkommen und43verschiedene Ganzwortannahmen bedeuten **keine**154gelesenen Wörter. Die gemeinsamen Formen tragen konsistente Lexikoneinträge, aber keine abgeleitete vollständige Argumentstruktur. Alle11IT/ZL-Vorkommen von `daiin` einschließlich der Doppelung bleiben erhalten; RFs9exakte Vorkommen und seine abweichenden Grenzen bleiben anders.

Die [vollständige Tabelle](artifacts/LITERAL_GLOSS_LINES.tsv) stellt jede Zeile aller drei Lesungen ihren ungeschönten C0-Werten gegenüber. [AUTHOR_READING.md](AUTHOR_READING.md) enthält die beabsichtigte zusammenhängende Lesung samt den vom Autor selbst festgehaltenen Lücken. [ROOT_ASSESSMENT.md](ROOT_ASSESSMENT.md) bewertet alle sieben Hauptzeilen, nicht nur günstige Einzelstellen.

## Nicht eingelöste Vorhersagen

- Der Pflanzenbezug bleibt gleich benannt; die Regeln bestimmen aber nicht vollständig, wem Haar und Auge gehören und welche Rolle die Pflanze in der zweiten Anwendung hat.
- Die Standortbeschreibung benötigt ungeschriebene Anbindungen. Insbesondere darf das eingefrorene `chol` mit dem Wert „bindet/hält“ nicht nachträglich zu „wächst“ werden, damit die freie Paraphrase passt.
- Tierzustand und Pflanzenwirkung werden in der beabsichtigten Geschichte als Namensgrund verwendet. Der Textentwurf liefert dafür keine vollständig hergeleitete Verbindung und keinen bestimmten Satzbau, der diesen Grund tatsächlich übernimmt.
- Die abschließende Blatt-/Pflanzenphrase und die Abweichungen der alternativen Leser bleiben offen.

Damit ist die zentrale Anforderung einer vollständigen Konstruktion nicht erfüllt. Das ist weder eine Widerlegung jedes gemischten Kräutereintrags noch ein Test gegen jede Rückverweislesung von `daiin`. Die Häufigkeitsprofile allein beweisen ebenfalls keinen semantischen Widerspruch; die entsprechende stärkere Formulierung im Autorenentwurf wird nicht als Befund übernommen.

## Protokoll und Grenzen

[PROTOCOL_NOTE.md](PROTOCOL_NOTE.md) dokumentiert eine vom unabhängigen Prüfer bemerkte Mehrdeutigkeit des registrierten Verbots benannter Tiere/Pflanzen. Wörtlich kollidiert es mit den provisorischen Hasenwerten; die ausdrücklich erlaubte C0-Exploration und die Vollquellenpflicht legen dagegen die engere Grenze gegen eine behauptete Bildidentifikation nahe. Der ursprüngliche Vertrag und alle Autorenartefakte bleiben unverändert. Auch unter der erlaubenden Auslegung scheitert die vollständige Konstruktion an den obigen Lücken; die nachträgliche Klarstellung verschafft ihr keinen Erfolg.

Die Absatzgrenzen sind in IT2a/ZL3b gesetzt; RF1b lässt die entsprechenden Flags im besessenen Paket ungesetzt. Daraus folgt weder eine fehlende RF-Absatzstruktur noch ihre Bestätigung. Der verlangte absatzinterne Begründungsgraph bleibt dort hinsichtlich dieser Metadaten unbewertet.

Alles beruht auf zuvor exponierten Daten. Keine neuen Bilder, Quellenabrufe, Manuskriptseiten oder Reserven wurden geöffnet; f84/f84r bleiben versiegelt. Drei Transkriptionen und mehrere Modellprüfer sind keine unabhängigen Handschriften oder Bedeutungsbestätigungen. Keine Signifikanzbehauptung, kein ausgewählter Pflanzenname, keine geänderte Entscheidung von1092/1093/1094/1095/1142.

## Entscheidung und Reproduktion

Diesen Kandidaten nicht durch weitere freie Wortwerte oder einen neuen historischen Pflanzennamen verlängern. Eine Wiederaufnahme benötigt eine explizite neue Argument-/Anbindungskonstruktion, die die benannten Lücken auf dem ganzen vorhandenen Absatz tatsächlich bearbeitet; bestätigte Anfangsglossen werden dafür nicht verlangt. Der vollständige Versuch bleibt als C0-Entwurf erhalten.

`python3 experiments/yolo/gdt1143_mixed_herbal_entry_whole_reading/src/run.py` reproduziert die Worttabelle und die Buchführungszahlen aus den eingefrorenen Dateien. Es ist kein Decoder und erzeugt keine Sätze. Der unabhängige Prüfbericht wird unter `artifacts/VALIDATION.md` geführt; technische Konsistenz und fehlende Bedeutungsableitung bleiben getrennt.

Die unabhängige Prüfung und der anschließende Root-Lauf bestehen 15/15 Protokoll-/Buchführungsprüfungen. Sie bestätigen die vollständige Erfassung und unveränderte Werte, keine Satzableitung oder Bedeutung.
