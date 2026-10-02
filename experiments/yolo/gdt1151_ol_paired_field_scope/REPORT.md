# GDT1151 — alternating nonempty OL fields fail

**REFUTED_FIXED_PAIRED_FIELD_SCOPE.** Exact free `ol` cannot uniformly open and close nonempty fields under the registered complete-paragraph reset and native-group assumptions. All counterexamples are retained; no boundary/phase repair was made. This is a long-range scope test, not a meaning assignment or a new neighbour-window search.

| Native reading | All P ol | Complete ol-bearing paragraphs | Scorable | Compatible | Contradiction | Annotation barrier | Unbounded ol |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZL3b |454|249|74|15|59|175|0|
| IT2a |454|247|232|55|177|15|0|
| RF1b |467|0|0|0|0|0|467|

The primary scorable paragraphs span32/65physicalleaves. They are a strict pure-transcription subset, not a random sample: the different annotation conventions explain much of the unequal eligibility. RF has no native paragraph flags and is untestable; no boundaries were borrowed. Readings are not independent manuscripts. Annotated paragraphs remain fully retained, with their hypothetical fields diagnostic only.

## Every kind of contradiction

ZL has59scorable odd-count paragraphs and1with an empty field; that empty-field case is also odd. IT has176odd-count paragraphs and4with empty fields; one empty-field paragraph has an even count. Both types violate the same fixed model. Among scorable adjacent pairs, ZL has2 CLOSE→OPEN and1 OPEN→CLOSE; IT has5 and4. The latter direction closes an empty field and is forbidden. Zero-ol paragraphs supply no support.

All scorable empty-field paragraphs:

| Reading | Complete native paragraph | ol count | Empty OPEN→CLOSE pair |
|---|---|---:|---|
| ZL3b | f99v.32–35 |3|f99v.34 G002–G003|
| IT2a | f23r.4–5 |2|f23r.5 G008–G009|
| IT2a | f75r.1–26 |9|f75r.5 G007–G008|
| IT2a | f81r.1–15 |11|f81r.5 G005–G006|
| IT2a | f99v.32–35 |3|f99v.34 G002–G003|

The f23r case shows why even parity alone is insufficient: its only two ol stand adjacent. The f81r IT stream includes three consecutive exact free ol, yielding overlapping CLOSE→OPEN and OPEN→CLOSE pairs. That is a reading-specific native-group observation; no new visual adjudication or spacing normalization occurred. Logical observation only: a three-marker run necessarily contains an empty OPEN→CLOSE pair under either initial alternating phase. The registered decision does not depend on this additional explanation.

[PARAGRAPH_DECISIONS.tsv](artifacts/PARAGRAPH_DECISIONS.tsv) lists every one of496complete ol-bearing reader paragraphs, including the190annotation barriers. [ADJACENT_PAIRS.tsv](artifacts/ADJACENT_PAIRS.tsv) lists all adjacency directions, including unscorable diagnostics. [PARAGRAPHS.json.gz](artifacts/PARAGRAPHS.json.gz) preserves full ordered native source lines, every proposed field's content IDs, roles and unmatched openings. [OCCURRENCES.json](artifacts/OCCURRENCES.json) retains all1375exact free-ol P events, including the467unbounded RF cases. Empty/odd contradiction lists and noncontradictory cases are all reproducible; no successful subset was selected to rescue the rule.

## What this changes

Stop the specified identical-marker, alternating, nonnested, nonempty paragraph-contained field model. Do not add silent delimiters, choose paragraph-specific entry phases, normalize troublesome spaces or reinterpret only counterexample ol as nouns. A future materially different model would need its own motivation and consequences. The result does not choose a nominal, conjunction, quantifier, operation or punctuation reading. It cannot refute all paired constructions: the exact-free-marker identity, transcription segmentation, paragraph reset and nonempty alternating-field obligations are a joint contract. Physical paragraphs are not independently established semantic scope units.

Preserve the previously known right-neighbour concentration and broad profiles, together with769's tied roles,774's unexplained repeats and571's projected-marker distinction. GDT1150 remains closed; no shorter neighbour window was tried. No translated word, semantic probability or significance claim. Compatible paragraphs are compatibility only, not confirmed fields.

## Registration, exposure and validation

[METHOD.md](METHOD.md), identical PREREGISTRATION and SOURCE hashes were locked at2026-10-02T22:22:24.254988+00:00 (local date2026-10-03), before the new paragraph-scope census. Prior exact profiles and all seven774repeat lines were already exposed; those exposures motivated the hypothesis. No blind discovery or independent confirmation is claimed. Six915snapshots and1149complete block identities were pinned unchanged; all179admittedselectors retained. f84/f84r remain sealed, f116v unadmitted, reserves closed. No images, source admissions or contacts.

Reproduce with `python3 experiments/yolo/gdt1151_ol_paired_field_scope/src/run.py`, then `python3 experiments/yolo/gdt1151_ol_paired_field_scope/src/validate.py`. [VALIDATION.json](artifacts/VALIDATION.json) records independent reconstruction and full case comparison; accounting is not semantic truth. Confirmed words and independent meaning-confirmation capacity remain zero.
