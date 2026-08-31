# GDT687 — V60 trennt Aktion, Resultat, Bezug und Grenze

Status: `PASS_95_POSITION_SCOPE_DISPATCH__V60_24_ACTION_64_RESULT_3_REFERENCE_4_BOUNDARY`

Der vollständige aktuelle Umfang umfasst 95 Positionen auf 40 der 51
Readerzeilen: vierzehn `dchey`, vier nackte `y`, drei freie `dy` und 74
gebundene `*dy*`. V60 gibt jeder Position eine praktische Standardrolle:

```text
24  lizenzierte Aktionen
64  fertige Resultate/Zustände
 3  lokale Rechtsbezüge
 4  reine Feld-/Satzgrenzen
```

`dy` erzeugt kein eigenes Verb. Bei einer gebundenen Form entscheidet die
ganze Karte, ob ein Aktionsverb vorhanden ist; `dy` liefert höchstens den
Endpunkt. Freies `dy` wird nur als `;` oder `.` ausgegeben. Das bisherige
`qody = fertigstellen` fällt deshalb auf `fertige Zubereitung` zurück.

Siehe `REPORT.md`, `METHOD.md` und den vollständigen Reader
`artifacts/V60_51_LINE_READER.tsv`.
