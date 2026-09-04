# GDT807 — target-maskierte Absatzökologie

Status: `COMPLETE__0_ROBUST__3_PROVISIONAL__0_NO_SPLIT__ZERO_SEMANTIC_PROMOTION`

## Ergebnis

Der offizielle Lauf rekonstruiert exakt 665 vollständig durch Start-/Endflags
begrenzte Absätze aus 4.137 guarded gelesenen Zeilen. Vor jedem Modell werden
alle vollständigen Zeilen entfernt, die eines der sieben registrierten Zielwörter
enthalten. Eligibility und Längenbin entstehen danach, aber noch vor der
Ganzwort- beziehungsweise ED1-Featurequarantäne.

| Paar | raw AUC | stable AUC | stable BA | stable ED1 AUC | cyclic Rang | K24 Rang | Removal | Entscheidung |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `cheol` / `otal` | 0.733614330875 | 0.702507232401 | 0.616923818708 | 0.662729026037 | 1/13 | 17 | 1 | `PROVISIONAL_PARAGRAPH_ECOLOGY_SPLIT` |
| `qokol` / `qotal` | 0.731656184486 | 0.706705539359 | 0.636734693878 | 0.585422740525 | 6/13 | 11 | 1 | `PROVISIONAL_PARAGRAPH_ECOLOGY_SPLIT` |
| `qokeol` / `qokol` | 0.667108753316 | 0.694041867955 | 0.631239935588 | 0.693236714976 | 2/13 | 12 | 1 | `PROVISIONAL_PARAGRAPH_ECOLOGY_SPLIT` |

Fehlende Robust-Gates:

- `G807-P01`: K24 specificity.
- `G807-P02`: stable ED1 AUC, cyclic null, K24 specificity.
- `G807-P03`: stable capacity, K24 specificity.

Kein Ergebnis ist eine Übersetzung. Ein positiver Ausgang benennt höchstens
eine reproduzierbare Verteilung verschiedener exakter Ganzwörter in den übrigen
Absatzzeilen. Deutsche Rivalen, Bilddeutungen und historische Rollen hatten null
Auswahlgewicht.

## Kontroll- und Leakage-Audit

Die zyklische Null rotiert vollständige Membership-Sets einschließlich leerer Sets
in den vorregistrierten section×language×hand×length-Strata. Die 24 K24-IDs pro
Zielpaar sind eine deterministische Spezifitätskalibrierung, keine 24 unabhängigen
Kontrollen und ausdrücklich kein p-Wert. Jedes Pseudopaar entfernt zusätzlich alle
Zeilen mit seinen beiden Kontrollwörtern, damit das Modell sein Label nicht sieht.

- `G807-P01`: 24 feste IDs, 22 verschiedene Oberflächenpaare.
- `G807-P02`: 24 feste IDs, 24 verschiedene Oberflächenpaare.
- `G807-P03`: 24 feste IDs, 24 verschiedene Oberflächenpaare.

## Strukturelle Landmarks

- `G807-P01`: 166/551 Full-fit-Vokabularzeilen passieren den breiten Stabilitätsgate; stärkste Beispiele: `sho` (+2.728), `qokeeo` (+2.391), `qokor` (+2.391), `chckhey` (+2.248), `qokeody` (+2.248), `cho` (+1.952), `ckhy` (-1.926), `choty` (-1.783).
- `G807-P02`: 113/377 Full-fit-Vokabularzeilen passieren den breiten Stabilitätsgate; stärkste Beispiele: `qokchy` (+3.244), `cthy` (+2.781), `shy` (+2.346), `cthol` (+1.894), `chor` (+1.794), `chy` (+1.682), `okol` (+1.682), `al` (-1.578).
- `G807-P03`: 101/353 Full-fit-Vokabularzeilen passieren den breiten Stabilitätsgate; stärkste Beispiele: `qokedy` (-3.252), `chdy` (-2.463), `shody` (-2.380), `otar` (-2.077), `qol` (-2.077), `sheedy` (-2.077), `ckhy` (+2.055), `okeedy` (-1.952).

Insbesondere ist 101/353 für `G807-P03` breit und nicht selektiv. Formen wie
`qokedy` und `qokeody` können bloße Familien-Echos jenseits der ED1-Maske sein;
kein Landmark erhält deshalb einen Gloss oder semantischen Kredit.

## Claim ceiling

Entscheidungen: 0 robust, 3 provisional, 0 ohne Split. Der feste Landmark-Gate markiert 380 Paar×Oberflächen-Zeilen.

`PARAGRAPH_ECOLOGY_LANDMARK` ist ausschließlich ein strukturelles Label. GDT807
bestätigt kein Wort, Morphem, Rezept, Material, Verfahren, Medium, Leiden, Maß,
Latein oder Deutsch. Das GDT388-Paket bleibt wegen bereits erfolgtem Formalzugriff
absichtlich fail-closed und ist nicht score-ready.

## Reproduktion

```bash
python3 experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/src/run.py
python3 experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/artifacts/GDT807_GDT388_PARAGRAPH_EDGE_PACKET.tsv
```
