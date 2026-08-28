# GDT598 — integrierte Sechs-Seiten-Objektedition

Status: `PASS_313_STATEMENTS__2272_HOSTS__1443_ACTIONS__650_OBJECT_COMPLETE__793_GAPS__71_COMPLETE__229_MIXED__13_GAP_ONLY__298_PARTICIPANT_PACKET__46_AIIN_ONLY__449_CARRIERLESS__36_MULTI_EVENTS__10_STRING_HAZARDS__0_SLOT_COLLISIONS`

GDT598 setzt die 254 fertigen SH-Klauseln aus GDT596 und die 396 fertigen
T/CHD/S-Klauseln aus GDT597 in den vollständigen GDT584-Aussagestrom derselben
sechs Seiten zurück. Alle 650 Action-Slot-Zuordnungen sind eindeutig; Controls,
Frames, Hostreihenfolge und Absatzgrenzen bleiben erhalten.

Der integrierte Leser umfasst 313 Aussagen, 2.272 Hosts und 1.443
Aktionshosts. 71 Aussagen besitzen bereits für jede Aktion ein fertiges
Objekt. Der exakt sichtbare Rest sind 793 Aktionen: 298 mit geschriebenem
Teilnehmerpacket, 46 mit ausschließlich AIIN-Maßparameter und 449 ohne
geschriebenen Träger. Zusammen besitzen die ersten beiden Gruppen 410 Slots.

Der exakte Action-Slot ist als Join-Schlüssel zwingend: 36 Ereignisse enthalten
mehrere fertige Aktionen und zehn identische alte Klauselstrings führen an 240
Slots zu verschiedenen Endfassungen. Beide Abkürzungen würden Information
verlieren; der aktuelle Join verliert null Slots.

Die vollständige Ausgabe steht in
`artifacts/GDT598_SIX_PAGE_INTEGRATED_READER.md`; das occurrence-genaue nächste
Arbeitsblatt in `artifacts/gdt598_793_remaining_action_gaps.tsv`.

```bash
python3 experiments/yolo/gdt598_six_page_object_statement_integration/src/run.py
python3 experiments/yolo/gdt598_six_page_object_statement_integration/src/validate.py
```
