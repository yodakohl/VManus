# GDT688 — V61 bindet jedes praktische Verb an ein geschriebenes Ordinal

Status: `PASS_V61_113_OF_113_PRACTICAL_VERBS_EXACT_ACTION_ORDINAL__LEGACY_LEAKAGE_74_TO_66_TO_4_TO_0`

V61 rendert alle 51 aktuellen Zeilen mit demselben quellgeordneten
Token-Renderer. Jedes der 113 deutschen Verbvorkommen liegt dadurch innerhalb
des Zeichenspans genau einer der 85 geschriebenen Aktionspositionen. Null
Verben bleiben ohne Quelle.

Der ausführbare Vergleich korrigiert zugleich den GDT687-Ausblick:

```text
V57  74 zusätzliche Verb×Zeile-Paare auf 29 Zeilen
V59  66 auf 28 Zeilen
V60   4 auf  2 Zeilen
V61   0 auf  0 Zeilen
```

Siehe `REPORT.md`, `METHOD.md`, den vollständigen Reader
`artifacts/V61_51_LINE_READER.tsv` und die 113 exakten Rückbindungen in
`artifacts/V61_113_VERB_OCCURRENCE_PROVENANCE.tsv`.
