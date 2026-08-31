# GDT685 — `chol/shol/tol` sind Zustandszellen, keine drei Ansatzwörter

Status: `REJECT_UNIVERSAL_ANSATZ_HEAD__PASS_540_STATE_CELL_DISPATCH__V58_EIGHT_GENERIC_HEADS_REMOVED`

GDT685 prüft die drei aus GDT684 vorhergesagten Ganzwortkarten
`Trockenansatz`, `Feuchtansatz` und `Kaltansatz` an allen 540 bereits
zugelassenen exakten Vorkommen. Die gemeinsame portable Bedeutung ist
kleiner und nützlicher:

```text
chol -> trocken
shol -> feucht
tol  -> kalt
```

Der konkrete Stoff-, Teil- oder Ansatzkopf kommt aus einer sichtbaren oder
lokal geerbten Nachbarzelle. Ohne einen solchen Kopf bleibt er offen; der
Renderer darf ihn nicht mehr durch `Gut/Material` oder `Ansatz` vortäuschen.

Der vollständige Befund steht in `REPORT.md`, die Reproduktion in `METHOD.md`
und der aktualisierte 51-Zeilen-Reader in
`artifacts/V58_51_LINE_READER.tsv`.
