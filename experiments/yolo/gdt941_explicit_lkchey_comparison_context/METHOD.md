# GDT941 — ganze Absatzkontexte und expliziter Zahlenrahmen

DECISION.md begründet Auswahl und Budget. PREREGISTRATION.md und src/MODEL.json
fixieren die vier neuen Hypothesen und ihre eng begrenzten Konsequenzen.

src/run.py rendert den bestehenden33-Wort-Kontext, erfasst jeden exakten lkchey,
bindet alle unmittelbaren Operanden samt Rohgrenzen, vergleicht vier Modelle
und hält die ganzen vorhandenen Absätze sowie alle Leserabweichungen fest.
Keine Suche, keine gelernte Grammatik und keine Änderung älterer Quellen.

src/validate.py prüft getrennt Quell-/Protokollhashes, vollständige Marker-/
Variantenerfassung, ganze Absatzabdeckung, jede Operandenentscheidung und
berechnete Konsequenz. Reproduzierbarkeit ist keine Bedeutungsvalidierung.
