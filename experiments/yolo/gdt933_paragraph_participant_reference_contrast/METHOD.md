# GDT933 — Reproduktion und Abgrenzung

[PREREGISTRATION](PREREGISTRATION.md) enthält das einzige maßgebliche Protokoll.
GDT930s abgegrenzte Rohgruppen/Arbeitsrahmen und GDT932s neun feste Wortwerte
und lokale Bindungen werden unverändert wiederverwendet. Kein neuer Zugriff
auf eine gemischte TSV-Datei oder ein Bild. f84/f84r bleiben geschlossen.

```sh
python experiments/yolo/gdt933_paragraph_participant_reference_contrast/src/run.py
python experiments/yolo/gdt933_paragraph_participant_reference_contrast/src/validate.py
```

Der Runner rechnet LOCAL, TYPED_BACK und NOMINAL_BACK für alle150 bestehenden
Vorgangs-/Fortsetzungspositionen. Bei V wird der Teilnehmer des früheren
Vorgangs unverändert übernommen; keine spätere Stoffnennung repariert ihn.
INTERVALS.json enthält alle Zwischen-Gruppen-IDs. REFERENCE_CASES.tsv legt
Unbekanntes, Nominalkonkurrenz, Kopulas, unmittelbare Ortszusätze und leere
Teilnehmerintervalle offen. Die komplette zugrundeliegende Quelle bleibt im
hashgebundenen GDT930-Artifact; alle24 P2/P3-Zeilen werden je Transkription
vollständig mit beiden Lesungen und den Gegenbezügen dargestellt.

Der Validator scannt die zulässigen Antezedenten und alle Zwischenintervalle
separat vom Runner, prüft die kritischen .26/.36/.42-Folgen und alle450Fälle,
Rohzeilenerhaltung und bytegleichen Replay. Root schrieb beide Programme;
keine unabhängige semantische Begutachtung. Ergebniszahlen sind Modellfolgen,
keine Trefferquoten, Wortbestätigungen oder neue score-ready Bildrelationen.
