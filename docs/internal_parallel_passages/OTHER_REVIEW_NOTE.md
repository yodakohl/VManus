# Separater statischer Decoderhinweis, kein ausgewählter Nachfolgefit

5. September 2026. Bei der Suche nach einem stärkeren Ansatz fand ein Reviewer
eine begrenzte Schwäche eines alten Wortscorers; Root prüfte die betreffenden
Codepassagen selbst nach.

In GDT610 src/consensus_carrier_decoder.py setzt log_score_word() ab Zeile99
den Zeichenkontext für jedes Wort neu auf Leerzeichen. chunk_score() ab Zeile555
summiert diese Einzelwortwerte und verwendet außerdem Wortlängen und Anzahlen.
Seine Bewertung kann deshalb keine Reihenfolgeabhängigkeit zwischen denselben
ausgegebenen Wörtern innerhalb dieses Chunks unterscheiden. Das ist eine
statische Eigenschaft dieser konkreten Funktion, kein neuer Voynich-Test.
Der [ursprüngliche GDT610-Bericht](../../experiments/yolo/gdt610_consensus_carrier_control_audit/REPORT.md)
mit dem Ergebnis CONSENSUS_STABILITY_INCREASES__WHOLE_WORD_KEY_STABLE_BUT_WRONG
bleibt unverändert; dieser spätere Hinweis ergänzt ihn.

Ein durchgehender Klartextscore könnte diese verworfene Information nutzen.
Die Schlussfolgerung darf nicht auf sämtliche alten Decoder übertragen werden:
GDT001 enthält bereits umfangreiche andere Kontextmodelle. Ebenso bleibt eine
historisch begründete Kodierungsklasse offen. Ein stärkeres Sprachmodell allein
wird hier nicht als neue Lösung vorgeschlagen, kein alter Schlüsselangriff
wird wiederholt und keine Laufzeitauswirkung wird aus der Codelektüre behauptet.

Der unabhängige Reviewer nannte zusätzlich GDT612-Chunkgrenzen und Details des
GDT610-Kontrollgenerators. Root hat diese weitergehenden Implementationspfade
nicht vollständig nachverfolgt; sie sind hier kein neu bestätigter Befund.

Die anschließende [gemeinsame Decoderprüfung](../joint_reading/PROPOSAL.md)
dokumentiert Root's spätere direkte Prüfung der GDT612-Pfade und der früheren
Kontextmodelle. Auch diese Erweiterung enthält keinen neuen Fit.
