# GDT906 — vollständige Suche: keine tragfähige Lesung im festen Modell

**COMPLETE_NO_GRAMMAR_KEY.** Alle 439.399 festgelegten Fälle sind vollständig
berechnet und unabhängig geprüft. Kein Schlüssel überführt einen vollständigen
Absatz zugleich in Wörter der festen Referenz und in eine von der festgelegten
Grammatik akzeptierte Folge. Es gibt keine offene Restmenge mehr.
Eine Entschlüsselung oder bestätigte Bedeutung wurde nicht gefunden.

Es bleiben **zwei unterschiedliche Wortlisten-Schlüssel für zwei Absätze** auf
f103r und f103v, bereits aus GDT905 bekannt. Ein dritter Fall ist der identische
f103r-Text mit demselben Schlüssel unter ZL3b statt IT2a. Das ist kein weiterer
Schlüssel und keine unabhängige Bestätigung durch ein anderes Manuskript.
Die [vollständigen mechanischen Ausgaben und Schlüssel](artifacts/LEXICAL_KEYS.md)
bleiben zusammen mit sämtlichen anderen Fällen erhalten.

| Absatz/Lesung | Ganze Gruppen | Lexikalische Schlüssel | Feste Grammatik erfüllt |
|---|---:|---:|---:|
| IT2a f103r.43–44 |16|1|0|
| IT2a f103v.37–38 |18|1|0|
| ZL3b f103r, identischer Wortlaut zu IT2a |16|1, identisch zu IT2a|0|

Die Suchauswahl umfasst unverändert 49 ganze Absatz-/Lesungsfälle: 41
unterschiedliche Absätze auf 15 physischen Blättern, jeweils 12–24 Rohgruppen.
Die unabhängig bestätigte Aufteilung deckt 2.240.785 Zerlegungsmasken in 98.083
exakten Segmentierungsgruppen und 439.399 Vokalfällen lückenlos ab. 26.483
abgeschlossene Vorgängerfälle wurden unter identischen Bindungen übernommen;
412.916 Fälle wurden vollständig neu ausgezählt. Die neue Hauptauszählung lief
776,577 Sekunden nach dem Laden von Referenz und Fallplan, ohne Zeit- oder
Trefferlimit. Diese Laufzeit misst nicht den gesamten Forschungsaufwand.

Die zweite Implementierung rekonstruiert die Worttabellen unabhängig. Sie
verwendet eigene Konsistenzprüfungen und vollständige Z3-Auszählung; eine spätere
Version ergänzt eine unabhängige Flussprüfung der notwendigen Injektivität.
180.257 gültige Nachweise der exakt erhaltenen früheren Version und 259.142 der
späteren Version bilden zusammen den vollständigen Nachweis. Beide Quellen
sind durch ihre Hashes gebunden. Keine bereits geprüften Fälle wurden gelöscht,
keine Bedingungen gelockert und keine Modelle bei einem Treffer übersprungen.
Die Flussprüfung ist eine technische Beschleunigung, kein Manuskriptbefund.

Für jeden Fall wurden die **vollständige Menge beobachteter Schlüssel und alle
Grammatikentscheidungen** verglichen. Alle stimmen überein. Die drei Fälle mit
lexikalischen Schlüsseln wurden unabhängig bis zur Erschöpfung ausgezählt:
jeweils genau eine Zuordnung, kanonische Rückkodierung und verworfene vollständige
Grammatik. Der abschließende Prüfer kontrolliert zusätzlich jeden gepackten
Einzelnachweis gegen die genauen Hauptlaufdaten, beide Quellversionen und den
vollständigen Fallplan. [Prüfergebnis](artifacts/VALIDATION.json).

[Die Methode](METHOD.md) und [die gebundenen Quellen](artifacts/BINDINGS.json)
halten Wortliste, Grammatik, Code und Textauswahl fest. Die vollständigen
[Hauptnachweise](artifacts/CASES.json.gz) und
[unabhängigen Nachweise](artifacts/INDEPENDENT_CASES.jsonl.gz) sind beigefügt.
Die Suchhistorie GDT905 bleibt unverändert. Während der Hauptrechnung liefen
28 Haupt- und vier Prüfprozesse; danach bis zu 32 Prüfprozesse. Es gab keinen
Zeitabbruch und keine Begrenzung der Zahl gefundener Schlüssel.

Das Nullergebnis schließt genau diesen unveränderten GDT905-Suchraum auf diesen
49 wörtlichen Absatzlesungen. Es widerlegt weder Latein noch CV-Schreibweisen
allgemein oder andere Textauswahlen und Modelle. GDT892 hat seinen Kontrolltest
wegen fehlender Kapazität nicht ausgeführt. Keine zusätzlichen, versiegelten
oder zurückgehaltenen Manuskripttexte wurden hinzugefügt. Weitere Laufzeit
allein kann im vollständig ausgeschöpften festen Suchraum nichts mehr finden.
