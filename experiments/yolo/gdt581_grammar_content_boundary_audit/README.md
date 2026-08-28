# GDT581 — grammar/content-boundary audit

Status: `PASS_15889_COMPLETE_SLOTS__13702_CONTENT_CARRIERS__2187_CONTROL_SLOTS__4026_INHERITED_ALIASES__5672_FOCUS_HOSTS__8_FINAL_RECIPE_RECONCILIATIONS__269_FOCUS_VOICE_REPAIRS__232_EVENT_REPAIRS__2_SAFE_EXPLICIT_REMOTE_SLOTS__744_LOCAL_CARD_HOSTS__1973_LOCAL_COMPONENTS__107_NAME_SLOTS__ZERO_UNOWNED_SLOTS__5122_EXACT_ROUNDTRIPS`

GDT581 zieht vor der ersten konkreten Inhaltsbelegung eine vollständige Grenze
zwischen tragenden Inhaltspositionen und reinen Steuerungspositionen. Über die
gegenwärtigen dreißig Seiten werden 15.889 einzeln adressierbare Slots erfasst:
13.702 dürfen in einem späteren Pass eine konkrete Arbeitsbedeutung tragen,
2.187 bleiben ausschließlich grammatische oder lokale Steuerung. Jeder Slot hat
genau einen primären Host; die 4.026 geerbten Handlungs- und Objektverweise sind
ausdrücklich Aliase und keine zusätzlichen geschriebenen Wörterbuchplätze.

Der Pass repariert außerdem eine bislang hörbare Mehrdeutigkeit der deutschen
Arbeitsstimme. 269 Fokusanschlüsse in 232 Ereignissen werden mit ihrem exakten
Besitzer- oder Handlungskopf ausgesprochen. Die neue Ausgabe bleibt jederzeit
auf den vollständigen GDT580-Wortlaut zurückführbar: 5.122 Ereignisse und 793
Aussagen rekonstruieren ihre GDT580-Quelle exakt.

Ausführen:

```bash
python3 experiments/yolo/gdt581_grammar_content_boundary_audit/src/run.py
python3 experiments/yolo/gdt581_grammar_content_boundary_audit/src/validate.py
```

Die Ergebnisse stehen in [REPORT.md](REPORT.md), das genaue Verfahren in
[METHOD.md](METHOD.md), und die lesbare Gesamtausgabe in
`artifacts/GDT581_GRAMMAR_CONTENT_BOUNDARY_THIRTY_PAGE_EDITION.md`.

„Content-ready“ bezeichnet nur die vollständige strukturelle Adressierung. Der
Pass übersetzt kein Voynich-Wort und weist keinem Slot Wasser, Öl, Salz,
Pflanzenteil, Krankheit, Heilung, Gefäß oder eine andere konkrete Bedeutung zu.
