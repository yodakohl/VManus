# Neun Positionsregeln für die Oberflächenwahl

Der Lehrling kennt zuerst die Masterkarte. Erst danach wählt er deren sichtbare Form.
Die Regel fragt nur: Herbal oder Bio, Anfang/Mitte/Ende des Feldes und Anfang/Mitte/Ende
der physischen Linie. Sie ändert keinen Kartenwert.

1. **B_LINE_FIELD_OPEN** — Am Linien- und Feldanfang zuerst die Flusshand versuchen.
   Reihenfolge: `S_FLOW_ENTRY > HARD_D_T_ENTRY > Q_CELL_ENTRY > BARE_OR_INTERNAL > OPEN_CH_ENTRY`
2. **B_FIELD_OPEN** — Neues Bio-Feld in laufender Linie zuerst mit q eröffnen.
   Reihenfolge: `Q_CELL_ENTRY > OPEN_CH_ENTRY > HARD_D_T_ENTRY > S_FLOW_ENTRY > BARE_OR_INTERNAL`
3. **B_FIELD_CLOSE_INSIDE_LINE** — Feldende vor weiterlaufender Linie möglichst nackt schreiben.
   Reihenfolge: `BARE_OR_INTERNAL > Q_CELL_ENTRY > S_FLOW_ENTRY > HARD_D_T_ENTRY > OPEN_CH_ENTRY`
4. **B_FIELD_AND_LINE_CLOSE** — Gemeinsames Feld- und Linienende aus dem knappen Endregister wählen.
   Reihenfolge: `Q_CELL_ENTRY > S_FLOW_ENTRY > BARE_OR_INTERNAL > HARD_D_T_ENTRY > OPEN_CH_ENTRY`
5. **B_SINGLE_CELL** — Einzelzelle zuerst als q- oder nackte Kurzkarte setzen.
   Reihenfolge: `Q_CELL_ENTRY > BARE_OR_INTERNAL > HARD_D_T_ENTRY > OPEN_CH_ENTRY > S_FLOW_ENTRY`
6. **B_FIELD_INTERIOR** — Im Bio-Feldinneren die kompakte Arbeitsform bevorzugen.
   Reihenfolge: `Q_CELL_ENTRY > HARD_D_T_ENTRY > BARE_OR_INTERNAL > S_FLOW_ENTRY > OPEN_CH_ENTRY`
7. **H_FIELD_OPEN** — Herbal-Feld mit q oder nackter Form beginnen.
   Reihenfolge: `Q_CELL_ENTRY > BARE_OR_INTERNAL > OPEN_CH_ENTRY > S_FLOW_ENTRY > HARD_D_T_ENTRY`
8. **H_FIELD_INTERIOR** — Herbal-Innenkarten bevorzugt ch/che schreiben.
   Reihenfolge: `OPEN_CH_ENTRY > BARE_OR_INTERNAL > HARD_D_T_ENTRY > Q_CELL_ENTRY > S_FLOW_ENTRY`
9. **H_FIELD_CLOSE** — Herbal-Feldende bevorzugt hart oder nackt schreiben.
   Reihenfolge: `HARD_D_T_ENTRY > BARE_OR_INTERNAL > OPEN_CH_ENTRY > Q_CELL_ENTRY > S_FLOW_ENTRY`

Ergebnis: Die neun Regeln wählen bei 182/251 Ereignissen die tatsächlich gebrauchte
Gewohnheit. Mit der jeweils ersten registrierten Form treffen sie 160/251 sichtbare Tokens
vollständig. 22 weitere brauchen nur die zweite Schreibweise innerhalb derselben Gewohnheit;
69 brauchen die lokale Gewohnheitswahl des Schreibers. Alle 251 bleiben exakt rücklesbar.
