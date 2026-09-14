# GDT930 — Verfahren und Reproduktion

Explorative gemeinsame nominale Lesung, kein blinder Bedeutungsversuch.
PREREGISTRATION.md legt den Umfang vor der erneuten Sichtung fest;
MODEL_DECISION.md und src/MODEL.json dokumentieren die danach entworfenen
vier festen Lesungsmodelle. Beide Schritte besitzen getrennte Hash-Locks.

`python3 experiments/yolo/gdt930_label_text_joint_reading/src/prepare.py`
exportiert nur die fünf expliziten Seitenselektoren durch query-tsv und
beschränkt HERB4 anschließend auf die festen bereits exponierten Absatzbereiche.
Das unveränderte bereits zugelassene f77r-Bild wird bei Bedarf von seiner
exakten Yale-URL geladen und vor Verwendung gegen den alten Hash geprüft.
Der eingefrorene vollständige kleine Export bleibt artifacts/SOURCE.json.

`python3 experiments/yolo/gdt930_label_text_joint_reading/src/run.py`
wendet das manuell festgelegte Achtwortmodell ohne Suche auf jede Quellgruppe
an. Ganze Rohformen entscheiden, keine bereinigten Fragmente. Prosa wird nach
den festen Arbeitsabschnitten gebunden, Labels separat. L/S/T benutzen nur
den unmittelbar vorangehenden geschriebenen Kopf, auch über eine physische
Zeilengrenze innerhalb desselben Arbeitsabschnitts; N setzt keine Relation.
Der Trenner bleibt in den Ergebnissen sichtbar. Köpfe ohne Wortwert bleiben
unübersetzt, bereits markierte Köpfe erfüllen die enge Regel nicht.

Der vollständige Label-/Textvergleich ist eine Zeichenfolgenbilanz; selbst
ein unsicher abgetrenntes o wird erhalten, aber nicht in das Achtwortmodell
aufgenommen. Das GDT388-Paket fasst gleiche Label-/Prosalocus-Paare zusammen;
PACKET_MEMBERS.json bewahrt sämtliche einzelnen Quellgruppen. Es ist ausdrücklich
unsealed/ineligible. Keine fließende Richtung oder Eigentümeridentität wird
darin als Beobachtung ausgegeben.

`python3 experiments/yolo/gdt930_label_text_joint_reading/src/validate.py`
prüft erneut durch den Guard exportierte Gruppen, vollständige Loci und
Trenner, jedes Alignment, jeden unmittelbaren Bezug, alle Labels, berichtete
Zahlen, den negativen GDT388-Einlass und bytegleiche Reproduktion. Der Validator
importiert die Builderfunktionen nicht. Beide stammen von Root und prüfen
keine wissenschaftliche Bedeutungswahrheit.

Die Entscheidung beruht auf der vollständigen Gegenbilanz in REPORT.md.
Gleiche Abdeckung ist kein Modellrang; fehlende Köpfe sind nicht automatisch
falscher Manuskriptinhalt. Keine unabhängige Bestätigung im exponierten
Entwicklungsumfang. f84/f84r, f116v und Reserven wurden nicht geöffnet.
